from django.contrib.auth import authenticate
from ..entities.user import User
from typing import Optional, Tuple
from ..models import User as DjangoUser
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

class JWTAuthentication:
    def authenticate(self, username: str, password: str) -> Optional[User]:
        django_user = authenticate(username=username, password=password)
        if not django_user:
            return None
        
        return User(
        id=django_user.id,
        username=django_user.username,
        is_active=django_user.is_active,
        is_staff=django_user.is_staff,
        created_at=django_user.created_at,
        updated_at=django_user.updated_at
        )
    

    def login(self, user: User) -> Optional[User]:
        if user.is_active:
            return True
        return False


    def create_tokens(self, user: User) -> Tuple[str, str]:
        django_user = DjangoUser.objects.get(id=user.id)
        tokens = RefreshToken.for_user(django_user)
        return str(tokens), str(tokens.access_token)

    def get_access_token(self, refresh: str) -> str | Exception:
        '''получение access токена по refresh'''
        return str(RefreshToken(refresh).access_token)

