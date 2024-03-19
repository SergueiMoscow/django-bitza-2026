import pdb
from logging import debug

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from bitza.common_functions import is_in_group, GROUPS, get_menu_items_by_group
from rent.forms import PaymentModelForm, ContractModelForm
from rent.models import ExpectedPayments, Payment, Room, Contract, Contact
from rent.repository import get_vacant_rooms


def summary(request):
    print(f'Summary: request: {request}')
    user = request.user
    print(f'Summary: user: {user}')
    if not is_in_group(user, group=GROUPS['owners']):
        raise Http404()
    summary_lst = ExpectedPayments.objects.all()
    menu = get_menu_items_by_group('owners')
    vacant_rooms = get_vacant_rooms()
    context = {'summary': summary_lst, 'menu': menu, 'vacant_rooms': vacant_rooms}
    print(f'menu: {menu}')
    return render(
        request,
        'rent/summary.html',
        context=context
    )


def close_contract(request):
    user = request.user
    if not is_in_group(user, group=GROUPS['owners']):
        raise Http404()
    if request.method == 'POST':
        contract_number = request.POST.get('number')
        contract_obj = get_object_or_404(Contract, pk=contract_number)
        contract_obj.close_date = request.POST.get('close_date')
        contract_obj.status = 'B'
        # pdb.set_trace()
        contract_obj.save()
        return redirect('rent:contracts')
    else:
        contract_number = request.GET.get('contract')
        contract_obj = get_object_or_404(Contract, pk=contract_number)
        return render(
            request,
            'rent/contract_close.html',
            context={'contract': contract_obj}
        )


# TODO: Delete functions: payments_delete_this_function, payments_delete_all_this_function
# def payments_delete_this_function(request):
#     user = request.user
#     payments_obj = Payment
#     if not is_in_group(user, group=GROUPS['owners']):
#         raise Http404()
#     if request.POST:
#         form = PaymentModelForm(request.POST)
#         if form.is_valid():
#             payment_obj = Payment()
#             print(f'cleaned data: {form.cleaned_data}')
#             payment_obj.date = form.cleaned_data['date']
#             payment_obj.room = get_object_or_404(Room, pk=form.cleaned_data['room'])
#             payment_obj.amount = form.cleaned_data['amount']
#             payment_obj.discount = form.cleaned_data['discount']
#             payment_obj.total = form.cleaned_data['total']
#             payment_obj.bank_account = form.cleaned_data['bank_account']
#             payment_obj.type = 'Alq'
#             payment_obj.concept = f'Аренда {form.cleaned_data["room"]}'
#             payment_obj.book_account = 'Приход'
#             payment_obj.contract = Contract.get_active_contract_by_room(form.cleaned_data['room'])
#             payment_obj.user = user
#             payment_obj.save()
#             print('saved')
#         else:
#             print(f'form not valid {form.errors}')
#     else:
#         form = PaymentModelForm()
#     if request.GET.get('contract'):
#         contract = request.GET.get('contract')
#         result = Payment.objects.filter(contract=contract)
#     else:
#         result = Payment.objects.all()
#     page = request.GET.get('page', 1)
#     paginator = Paginator(result, 30)
#     try:
#         list_payments = paginator.page(page)
#     except PageNotAnInteger:
#         list_payments = paginator.page(1)
#     except EmptyPage:
#         list_payments = paginator.page(paginator.num_pages)
#     rooms_list = Contract.get_active_rooms_for_js()
#     menu = get_menu_items_by_group('owners')
#     labels = ['Дата', 'Комната', 'Сумма', 'Оплачено', 'Назначение', 'Счёт']
#     years = Payment.list_years(payments_obj)
#     context = {
#         'payments': list_payments,
#         'menu': menu,
#         'labels': labels,
#         'years': years,
#         'form': form,
#         'rooms_list': rooms_list
#     }
#
#     return render(
#         request,
#         'rent/payments.html',
#         context=context,
#     )
#
#
# def contracts__delete_this_function(request):
#     user = request.user
#     if not is_in_group(user, group=GROUPS['owners']):
#         raise Http404()
#     if request.POST:
#         form = ContractModelForm(request.POST)
#         if form.is_valid():
#             contract_obj = form.save(commit=False)
#             contract_obj.room = get_object_or_404(Room, pk=form.cleaned_data['vacant_room'])
#             contract_obj.number = Contract.new_contract_number(form.cleaned_data['date_begin'],
#                                                                form.cleaned_data['vacant_room'])
#             contract_obj.user = user
#             selected_contact = int(request.POST.get('contact_id'))
#             contract_obj.contact = Contact.objects.get(pk=selected_contact)
#             contract_obj.status = 'A'
#             contract_obj.save()
#         else:
#             print(f'form not valid {form.errors}')
#     else:
#         form = ContractModelForm()
#     result = Contract.objects.all()
#     page = request.GET.get('page', 1)
#     paginator = Paginator(result, 30)
#     try:
#         list_payments = paginator.page(page)
#     except PageNotAnInteger:
#         list_payments = paginator.page(1)
#     except EmptyPage:
#         list_payments = paginator.page(paginator.num_pages)
#     menu = get_menu_items_by_group('owners')
#     labels = ['Комната', 'Клиент', 'Дата', 'Сумма', 'Оплата', 'Статус', '']
#     context = {
#         'contracts': list_payments,
#         'menu': menu,
#         'labels': labels,
#         'form': form,
#     }
#
#     return render(
#         request,
#         'rent/contracts.html',
#         context=context,
#     )


def clients(request):
    pass


def query_contacts(request):
    q = request.GET.get('q')
    list_contacts = Contact.search_contacts(q)
    result = {}
    if list_contacts is None:
        return JsonResponse(result)
    for contact in list_contacts:
        result[contact.id] = f'{contact.name} {contact.surname}'
    return JsonResponse(result)


def new_payment(request):
    menu = get_menu_items_by_group('owners')
    current_contract = None
    contract_number = None
    if request.GET.get('contract'):
        contract_number = request.GET.get('contract')
        current_contract = Contract.objects.get(pk=contract_number)

    form = PaymentModelForm()
    form.fields['room'].initial = current_contract.room
    form.fields['amount'].initial = current_contract.price
    form.fields['discount'].initial = current_contract.discount
    form.fields['total'].initial = current_contract.price - current_contract.discount
    context = {'form': form, 'menu': menu}

    return render(
        request,
        'rent/new_payment.html',
        context=context,

    )
