from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.rent.serializers import RoomDebtSerializer, PaymentSerializer, ContractPaymentsSerializer
from rent.mobile_services import get_summary_rooms
from rent.models import Room, Contract, Payment


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
    """
    Оплаты для одно комнаты (последние x оплат)
    """
    def get(self, request: Request, room_id: str, last_payments: int = 3):
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


