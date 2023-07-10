from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import rent.views as rent_views
from bitza.common_functions import is_in_group, GROUPS
from rent.models import Tokens
from django.contrib.auth import login


def main(request):
    if request.GET.get('token'):
        token = Tokens.objects.filter(token=request.GET.get('token')).first()
        if token:
            user = User.objects.get(id=token.user_id)
            login(request, user)
        return redirect('summary')
    else:
        user = request.user
    if is_in_group(user, GROUPS['owners']):
        print(f'{user.username} is owner')
        return rent_views.summary(request)
    return render(
        request,
        'main.html'
    )


