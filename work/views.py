from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bitza.common_functions import get_menu_items_by_group, get_menu_items_by_user
from work import forms
from work.services import list_work_by_user


@login_required
def list_by_user_view_1(request: HttpRequest) -> HttpResponse:
    menu = get_menu_items_by_user(request.user)
    labels = ('Начало', 'Окончание', 'Проект', 'Описание', 'Время работы')
    if request.method == 'POST':
        form = forms.BeginWorkForm(request.POST)
    else:
        form = forms.BeginWorkForm()
    context = {
        'menu': menu,
        'labels': labels,
        'list': list_work_by_user(request),
        'form': form,
    }
    return render(request, 'work/main.html', context)
