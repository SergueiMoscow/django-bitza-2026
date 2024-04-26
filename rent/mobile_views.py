from django.utils import timezone

from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView

from bitza.common_functions import is_in_group, GROUPS
from rent.forms import PaymentModelForm
from rent.mobile_services import get_summary_rooms, get_payments_context
from rent.models import ExpectedPayments, Room, Contract, Payment
from rent.repository import get_active_rooms, get_user_by_token


class SummaryView(UserPassesTestMixin, TemplateView):
    template_name = 'rent/mobile/summary.html'

    def get_context_data(self, **kwargs):
        context = {'rooms': get_summary_rooms()}
        return context

    def test_func(self):
        if self.request.GET.get('token'):
            token = self.request.GET.get('token')
            self.request.user = get_user_by_token(token)
            login(self.request, self.request.user)
        # TODO: доделать
        return True
        return is_in_group(self.request.user, group=GROUPS['electricity'])


@method_decorator(csrf_exempt, name='dispatch')
class RoomPaymentsView(DetailView):
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
            context['payments'] = Payment.objects.filter(contract=active_contract).order_by('-date')[:n]
            context['today'] = timezone.now()
            form = PaymentModelForm()
            # TODO: пока hardcode. При наличии изменений ЗАСУНУТЬ ВСЁ В ТАБЛИЦУ!!!
            if self.request.user.username == "Валя":
                form.fields['bank_account'].choices = [('Валя', 'Валя')]
            elif self.request.user.username == "Ольга":
                form.fields['bank_account'].choices = [('Ольга', 'Ольга'), ('Валя', 'Валя')]
            else:
                form.fields['bank_account'].choices = [('Сергей', 'Сергей'), ('Сбер', 'Сбер'), ('Авангард', 'Авангард'),
                                                       ('Тинькофф', 'Тинькофф')]
            context['form'] = form

        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        room = kwargs.get('room')
        kwt_count = data.get('kwt_count')
        if room and kwt_count is not None:
            # reading = MeterReading(room_id=room, date=date.today(), kwt_count=kwt_count, user=request.user)
            # reading.save()
            try:
                save_readings(room, kwt_count, request.user)
            except ValueError as e:
                return JsonResponse({'error': e.args[0]})
        else:
            return JsonResponse({'error': 'Missing room or kwt_count'})
        next_room_id = get_first_room_for_input()
        if next_room_id is not None:
            current = get_readings_context(next_room_id)
            return JsonResponse(current, safe=False)
        else:
            readings_context = get_readings_context()
            return JsonResponse({'success': 'Сегодня всё заполнено', 'rooms': readings_context['rooms']})
