from datetime import datetime

from django.http import HttpResponseRedirect
from django.views.generic import ListView

from bitza.common_functions import get_menu_items_by_user
from work import forms
from work.services import list_work_by_user, add_work, is_work_opened, get_opened_work
from pytz import utc


class ListByUserView(ListView):
    model = 'work'
    template_name = 'work/main.html'
    paginate_by = 30
    context_object_name = 'list'
    user = None

    def get_queryset(self):
        return list_work_by_user(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_work_opened'] = is_work_opened(self.request.user)
        if context['is_work_opened']:
            work = get_opened_work(self.request.user)
            form = forms.EndWorkForm(instance=work)
        else:
            form = forms.BeginWorkForm()
        menu = get_menu_items_by_user(self.request.user)
        labels = ('Начало', 'Окончание', 'Проект', 'Описание', 'Время работы')
        context['menu'] = menu
        context['labels'] = labels
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('begin'):
            add_work(request)
        elif request.POST.get('end'):

            work = get_opened_work(self.request.user)
            form = forms.EndWorkForm(request.POST)
            if form.is_valid():
                work.project = form.cleaned_data['project']
                work.description = form.cleaned_data['description']
                work.time_end = datetime.now()
                # time_begin_naive = work.time_begin.replace(tzinfo=None)
                # time_end_naive = work.time_end.replace(tzinfo=None)
                # work.worked_out = (time_end_naive - time_begin_naive).total_seconds()
                time_begin_aware = work.time_begin.astimezone(utc)
                time_end_aware = work.time_end.astimezone(utc)
                work.worked_out = (time_end_aware - time_begin_aware).total_seconds()
                work.save()
        return HttpResponseRedirect(request.path)

