from datetime import timedelta, date

from django.utils import timezone
from rest_framework import generics, status
from django.db.models import Subquery, OuterRef, DateField, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Value, DecimalField
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from rent.models import Room
from .serializers import RoomLatestReadingSerializer, MeterReadingCreateSerializer, ConsumptionResponseSerializer
from ..models import MeterReading
from ..services import get_all_rooms_consumption


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


class RoomsConsumptionView(APIView):
    def get(self, request: Request, format=None):
        date_begin_str = request.query_params.get('date_begin')
        date_end_str = request.query_params.get('date_end')
        today = timezone.now().date()
        default_date_end = today
        default_date_begin = today - timedelta(days=30)

        try:
            if date_begin_str:
                date_begin = date.fromisoformat(date_begin_str)
            else:
                date_begin = default_date_begin
            if date_end_str:
                date_end = date.fromisoformat(date_end_str)
            else:
                date_end = default_date_end

        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            results = get_all_rooms_consumption(date_begin, date_end, sort_reverse=False)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
        data = {
            'date_begin': date_begin,
            'date_end': date_end,
            'results': results,
        }
        serializer = ConsumptionResponseSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
