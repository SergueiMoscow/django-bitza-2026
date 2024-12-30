from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes

from api.serializers import RegisterSerializer


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
