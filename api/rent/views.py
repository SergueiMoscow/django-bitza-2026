from django.db.models import Max, Prefetch
from django.db.models.functions import Coalesce
from rest_framework import status, serializers, generics
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models

from api.rent.contract_print_serializers import ContractPrintListSerializer, ContractPrintSerializer
from api.rent.serializers import RoomDebtSerializer, PaymentSerializer, ContractPaymentsSerializer, \
    PaymentCreateSerializer
from rent.mobile_services import get_summary_rooms
from rent.models import Room, Contract, Payment, ContractPrint
from rent.repository import get_active_contracts_with_latest_print


class RoomDebtListAPIView(APIView):
    """
    Для Summary
    Все (активные) комнаты с количеством месяцев долга и html_class для цвета
    """
    def get(self, request: Request):
        data = get_summary_rooms()
        serializer = RoomDebtSerializer(data, many=True)
        return Response(serializer.data)


class RoomPaymentsAPIView(APIView):
    def get(self, request: Request, room_id: str, last_payments: int = 3):
        """
        Оплаты для одной комнаты (последние x оплат)
        """
        room = get_object_or_404(Room, pk=room_id)
        active_contract = Contract.objects.filter(room=room, status='A').order_by('-date_begin').first()
        if active_contract:
            payments = Payment.objects.filter(contract=active_contract).order_by('-date')[:last_payments][::-1]
            data = {
                'contract': active_contract,
                'payments': payments,
            }
            serializer = ContractPaymentsSerializer(data, context={'request': request})
            return Response(serializer.data)
        return Response(
            {'detail': 'Активный договор для этой комнаты не найден.'},
            status=status.HTTP_404_NOT_FOUND
        )

    def post(self, request: Request, room_id: str):
        """
        Создание нового платежа для комнаты.
        """
        # Проверяем, что комната из URL существует
        room = get_object_or_404(Room, pk=room_id)

        # Инициализируем сериализатор с данными запроса и контекстом
        print(f"Тип request.data: {type(request.data)}")
        print(f"Содержимое request.data: {request.data}")
        request_data = request.data
        serializer = PaymentCreateSerializer(data=request_data, context={'request': request})

        # Проверяем валидность данных
        if serializer.is_valid():
            try:
                # Сохраняем платеж
                payment = serializer.save()

                # Сериализуем сохраненный платеж для ответа
                response_serializer = PaymentSerializer(payment, context={'request': request})

                # Возвращаем успешный ответ с данными платежа
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                # Возвращаем ошибку, если активный договор не найден
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Возвращаем ошибки валидации
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrintContractsView(generics.ListAPIView):
    """
    Возвращает список активных договоров с информацией о контакте, последними датами печати и статусом.
    """
    serializer_class = ContractPrintListSerializer

    def get_queryset(self):
        return Contract.objects.filter(status='A').annotate(
            latest_print_date=Max('prints__date')
        ).annotate(
            sort_date=Coalesce('latest_print_date', 'date_begin')
        ).order_by('sort_date').select_related(
            'contact'  # Добавлено для оптимизации запросов к Contact
        ).prefetch_related(
            Prefetch('prints', queryset=ContractPrint.objects.order_by('-date'))
        )

class ContractPrintCreateView(generics.CreateAPIView):
    """
    Позволяет добавлять записи в модель ContractPrint.
    """
    serializer_class = ContractPrintSerializer
