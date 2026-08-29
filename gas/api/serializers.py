from django.db.models import Min
from rest_framework import serializers

from gas.models import GasRecord


class GasRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasRecord
        fields = [
            'id', 'message_id', 'date', 'gas_taken_date', 'quantity', 'capacity',
            'room', 'payment_date', 'amount', 'receiver', 'comments', 'linked_record',
            'sender_user_id', 'sender_name',
        ]
        read_only_fields = ['id', 'message_id']

    def create(self, validated_data):
        # message_id исторически приходил из телеграм-бота (id сообщения) — здесь записи
        # создаются не из бота. Генерируем заведомо непересекающееся с реальными
        # (положительными) telegram message_id отрицательное значение — на единицу меньше
        # самого маленького существующего, чтобы точно не выйти за диапазон integer.
        min_id = GasRecord.objects.aggregate(m=Min('message_id'))['m'] or 0
        validated_data['message_id'] = min(min_id, 0) - 1
        return super().create(validated_data)
