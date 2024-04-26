from rent.models import ExpectedPayments
from rent.repository import get_active_rooms, get_last_payments_by_room


def get_summary_rooms():
    """
    Возвращает список словарей активных комнат. Ключи:
    room
    debt_month
    class (room_vacant, room_little_debt, room_big_debt)
    """
    expected_payments = ExpectedPayments.objects.all().values()
    active_rooms = get_active_rooms()
    result = []
    for room in active_rooms:
        debt_month = next((item for item in expected_payments if item["room"] == room[0]), None)
        if debt_month is None:
            # Комната свободна
            debt_month = 0
            html_class = 'room_vacant'
        else:
            debt_month = debt_month['debt_month']
            if debt_month < 0:
                html_class = 'room_no_debt'
            elif debt_month > 1:
                html_class = 'room_big_debt'
            else:
                html_class = 'room_big_debt'

        result.append({'name': room[0], 'debt_month': debt_month, 'html_class': html_class})

    return result


def get_payments_context(room: str):
    payments = get_last_payments_by_room(room)
    return payments
