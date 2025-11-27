from django.contrib.auth.hashers import make_password
from ..models import User as DjangoUser
from entities.user import User as DomainUser

class DjangoUserRepository:
    def save(self, user: DomainUser) -> DomainUser:
        if user.id:
            django_user = DjangoUser.objects.get(id=user.id)
        else:
            django_user = DjangoUser(username=user.username)

        django_user.is_active = user.is_active
        django_user.is_staff = user.is_staff
        django_user.is_superuser = user.is_superuser


        if not user.id:
            django_user.set_password("temp-pass")  # будет заменён

        django_user.save()

        return DomainUser(
            id=django_user.id,
            username=django_user.username,
            is_active=django_user.is_active,
            is_staff=django_user.is_staff,
            is_superuser=django_user.is_superuser,
            created_at=django_user.created_at,
            updated_at=django_user.updated_at
        )
