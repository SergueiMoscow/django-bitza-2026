from datetime import date

from django import forms
from django.forms import SelectDateWidget

from rent.models import Payment, Room, Contract, VacantRooms
from dateutil.relativedelta import relativedelta


class PaymentModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PaymentModelForm, self).__init__(*args, **kwargs)
        # print(f'Args: {args}')
        # print(f'Kwargs {kwargs}')

    class Meta:
        model = Payment
        fields = ['date', 'room', 'amount', 'discount', 'total', 'bank_account']
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'value': date.today()}),
            'room': forms.TextInput(attrs={'id': 'room'}),
            'amount': forms.TextInput(attrs={'id': 'amount'}),
            'discount': forms.TextInput(attrs={'id': 'discount'}),
            'total': forms.TextInput(attrs={'id': 'total'}),
            'bank_account': forms.Select()
        }


class ContractModelForm(forms.ModelForm):

    vacant_rooms = Room.get_vacant_rooms()
    select_contact = forms.CharField(
        label='Клиент',
        widget=forms.TextInput(attrs={'id': 'contact'})
    )
    vacant_room = forms.CharField(
        widget=forms.Select(
            choices=vacant_rooms,
            attrs={'value': vacant_rooms[0]}
        ),
        label='Свободные комнаты'
    )

    class Meta:
        model = Contract
        fields = [
            'date_begin',
            'date_end',
            # 'number',
            'pay_day',
            'price',
            # 'deposit',
            'discount',
            'form',
        ]
        widgets = {
            'date_begin': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'value': date.today()}),
            'date_end': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'value': date.today() + relativedelta(months=+6)}
            ),
            'price': forms.TextInput(attrs={'id': 'price'}),
            'discount': forms.TextInput(attrs={'id': 'discount'}),
            'deposit': forms.TextInput(attrs={'id': 'deposit', 'value': '0'}),
            'contact': forms.TextInput(attrs={'id': 'contact'}),
            'form': forms.Select(),
        }
