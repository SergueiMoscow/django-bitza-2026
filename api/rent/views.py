from django.db.models import Max, Prefetch, Q, Count
from django.db.models.functions import Coalesce
from rest_framework import status, serializers, generics
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from api.rent.contract_print_serializers import ContractPrintListSerializer, ContractPrintSerializer
from api.rent.serializers import RoomDebtSerializer, PaymentSerializer, ContractPaymentsSerializer, \
    PaymentCreateSerializer, ContactSerializer, DocumentSerializer, BuildingCRUDSerializer, \
    RoomCRUDSerializer, ContractCRUDSerializer, ContractCreateSerializer
from rent.mobile_services import get_summary_rooms
from rent.models import Room, Contract, Payment, ContractPrint, Contact, Document, Building


class RoomDebtListAPIView(APIView):
    """
    Для Summary
    Все (активные) комнаты с количеством месяцев долга и html_class для цвета
    """
    def get(self, request: Request):
        data = get_summary_rooms()
        serializer = RoomDebtSerializer(data, many=True)
        return Response(serializer.data)


class PaymentsPagination(PageNumberPagination):
    page_size = 30


class PaymentListAPIView(generics.ListAPIView):
    """
    Все оплаты (аренда), без привязки к конкретному помещению. Поиск — по номеру
    комнаты, номеру договора или счёту (?q=), как в старом UI.
    """
    serializer_class = PaymentSerializer
    pagination_class = PaymentsPagination

    def get_queryset(self):
        qs = Payment.objects.filter(type='Alq').select_related('room', 'contract').order_by('-date', '-time')
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(room__shortname__icontains=q) |
                Q(contract__number__icontains=q) |
                Q(bank_account__icontains=q)
            )
        return qs


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

        # room берём из URL, а не из тела запроса — так эндпоинт остаётся однозначным
        # (и не полагается на то, что клиент продублирует room_id в теле).
        request_data = {**request.data, 'room': room_id}
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


class ContactListCreateAPIView(generics.ListCreateAPIView):
    """
    Список клиентов (с поиском по ?q=) и создание нового клиента.
    """
    serializer_class = ContactSerializer

    def get_queryset(self):
        q = self.request.query_params.get('q')
        if q:
            return Contact.search_contacts(q)
        return Contact.objects.all()


class ContactDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и редактирование одного клиента.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDocumentListCreateAPIView(generics.ListCreateAPIView):
    """
    Документы (сканы/фото) клиента: список и загрузка новых.
    """
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(contact_id=self.kwargs['contact_id']).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(contact_id=self.kwargs['contact_id'])


class DocumentDetailAPIView(generics.DestroyAPIView):
    """
    Удаление документа клиента.
    """
    queryset = Document.objects.all()

    def perform_destroy(self, instance):
        instance.image_file.delete(save=False)
        instance.delete()


class BuildingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingCRUDSerializer


class BuildingDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingCRUDSerializer


class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.select_related('building').all()
    serializer_class = RoomCRUDSerializer


class RoomDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCRUDSerializer
    lookup_field = 'shortname'
    lookup_url_kwarg = 'shortname'


class ContractListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contract.objects.select_related('room', 'contact').order_by('-date_begin')

    def get_serializer_class(self):
        return ContractCreateSerializer if self.request.method == 'POST' else ContractCRUDSerializer


class ContractDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Contract.objects.select_related('room', 'contact')
    serializer_class = ContractCRUDSerializer
    lookup_field = 'number'
    lookup_url_kwarg = 'number'


class PaymentFieldSuggestionsView(APIView):
    """
    Реально встречающиеся в оплатах значения bank_account/book_account (тип 'Alq' — аренда).
    Модельные choices этих полей не соответствуют тому, что реально вводится годами, поэтому
    берём варианты из данных, а не из choices.
    """

    def get(self, request):
        def distinct_values(field):
            rows = (
                Payment.objects.filter(type='Alq')
                .exclude(**{f'{field}__isnull': True})
                .exclude(**{field: ''})
                .values(field)
                .annotate(n=Count('id'))
                .order_by('-n')
            )
            return [row[field] for row in rows]

        return Response({
            'bank_accounts': distinct_values('bank_account'),
            'book_accounts': distinct_values('book_account'),
        })
