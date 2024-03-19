from typing import List, Tuple

from django.db.models import Subquery
from rent.models import Room, Contract


def get_vacant_rooms() -> Tuple[Tuple[str, str]]:
    active_contracts = Contract.objects.filter(status='A').values('room_id')
    vacant_rooms = Room.objects.filter(status='A').exclude(shortname__in=Subquery(active_contracts))
    result = []
    for row in vacant_rooms:
        result.append((str(row.shortname), str(row.shortname)))
    return tuple(result)
