from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import RegisterView, logout_view

app_name = 'api'

urlpatterns = [
    # Регистрация пользователя
    # path('register/', RegisterView.as_view(), name='register'),

    # Логин и получение токенов
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Обновление access-токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Выход пользователя
    path('logout/', logout_view, name='logout'),

    # Восстановление пароля (опционально)
    # path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    # path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),


    path('rent/', include('api.rent.api_urls', namespace='rent_api')),
    path('expenses/', include('api.expenses.api_urls', namespace='expenses_api')),
    # path('work/', include('work.api_urls', namespace='work_api')),
    # path('electricity/', include('electricity.api_urls', namespace='electricity_api')),
]