from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from rent.models import Tokens


class TokenBackend(BaseBackend):
    def authenticate(self, request, token=None, **kwargs):
        try:
            user = Tokens.get_user_by_token(token)
            return user
        except User.DoesNotExist:
            return None
