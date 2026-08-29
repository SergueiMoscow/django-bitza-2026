import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import psycopg2
from django.core.management.base import BaseCommand
from django.utils import timezone

from electricity.models import MeterReading
from rent.models import Contract, Room

MOSCOW = ZoneInfo('Europe/Moscow')

# Комнаты, где название в bitza_ha отличается от нашего shortname.
# "Сруб" — один счётчик на всё здание "Рубленый дом", привязан к Д.00.
ROOM_NAME_OVERRIDES = {
    'Д.00': 'Сруб',
}

# Насколько далеко от целевой даты (день оплаты / еженедельная точка) можно искать
# ближайшую реальную запись в bitza_ha. Точность тут не критична.
SEARCH_WINDOW_DAYS = 10

# Каданс для периодов, когда у комнаты нет договора (например, комната переоборудована
# под котельную и никогда не будет сдаваться, но счётчик есть и его нужно отслеживать).
WEEKLY_GAP_DAYS = 7


def add_month(d: date) -> date:
    return (d.replace(day=28) + timedelta(days=4)).replace(day=1)


def last_day_of_month(d: date) -> date:
    return add_month(d) - timedelta(days=1)


class Command(BaseCommand):
    help = (
        'Импортирует/синхронизирует показания автоматических (Zigbee) счётчиков из внешней БД '
        'bitza_ha в MeterReading. Для комнат с активным договором — раз в месяц на день оплаты, '
        'для периодов без договора — раз в неделю. Идемпотентно, можно гонять по крону.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Только показать, что будет сделано, без записи в БД.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        ha_conn = psycopg2.connect(
            host=os.environ['HA_DB_HOST'],
            port=os.environ.get('HA_DB_PORT', '15432'),
            dbname=os.environ['HA_DB_NAME'],
            user=os.environ['HA_DB_USER'],
            password=os.environ['HA_DB_PASSWORD'],
        )
        try:
            with ha_conn.cursor() as cur:
                cur.execute('SELECT MIN(recorded_at) FROM meter_readings')
                row = cur.fetchone()
                if not row or row[0] is None:
                    self.stdout.write('В bitza_ha нет данных.')
                    return
                data_start = timezone.localtime(row[0], MOSCOW).date()
                today = timezone.localdate()

                total_written = 0
                total_skipped = 0
                for room in Room.objects.filter(type_watt_counter='A').order_by('shortname'):
                    ha_room_name = ROOM_NAME_OVERRIDES.get(room.shortname, room.shortname)
                    targets = self._build_target_dates(room, data_start, today)
                    written, skipped = self._import_room(cur, room, ha_room_name, targets, dry_run)
                    total_written += written
                    total_skipped += skipped
                    self.stdout.write(
                        f'{room.shortname} (bitza_ha: "{ha_room_name}"): '
                        f'{len(targets)} целевых дат, записано {written}, пропущено (нет данных рядом) {skipped}'
                    )
        finally:
            ha_conn.close()

        suffix = ' (dry-run, ничего не записано)' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'Готово{suffix}. Всего записано/обновлено: {total_written}, пропущено: {total_skipped}'
        ))

    def _build_target_dates(self, room: Room, data_start: date, today: date) -> list[date]:
        """
        Даты-кандидаты для снятия показаний:
        - раз в месяц на pay_day — пока по комнате есть договор (любого статуса, за период его действия)
        - раз в неделю — для промежутков внутри [data_start, today], не покрытых ни одним договором
        """
        contracts = list(Contract.objects.filter(room=room).order_by('date_begin'))

        covered_days: set[date] = set()
        monthly_targets: set[date] = set()

        for c in contracts:
            start = max(c.date_begin, data_start)
            end = today if c.status == 'A' else (c.close_date or c.date_end or today)
            end = min(end, today)
            if start > end:
                continue

            d = start
            while d <= end:
                covered_days.add(d)
                d += timedelta(days=1)

            month_cursor = start.replace(day=1)
            while month_cursor <= end:
                day = min(c.pay_day, last_day_of_month(month_cursor).day)
                target = month_cursor.replace(day=day)
                if start <= target <= end:
                    monthly_targets.add(target)
                month_cursor = add_month(month_cursor)

        weekly_targets: set[date] = set()
        gap_start = None
        d = data_start
        while d <= today:
            if d not in covered_days:
                if gap_start is None:
                    gap_start = d
                if (d - gap_start).days % WEEKLY_GAP_DAYS == 0:
                    weekly_targets.add(d)
            else:
                gap_start = None
            d += timedelta(days=1)

        return sorted(monthly_targets | weekly_targets)

    def _import_room(self, cur, room: Room, ha_room_name: str, targets: list[date], dry_run: bool):
        written = 0
        skipped = 0
        for target_date in targets:
            target_ts = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0, tzinfo=MOSCOW)
            window_start = target_ts - timedelta(days=SEARCH_WINDOW_DAYS)
            window_end = target_ts + timedelta(days=SEARCH_WINDOW_DAYS)
            cur.execute(
                """
                SELECT recorded_at, energy_kwh
                FROM meter_readings
                WHERE room = %s AND recorded_at BETWEEN %s AND %s
                ORDER BY ABS(EXTRACT(EPOCH FROM (recorded_at - %s)))
                LIMIT 1
                """,
                (ha_room_name, window_start, window_end, target_ts),
            )
            row = cur.fetchone()
            if row is None:
                skipped += 1
                continue
            recorded_at, energy_kwh = row
            # Пишем ДАТУ РЕАЛЬНОГО снятия показаний, а не расчётную целевую дату —
            # так показания не врут о том, когда они сняты на самом деле.
            actual_date = timezone.localtime(recorded_at, MOSCOW).date()
            if not dry_run:
                MeterReading.objects.update_or_create(
                    room=room,
                    date=actual_date,
                    # user default=0 на модели — реального пользователя с id=0 не существует,
                    # без явного None это упадёт на FK constraint.
                    defaults={'kwt_count': energy_kwh, 'user': None},
                )
            written += 1
        return written, skipped
