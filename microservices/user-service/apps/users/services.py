from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


def authenticate(username: str, password: str) -> User | None:
    '''аутентификация пользователя'''
    return authenticate(usertname=username, password=password)

def get_tokens_for_user(user: User) -> RefreshToken | None:
    '''получение токенов для пользователя'''
    if user and user.is_active:
        return RefreshToken.for_user(user)
    return None

def get_access_by_refresh(refresh: str) -> str | Exception:
    '''получение access токена по refresh'''
    return RefreshToken(refresh).access_token