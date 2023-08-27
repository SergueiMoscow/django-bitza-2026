from datetime import datetime

from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from work.models import Work


def add_paginator(request, rows):
    page = request.GET.get('page', 1)
    paginator = Paginator(rows, 30)
    try:
        page_list = paginator.page(page)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    return page_list


def list_work_by_user(request):
    result = Work.objects.filter(user=request.user)
    page_list = add_paginator(request, result)
    return page_list


def add_work(request):
    work = Work.objects.create(user=request.user, time_begin = datetime.now())
    work.time_begin = datetime.now()
    work.save()


def is_work_opened(user: User):
    work = get_opened_work(user)
    if work is None or work.time_end:
        return False
    else:
        return True


def get_opened_work(user: User):
    return Work.objects.filter(user=user).order_by('-time_begin').first()
