from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):

    def create_user(self, username, password=None):
        if username is None:
            raise TypeError('Пользователь должен иметь юзернейм')

        if password is None:
            raise TypeError('Пользователь должен иметь пароль')

        user = self.model(username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):

        if username is None:
            raise TypeError('Пользователь должен иметь юзернейм')

        if password is None:
            raise TypeError('Суперпользователь должен иметь пароль')

        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
    


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    objects = UserManager()

    def __str__(self):
        return self.username
