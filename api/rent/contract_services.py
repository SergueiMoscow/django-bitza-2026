from rent.models import Contract
from api.rent.rent_settings import CONTRACT_MAX_DURATION_DAYS, CONTRACT_ALARM_BEFORE_DAYS

def calculate_new_contract_date(contract: Contract):
    """
    Рассчитывает рекомендованную дату для нового договора
    """
