from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth.models import User

from bitza.settings import NORM_MONTH_KWT
from rent.models import Room
from .models import MeterReading
from .repository import (
    get_rooms_with_watt_counter,
    get_rooms_for_input_readings,
    get_last_readings_by_room,
    get_last_reading_for_room,
    get_last_readings_by_room_and_date,
    get_next_readings_by_room_and_date
)


def get_list_for_input_readings():
    """
    Получить список для ввода данных счётчика
    Комната для ввода показаний - первая без показаний на сегодня.
    Есть ли показания - has_readings
    """
    rooms = get_rooms_for_input_readings(date.today())
    return rooms


def get_readings_context(room: str | None = None) -> dict:
    """
    Подготавливает данные для обновления элементов (комнаты по цветам, текущие показания)
    """
    rooms = get_rooms_for_input_readings()
    rooms = [{'room': room.name, 'kwt_today': room.kwt_count} for room in rooms]
    if room:
        last_readings = get_last_readings_by_room(room)
        return {'room': room, 'date': datetime.today().strftime('%d.%m.%Y'), 'readings': last_readings, 'rooms': rooms}
    else:
        # Если всё заполнено, то возвращаем только rooms
        return {'rooms': rooms}


def save_readings(room: str, kwt_count: Decimal, user: User):
    # Проверить, чтобы последние показания были меньше, чем вносимые
    last_readings = get_last_readings_by_room(room=room, last_records=1)
    if len(last_readings) > 0:
        if last_readings[0]['kwt_count'] > float(kwt_count):
            raise ValueError('Показания не могут быть меньше, чем предыдущие')
    # Если запись есть - заменить
    last_reading = get_last_reading_for_room(room)
    if last_reading and last_reading.date == datetime.today().date():
        reading = last_reading
        reading.kwt_count = kwt_count
        reading.user = user
    else:
        reading = MeterReading(room_id=room, date=date.today(), kwt_count=kwt_count, user=user)
    reading.save()


def calculate_readings_by_room_and_date(room_id: str, date: date) -> float | None:
    readings_before = get_last_readings_by_room_and_date(room_id, date)
    if readings_before is None:
        # No data
        return None
    if readings_before.date == date:
        # Есть показания за запрашиваемый день
        return readings_before.kwt_count
    readings_after = get_next_readings_by_room_and_date(room_id=room_id, date=date)
    if readings_after is None:
        # Если после даты показаний нет - возвращаем последние
        return readings_before.kwt_count
    # Если есть до и после - вычисляем среднее на дату
    count_days_between_readings = readings_after.date - readings_before.date
    daily_average_consumption = (readings_after.kwt_count - readings_before.kwt_count) / count_days_between_readings.days
    result = readings_before.kwt_count + (daily_average_consumption * (date - readings_before.date).days)
    return result


def get_room_consumption(room_id, date_begin: date, date_end: date) -> float:
    start_readings = calculate_readings_by_room_and_date(room_id, date_begin)
    end_readings = calculate_readings_by_room_and_date(room_id, date_end)
    if start_readings is None or end_readings is None:
        return 0
    return end_readings - start_readings


def get_all_rooms_consumption(date_begin: date, date_end: date):
    rooms_with_watt_counters = get_rooms_with_watt_counter()
    norm_kwt = float(NORM_MONTH_KWT) / 30 * (date_end - date_begin).days
    result = []
    for room in rooms_with_watt_counters:
        room_consumption = get_room_consumption(room.shortname, date_begin, date_end)
        color = '#9BF5D099' if room_consumption <= norm_kwt else '#F59BD099'
        result.append({'room': room.shortname, 'consumption': room_consumption, 'color': color})
    sorted_result = sorted(result, key=lambda x: x['consumption'], reverse=True)
    return sorted_result
