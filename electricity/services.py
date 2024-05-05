from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth.models import User

from rent.models import Room
from .models import MeterReading
from .repository import get_rooms_with_watt_counter, get_rooms_for_input_readings, get_last_readings_by_room, \
    get_last_reading_for_room


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
