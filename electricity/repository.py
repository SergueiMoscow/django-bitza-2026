from typing import List
from datetime import date as dt_date, date, timedelta

from django.db.models import Q, Exists, OuterRef

from electricity.models import MeterReading
from rent.models import Room


def get_rooms_with_watt_counter() -> List[Room]:
    rooms_with_watt_counter = Room.objects.filter(has_watt_counter=True)
    return rooms_with_watt_counter


def get_rooms_for_input_readings(current_date=None) -> List[Room]:
    """
    Возвращает список комнат с сегодняшними и предыдущими показаниями счётчика
    """
    if current_date is None:
        current_date = dt_date.today()
    rooms_with_counters = Room.objects.filter(has_watt_counter=True)
    for room in rooms_with_counters:
        latest_reading = room.readings.filter(date__lt=current_date).order_by('-date').first()
        reading_today = room.readings.filter(date=current_date).first()
        room.kwt_count_before = latest_reading.kwt_count if latest_reading else None
        room.kwt_count = reading_today.kwt_count if reading_today else None
    return rooms_with_counters


def get_last_readings_by_room(room: str, last_records: int = 3) -> List[dict]:
    readings = MeterReading.objects.filter(room__shortname=room).order_by('-date')[:last_records]
    if len(readings):
        readings = readings[:last_records][::-1]
        readings = [
            {
                'date': entry.date.strftime('%d.%m.%Y'),
                'kwt_count': entry.kwt_count
            }
            for entry in readings
        ]
    else:
        readings = []
    return readings


def get_first_room_for_input() -> str:
    # Проверяем наличие показаний для данной комнаты с сегодняшней датой
    has_today_reading = MeterReading.objects.filter(room=OuterRef('pk'), date=date.today())
    # Получаем первую комнату, у которой есть счетчик и нет записей на сегодня
    room = Room.objects.filter(
        Q(has_watt_counter=True) &
        ~Exists(has_today_reading)
    ).first()
    return room.shortname if room else None


def get_last_reading_for_room(room: str) -> MeterReading:
    last_reading = MeterReading.objects.filter(room_id=room).order_by('-date').first()
    return last_reading


def get_last_readings_by_room_and_date(room_id: str, date: date) -> MeterReading | None:
    """
    Находит последние показания по комнате на определённую дату
    """
    last_readings = MeterReading.objects.filter(room_id=room_id, date__lte=date).order_by('-date').first()
    if last_readings:
        return last_readings
    return None


def get_next_readings_by_room_and_date(room_id: str, date: date) -> MeterReading | None:
    """
    Находит следующие показания по комнате для определённой даты. Если нет - то последние показания.
    """
    next_readings = MeterReading.objects.filter(room_id=room_id, date__gte=date).order_by('date').first()
    if next_readings:
        return next_readings
    # Если не нашли - последние показания.
    next_readings = MeterReading.objects.filter(room_id=room_id).order_by('-date').first()


def get_readings_by_period(room_id: str, date_begin: date | None = None, date_end: date | None = None):
    """
    Возвращает показания от даты <= date_begin и >= date_end
    """
    if date_begin is None:
        date.today() - timedelta(days=30)
    if date_end is None:
        date.today()
    # Находим ближайшие даты <= begin, >= end
    first_record = get_last_readings_by_room_and_date(room_id=room_id, date=date_begin)
    last_record = get_next_readings_by_room_and_date(room_id=room_id, date=date_begin)
    if first_record is None or last_record is None:
        return None
    meter_readings = MeterReading.objects.filter(
        room_id=room_id,
        date__lte=first_record.date,
        date__gte=last_record.date
    ).all()
    return meter_readings
