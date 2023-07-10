from logging import debug

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from bitza.common_functions import GROUPS, get_menu_items, is_in_group
from rent.forms import ContractModelForm, PaymentModelForm
from rent.models import Contract, Contact, Payment, Room


class PaymentListView(UserPassesTestMixin, ListView):
    template_name = 'rent/payments.html'
    context_object_name = 'payments'
    paginate_by = 30

    def test_func(self):
        return is_in_group(self.request.user, group=GROUPS['owners'])

    def post(self, request, *args, **kwargs):
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
        return redirect('payments')

    def get_queryset(self):
        if self.request.GET.get('q'):
            return Payment.objects.all().filter(
                Q(contract__number__icontains=self.request.GET.get('q')) |
                Q(bank_account__icontains=self.request.GET.get('q'))
            ).order_by('-time')
        elif self.request.GET.get('contract'):
            return Payment.objects.filter(
                contract=self.request.GET.get('contract')
            ).order_by('-time')
        else:
            return Payment.objects.all().order_by('-time')

    def get_template_names(self):
        if self.request.GET.get('container') == 'div':
            return ['rent/payments_list.html', 'rent/payments.html']
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = get_menu_items('owners')
        context['labels'] = ['Комната', 'Клиент', 'Дата', 'Сумма', 'Оплата', 'Статус', '']
        context['form'] = PaymentModelForm()
        queryset = self.get_queryset()  # Payments.objects.all().order_by('-time')
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        debug("Всего элементов:", len(context['payments']))
        debug("Page_obj: ", context['page_obj'])
        return context
