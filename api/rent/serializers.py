from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from rent.models import Payment, Contract, BankAccount, Room
from rent.repository import get_user_bank_accounts
from datetime import datetime


class RoomDebtSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    debt_month = serializers.DecimalField(max_digits=5, decimal_places=2)
    html_class = serializers.CharField(max_length=20)


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
    template_id = serializers.CharField()
