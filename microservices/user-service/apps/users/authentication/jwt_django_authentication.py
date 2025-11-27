from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..entities import User
from ..models import User as DjangoUser

class JWTAuthentication:
    def autheticate(self, username: str, password: str):
        django_user = authenticate(username=username, password=password)
        if django_user:
            return User(
            id=django_user.id,
            username=django_user.username,
            is_active=django_user.is_active,
            is_staff=django_user.is_staff,
            is_superuser=django_user.is_superuser,
            created_at=django_user.created_at,
            updated_at=django_user.updated_at
        )
    
    def login(self, user: User):
        django_user = DjangoUser.objects.get(id=user.id)
        refresh = RefreshToken.for_user(django_user)
        return refresh, user