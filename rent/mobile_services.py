from rent.models import ExpectedPayments
from rent.repository import get_active_rooms, get_last_payments_by_room


def get_summary_rooms(current_room: str = None):
    """
    Возвращает список словарей активных комнат. Ключи:
    room, debt_month, debt_rur, html_class (room_vacant, room_no_debt, room_little_debt, room_big_debt),
    date_begin, price, last_payment_date (None для свободных комнат)
    """
    expected_payments = ExpectedPayments.objects.all().values()
    active_rooms = get_active_rooms()
    result = []
    for room in active_rooms:
        contract_data = next((item for item in expected_payments if item["room"] == room[0]), None)
        if contract_data is None:
            # Комната свободна
            debt_month = 0
            debt_rur = 0
            html_class = 'room_vacant'
            date_begin = None
            price = None
            last_payment_date = None
        else:
            debt_month = contract_data['debt_month']
            debt_rur = contract_data['debt_rur']
            date_begin = contract_data['date_begin']
            price = contract_data['price']
            last_payment_date = contract_data['last_payment_date']
            if debt_month <= 0:
                html_class = 'room_no_debt'
            elif debt_month > 1:
                html_class = 'room_big_debt'
            else:
                html_class = 'room_little_debt'
        if current_room and room[0] == current_room:
            html_class = 'current'

        result.append({
            'name': room[0],
            'debt_month': debt_month,
            'debt_rur': debt_rur,
            'html_class': html_class,
            'date_begin': date_begin,
            'price': price,
            'last_payment_date': last_payment_date,
        })

    return result


def get_payments_context(room: str):
    payments = get_last_payments_by_room(room)
    return payments
