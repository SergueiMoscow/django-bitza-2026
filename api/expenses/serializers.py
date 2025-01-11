# expenses/serializers.py

from rest_framework import serializers
from datetime import datetime

class ChequeFilterSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False, format="%Y-%m-%dT%H:%M:%S%z", help_text="Начальная дата для фильтрации по покупке")
    end_date = serializers.DateTimeField(required=False, format="%Y-%m-%dT%H:%M:%S%z", help_text="Конечная дата для фильтрации по покупке")
    seller = serializers.CharField(required=False, allow_blank=True, help_text="Продавец для фильтрации")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Заметки для фильтрации")
    total_op = serializers.ChoiceField(choices=['<', '<=', '==', '>=', '>'], required=False, help_text="Операция для фильтрации по общей сумме")
    total_value = serializers.FloatField(required=False, help_text="Значение для фильтрации по общей сумме")
    search = serializers.CharField(required=False, allow_blank=True, help_text="Общий поиск по всем строковым полям")
