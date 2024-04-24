from typing import List, Tuple, Any

from django.contrib.auth.models import User
from django.db.models import Subquery
from rent.models import Room, Contract, Tokens


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
            result.append((str(row.shortname), str(row.shortname)))
        return tuple(result)
    return tuple([])


def get_user_by_token(token: str) -> User | None:
    token = Tokens.objects.get(token=token)
    if token:
        return token.user
    return None
