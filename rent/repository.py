from typing import List, Tuple, Any

from django.contrib.auth.models import User
from django.db.models import Subquery, Max, Prefetch
from rent.models import Room, Contract, Tokens, Payment, BankAccount, ContractPrint


def get_vacant_rooms() -> tuple[tuple[str, str], ...]:
    active_contracts = Contract.objects.filter(status='A').values('room_id')
    vacant_rooms = Room.objects.filter(status='A').exclude(shortname__in=Subquery(active_contracts))
    result = []
    if vacant_rooms:
        for row in vacant_rooms:
            result.append((str(row.shortname), str(row.shortname)))
        return tuple(result)
    return tuple([])


def get_active_rooms() -> tuple[tuple[str, str], ...]:
    active_rooms = Room.objects.filter(status='A')
    result = []
    if active_rooms:
        for row in active_rooms:
            result.append((str(row.shortname), str(row.name)))
        return tuple(result)
    return tuple([])


def get_user_by_token(token: str) -> User | None:
    token = Tokens.objects.get(token=token)
    if token:
        return token.user
    return None


def get_active_contract_by_room_id(room_id: str):
    return Contract.objects.filter(room=room_id, status='A').first()


def get_last_payments_by_room(room_id: str, count: int = 3):
    contract = get_active_contract_by_room_id(room_id)
    payments = Payment.objects.filter(contract=contract).order_by('-date')[:count]
    if len(payments):
        payments = payments[::-1]
        payments = [
            {
                'date': payment.date,
                'amount': payment.amount,
                'discount': payment.discount,
                'total': payment.total,
                'account': payment.bank_account,
            }
            for payment in payments
        ]
    else:
        payments = []
    return payments


def get_user_bank_accounts(user):
    accounts = BankAccount.objects.filter(users=user).values('id', 'name')
    return list(accounts)


def get_active_contracts() -> List[Contract]:
    """
    Возвращает список активных (status='A') договоров
    """
    contracts = Contract.objects.filter(status='A').order_by('date')
    return contracts


def get_active_contracts_with_latest_print_date():
    """
    Возвращает список активных договоров + дата последней печати
    """
    return Contract.objects.filter(status='A').annotate(
        latest_print_date=Max('prints__date')  # Использует related_name 'prints'
    )


def get_active_contracts_with_latest_print():
    """
    Возвращает список активных договоров + список последних печатей
    <result>.latest_prints[0] - последняя печать договора (дата + форма)
    """
    latest_print_qs = ContractPrint.objects.order_by('-date')
    prefetch = Prefetch(
        'prints',
        queryset=latest_print_qs,
        to_attr='latest_prints'
    )

    contracts = Contract.objects.filter(
        status='A'
    ).prefetch_related(prefetch)

    return contracts
