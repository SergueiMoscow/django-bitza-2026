from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from rent.models import Payment, Contract, BankAccount, Room, Contact, Document, Building
from rent.repository import get_user_bank_accounts
from api.rent.rent_settings import CONTRACT_MAX_DURATION_DAYS
from datetime import datetime, timedelta


class RoomDebtSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    debt_month = serializers.DecimalField(max_digits=5, decimal_places=2)
    debt_rur = serializers.DecimalField(max_digits=10, decimal_places=2)
    html_class = serializers.CharField(max_length=20)
    date_begin = serializers.CharField(max_length=10, allow_null=True)
    price = serializers.IntegerField(allow_null=True)
    last_payment_date = serializers.DateField(allow_null=True)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['room', 'date', 'amount', 'discount', 'total', 'bank_account', 'book_account']


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['number', 'room', 'price', 'discount']


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'name']


class ContractPaymentsSerializer(serializers.Serializer):
    contract = ContractSerializer()
    payments = PaymentSerializer(many=True)
    bank_accounts = serializers.SerializerMethodField()

    def get_bank_accounts(self, obj):
        user = self.context['request'].user
        accounts = get_user_bank_accounts(user)
        return accounts


class PaymentCreateSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%f'],
        error_messages={
            'invalid': 'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD или YYYY-MM-DDTHH:MM:SS.sss'
        }
    )
    # Модельные choices этих двух полей (Валя/Ольга/.../+/-/=) не совпадают с тем, что реально
    # вводится годами (Cash, Касса, Битца, Света...) — валидируем как обычный текст, а не по choices,
    # иначе форма отвергала бы почти все реальные значения.
    bank_account = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    book_account = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Payment
        fields = ['room', 'date', 'bank_account', 'book_account', 'amount', 'discount']

    # def validate_room(self, value):
    #     """
    #     Валидация поля room. Проверяет, что комната существует.
    #     """
    #     room = get_object_or_404(Room, pk=value)
    #     return room

    def validate_book_account(self, value):
        """
        Если book_account не указан, устанавливаем его в '+'.
        """
        if value is None:
            return 'Приход'
        return value

    def create(self, validated_data):
        """
        Создание записи Payment с установленными полями.
        """
        room = validated_data.pop('room')
        amount = validated_data.get('amount')
        discount = validated_data.get('discount') or 0
        total = amount - discount

        # Получение активного договора для комнаты
        active_contract = Contract.get_active_contract_by_room(room)
        if not active_contract:
            raise serializers.ValidationError('Активный договор для этой комнаты не найден.')

        # Установка типа платежа
        payment_type = 'Alq'  # 'Аренда'

        # Установка поля book_account, если оно не было передано
        book_account = validated_data.get('book_account') or '+'

        # Обработка поля date
        date_value = validated_data.get('date')
        if isinstance(date_value, datetime):
            date = date_value.date()
        else:
            date = date_value

        # Создание записи Payment
        payment = Payment.objects.create(
            contract=active_contract,
            room=room,
            date=date,
            bank_account=validated_data.get('bank_account'),
            book_account=book_account,
            amount=amount,
            discount=discount,
            total=total,
            type=payment_type,
            user=self.context['request'].user if self.context['request'].user.is_authenticated else None
        )
        return payment


class GeneratePDFSerializer(serializers.Serializer):
    contract_id = serializers.CharField()


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'surname', 'name', 'birth_date', 'birth_place', 'gender',
            'document_name', 'doc_series', 'doc_number', 'doc_date', 'doc_issued',
            'address1', 'address2', 'city', 'country', 'email', 'phone', 'notes',
        ]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'image_file', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class BuildingCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'address1', 'address2', 'zip', 'notes', 'status']


class RoomCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'shortname', 'name', 'building', 'floor', 'square',
            'price1', 'price2', 'description', 'status',
            'type_watt_counter', 'type_hot_water_counter', 'type_cold_water_counter',
        ]


class ContractCRUDSerializer(serializers.ModelSerializer):
    """Для чтения и редактирования существующего договора (число дней не пересчитывается)."""

    contact_name = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'number', 'date_begin', 'date_end', 'room', 'pay_day', 'price',
            'deposit', 'discount', 'contact', 'contact_name', 'status', 'close_date',
        ]
        read_only_fields = ['number']

    def get_contact_name(self, obj):
        if not obj.contact:
            return None
        return f'{obj.contact.surname or ""} {obj.contact.name or ""}'.strip() or None


class ContractCreateSerializer(serializers.ModelSerializer):
    """
    Для создания договора. duration_days (по умолчанию CONTRACT_MAX_DURATION_DAYS) используется,
    только если date_end не передан явно — так на фронте можно указать либо число дней, либо
    конкретную дату закрытия.
    """
    duration_days = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Contract
        fields = [
            'number', 'date_begin', 'date_end', 'room', 'pay_day', 'price',
            'deposit', 'discount', 'contact', 'duration_days',
        ]
        read_only_fields = ['number']
        extra_kwargs = {'date_end': {'required': False}}

    def create(self, validated_data):
        duration_days = validated_data.pop('duration_days', None) or CONTRACT_MAX_DURATION_DAYS
        date_begin = validated_data['date_begin']
        if not validated_data.get('date_end'):
            validated_data['date_end'] = date_begin + timedelta(days=duration_days)
        room = validated_data['room']
        validated_data['number'] = Contract.new_contract_number(date_begin.isoformat(), room.shortname)
        validated_data['status'] = 'A'
        return super().create(validated_data)
