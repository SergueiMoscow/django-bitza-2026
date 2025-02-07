from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta, date

from api.rent.rent_settings import CONTRACT_MAX_DURATION_DAYS, CONTRACT_ALARM_BEFORE_DAYS
from rent.models import Contract, ContractPrint, Contact


class ContactForContractPrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['surname', 'name']


class ContractPrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractPrint
        fields = ['id', 'date', 'form']


class ContractSerializer(serializers.ModelSerializer):
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
            return 'Подходит к завершению'
        else:
            return 'Активный'

    def get_recommended_contract_date(self, obj):
        status = self.get_status_description(obj)
        day = obj.date_begin.day
        today = timezone.now().date()

        # Функция для нахождения ближайшей прошлой даты с тем же днем
        def get_latest_past_date(year, month, day):
            while True:
                try:
                    candidate = date(year, month, day)
                    if candidate < today:
                        return candidate
                except ValueError:
                    # Неправильное число для месяца, пропускаем
                    pass
                # Переходим к предыдущему месяцу
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
                if year < 1900:  # Предотвращаем бесконечный цикл
                    return None

        # Функция для нахождения ближайшей будущей даты с тем же днем
        def get_earliest_future_date(year, month, day):
            while True:
                try:
                    candidate = date(year, month, day)
                    if candidate > today:
                        return candidate
                except ValueError:
                    # Неправильное число для месяца, пропускаем
                    pass
                # Переходим к следующему месяцу
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                if year > 3000:  # Предотвращаем бесконечный цикл
                    return None

        if status == 'Просрочен':
            recommended_date = get_latest_past_date(today.year, today.month, day)
        elif status == 'Подходит к завершению':
            recommended_date = get_earliest_future_date(today.year, today.month, day)
        else:
            recommended_date = None

        return recommended_date.isoformat() if recommended_date else None