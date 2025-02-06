from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

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
