from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from bitza.common_functions import GROUPS, get_menu_items, is_in_group
from rent.forms import ContractModelForm
from rent.models import Contract, Contact, Room


class ContractListView(UserPassesTestMixin, ListView):
    template_name = 'rent/contracts.html'
    context_object_name = 'contracts'
    paginate_by = 30

    def test_func(self):
        return is_in_group(self.request.user, group=GROUPS['owners'])

    def post(self, request, *args, **kwargs):
        user = request.user
        form = ContractModelForm(request.POST)
        if form.is_valid():
            contract_obj = form.save(commit=False)
            if not contract_obj:
                return HttpResponseBadRequest('Invalid form data')
            else:
                contract_obj.number = Contract.new_contract_number(form.cleaned_data['date_begin'],
                                                                   form.cleaned_data['vacant_room'])
                contract_obj.user = user
                selected_contact = int(request.POST.get('contact_id'))
                contract_obj.contact = Contact.objects.get(pk=selected_contact)
                contract_obj.status = 'A'
                contract_obj.room = get_object_or_404(Room, pk=form.cleaned_data['vacant_room'])
                contract_obj.save()
                messages.success(request, 'Contract created successfully!')
        else:
            messages.error(request, 'Form is not valid')

        return redirect('contracts')

    def get_queryset(self):
        if self.request.GET.get('q'):
            return Contract.objects.all().filter(
                Q(number__icontains=self.request.GET.get('q')) |
                Q(contact__name__icontains=self.request.GET.get('q')) |
                Q(contact__surname__icontains=self.request.GET.get('q'))
            ).order_by('-date_begin')
        else:
            return Contract.objects.all().order_by('-date_begin')

    def get_template_names(self):
        if self.request.GET.get('container') == 'div':
            return ['rent/contracts_list.html', 'rent/contracts.html']
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = get_menu_items('owners')
        context['labels'] = ['Комната', 'Клиент', 'Дата', 'Сумма', 'Оплата', 'Статус', '']
        context['form'] = ContractModelForm()
        queryset = self.get_queryset()  # Contract.objects.all().order_by('-date_begin')
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        print("Всего элементов:", len(context['contracts']))
        print("Page_obj: ", context['page_obj'])
        return context
