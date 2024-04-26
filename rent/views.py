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
