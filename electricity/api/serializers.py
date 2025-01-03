from rest_framework import serializers
from django.utils import timezone

from electricity.models import MeterReading
from rent.models import Room


class RoomLatestReadingSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    kwt_count = serializers.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        model = Room
        fields = ['shortname', 'name', 'date', 'kwt_count']


class MeterReadingCreateSerializer(serializers.Serializer):
    room = serializers.CharField(max_length=5)
    kwt_count = serializers.DecimalField(max_digits=10, decimal_places=1)

    def validate_room(self, value):
        try:
            room = Room.objects.get(shortname=value)
        except Room.DoesNotExist:
            raise serializers.ValidationError(f"Комната с shortname '{value}' не существует.")
        return value

    def create(self, validated_data):
        room_shortname = validated_data['room']
        kwt_count = validated_data['kwt_count']
        date_today = timezone.now().date()

        room = Room.objects.get(shortname=room_shortname)
        user = self.context['request'].user

        # Проверяем, существует ли уже запись на сегодняшнюю дату
        meter_reading, created = MeterReading.objects.update_or_create(
            room=room,
            date=date_today,
            defaults={'kwt_count': kwt_count, 'user': user}
        )
        return meter_reading


class RoomConsumptionSerializer(serializers.Serializer):
    room = serializers.CharField()
    consumption = serializers.FloatField()
    color = serializers.CharField()


class ConsumptionResponseSerializer(serializers.Serializer):
    date_begin = serializers.DateField()
    date_end = serializers.DateField()
    results = RoomConsumptionSerializer(many=True)
