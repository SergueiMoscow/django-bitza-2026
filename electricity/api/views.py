from rest_framework import generics, status
from django.db.models import Subquery, OuterRef, DateField, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from django.db.models import Value, DecimalField

from rent.models import Room
from .serializers import RoomLatestReadingSerializer, MeterReadingCreateSerializer
from ..models import MeterReading


class RoomLatestReadingListView(generics.ListAPIView):
    serializer_class = RoomLatestReadingSerializer

    def get_queryset(self):
        latest_readings = MeterReading.objects.filter(room=OuterRef('shortname')).order_by('-date')
        return Room.objects.filter(
            has_watt_counter=True
        ).annotate(
            date=Subquery(latest_readings.values('date')[:1], output_field=DateField()),
            kwt_count=Coalesce(
                Subquery(latest_readings.values('kwt_count')[:1], output_field=DecimalField()),
                Value(0, output_field=DecimalField()),
                output_field=DecimalField()
            )
        )


class MeterReadingBulkCreateView(generics.CreateAPIView):
    serializer_class = MeterReadingCreateSerializer

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        meter_readings = serializer.save()
        return Response({"detail": "Meter readings processed successfully."}, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        return {'request': self.request}
