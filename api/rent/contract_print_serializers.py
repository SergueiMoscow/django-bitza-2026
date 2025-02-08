import logging

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta, date

from api.rent.rent_settings import CONTRACT_MAX_DURATION_DAYS, CONTRACT_ALARM_BEFORE_DAYS
from rent.models import Contract, ContractPrint, Contact, ContractForm, get_latest_contract_form

logger = logging.getLogger(__name__)


class ContactForContractPrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['surname', 'name']


class ContractPrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractPrint
        fields = ['id', 'contract', 'date', 'form', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'form': {'required': False, 'allow_null': True}
        }

    def validate_contract(self, value):
        if not Contract.objects.filter(number=value.number, status='A').exists():
            raise serializers.ValidationError("Договор не существует или не активен.")
        return value

    def validate_form(self, value):
        if value is None:
            return get_latest_contract_form()
        return value


class ContractPrintListSerializer(serializers.ModelSerializer):
    latest_prints = ContractPrintSerializer(source='prints', many=True, read_only=True)
    status_description = serializers.SerializerMethodField()
    contact = ContactForContractPrintSerializer(read_only=True)
    recommended_contract_date = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'number',
            'status',
            'date_begin',
            'latest_prints',
            'status_description',
            'contact',
            'room',
            'recommended_contract_date',
        ]

    def get_status_description(self, obj):
        reference_date = obj.latest_print_date or obj.date_begin
        max_duration = timedelta(days=CONTRACT_MAX_DURATION_DAYS)
        alarm_before = timedelta(days=CONTRACT_ALARM_BEFORE_DAYS)
        end_date = reference_date + max_duration
        today = timezone.now().date()

        if end_date < today:
            return 'Просрочен'
        elif end_date - today <= alarm_before:
            return 'Завершается'
        else:
            return 'Активный'

    def get_recommended_contract_date(self, obj):
        status = self.get_status_description(obj)
        day = obj.date_begin.day
        today = timezone.now().date()
        max_iterations = 12

        # Функция для нахождения ближайшей прошлой даты с тем же днем
        def get_latest_past_date(year, month, day):
            iterations = 0
            while iterations < max_iterations:
                try:
                    candidate = date(year, month, day)
                    if candidate < today:
                        return candidate
                except ValueError:
                    logger.debug(f"Неверная дата: {year}-{month}-{day}")
                logger.debug(f"Итерация: year={year}, month={month}, day={day}")
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
                if year < 1900:
                    return None
                iterations += 1

        # Функция для нахождения ближайшей будущей даты с тем же днем
        def get_earliest_future_date(year, month, day):
            iterations = 0
            while iterations < max_iterations:
                try:
                    candidate = date(year, month, day)
                    if candidate > today:
                        return candidate
                except ValueError:
                    logger.debug(f"Неверная дата: {year}-{month}-{day}")
                logger.debug(f"Итерация: year={year}, month={month}, day={day}")
                # Переходим к следующему месяцу
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                if year > 3000:  # Предотвращаем бесконечный цикл
                    return None
                iterations += 1

        if status == 'Просрочен':
            recommended_date = get_latest_past_date(today.year, today.month, day)
        elif status == 'Завершается':
            recommended_date = get_earliest_future_date(today.year, today.month, day)
        else:
            recommended_date = None

        return recommended_date.isoformat() if recommended_date else None
