from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import rent.views as rent_views
from bitza.common_functions import is_in_group, GROUPS
from rent.models import Tokens
from django.contrib.auth import authenticate, login
from bitza.backends import TokenBackend


@csrf_exempt
def main(request):
    if request.GET.get('token'):
        # Не закончено
        # Проблема: Authentification не сохраняется в сессии
        # Любой преход по ссылке не видит аутентификацию
        token = request.GET.get('token')
        user = TokenBackend().authenticate(request=request, token=token, backend='bitza.backends.TokenBackend')
        if user is None:
            return render(request, 'rent/main.html', {'error': 'Invalid token'})
        else:
            print(f'user1: {user.username}, id: {user.id}')
            user.backend = 'bitza.backends.TokenBackend'
            login(request, user)
            # return redirect('main')
    else:
        user = request.user
    context = {'current_user': 'Default'}
    if is_in_group(user, GROUPS['owners']):
        print(f'{user.username} is owner')
        return rent_views.summary(request)
    return render(
        request,
        'main.html',
        context=context
    )


