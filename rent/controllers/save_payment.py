from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from rent.forms import PaymentModelForm
from rent.models import Payment, Contract, Room
from django.contrib import messages


def save_payment(request):
    form = PaymentModelForm(request.POST)
    if form.is_valid():
        payment_obj = Payment()
        print(f'cleaned data: {form.cleaned_data}')
        payment_obj.date = form.cleaned_data['date']
        payment_obj.room = get_object_or_404(Room, pk=form.cleaned_data['room'])
        payment_obj.amount = form.cleaned_data['amount']
        payment_obj.discount = form.cleaned_data['discount']
        payment_obj.total = form.cleaned_data['total']
        payment_obj.bank_account = form.cleaned_data['bank_account']
        payment_obj.type = 'Alq'
        payment_obj.concept = f'Аренда {form.cleaned_data["room"]}'
        payment_obj.book_account = 'Приход'
        payment_obj.contract = Contract.get_active_contract_by_room(form.cleaned_data['room'])
        payment_obj.user = request.user
        payment_obj.save()
        if not payment_obj:
            return HttpResponseBadRequest('Invalid form data')
        else:
            messages.success(request, 'Payment created successfully!')
    else:
        messages.error(request, 'Form is not valid')
