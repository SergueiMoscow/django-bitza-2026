from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView

from bitza.common_functions import is_in_group, GROUPS
from rent.controllers.save_payment import save_payment
from rent.forms import PaymentModelForm
from rent.mobile_services import get_summary_rooms, get_payments_context
from rent.models import ExpectedPayments, Room, Contract, Payment
from rent.repository import get_active_rooms, get_user_by_token


class SummaryView(UserPassesTestMixin, TemplateView):
    template_name = 'rent/mobile/summary.html'

    def get_context_data(self, **kwargs):
        room_id = kwargs.get('room_id', None)
        context = {'rooms': get_summary_rooms(), 'room_id': room_id}
        return context

    def test_func(self):
        if self.request.GET.get('token'):
            token = self.request.GET.get('token')
            self.request.user = get_user_by_token(token)
            login(self.request, self.request.user)
        return is_in_group(self.request.user, group=GROUPS['administrators'])


@method_decorator(csrf_exempt, name='dispatch')
class RoomPaymentsView(DetailView):
    """
    При клике на номере комнаты подгружает последние n платежей
    """
    model = Room
    template_name = 'rent/mobile/payments.html'
    context_object_name = 'room'

    def get_object(self):
        room_id = self.kwargs.get("room_id")
        return get_object_or_404(Room, pk=room_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        n = 3
        room = self.get_object()
        active_contract = Contract.objects.filter(room=room, status='A').order_by('-date_begin').first()
        context['active_contract'] = active_contract
        if active_contract:
            context['contract'] = active_contract
            context['contact'] = active_contract.contact
            payments = Payment.objects.filter(contract=active_contract).order_by('-date')[:n][::-1]
            # payments.reverse()
            context['payments'] = payments
            context['today'] = timezone.now()
            form = PaymentModelForm()
            form.fields['room'].initial = active_contract.room
            form.fields['amount'].initial = active_contract.price
            form.fields['discount'].initial = active_contract.discount
            form.fields['total'].initial = active_contract.price - active_contract.discount

            # TODO: пока hardcode. При наличии изменений ЗАСУНУТЬ ВСЁ В ТАБЛИЦУ!!!
            if self.request.user.username == "valentina":
                form.fields['bank_account'].choices = [('Валя', 'Валя')]
            elif self.request.user.username == "olga":
                form.fields['bank_account'].choices = [('Ольга', 'Ольга'), ('Валя', 'Валя')]
            else:
                form.fields['bank_account'].choices = [('Сергей', 'Сергей'), ('Сбер', 'Сбер'), ('Авангард', 'Авангард'),
                                                       ('Тинькофф', 'Тинькофф')]
            context['form'] = form

        return context

    def post(self, request, *args, **kwargs):
        room_id = request.POST.get('room', None)
        save_payment(request)
        if room_id:
            return redirect(reverse('rent:review', kwargs={'room_id': room_id}))
        return redirect('rent:review')


def refresh_list_rooms(request, room_id: str):
    rooms = get_summary_rooms(room_id)
    return JsonResponse(rooms, safe=False)

