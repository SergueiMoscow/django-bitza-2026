from rest_framework import serializers

from rent.models import Payment, Contract, BankAccount
from rent.repository import get_user_bank_accounts


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