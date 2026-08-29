from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes

from api.serializers import RegisterSerializer
from rent.models import Tokens


# Регистрация пользователя (опционально)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer  # Используйте ваш сериализатор для регистрации


# Выход пользователя
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response(status=204)


class TokenLoginView(APIView):
    """
    Вход по постоянной ссылке `?token=...` (для клиента без пароля) — раньше это была
    сессионная HTML-страница (bitza/views.py::main, привязка к User через Tokens),
    здесь тот же Tokens.get_user_by_token (с привязкой к браузеру, без изменений),
    только вместо Django-сессии выдаём JWT-пару, как при обычном логине.
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        user = Tokens.get_user_by_token(request)
        if user is None:
            return Response({'detail': 'Недействительная или просроченная ссылка.'},
                             status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})
