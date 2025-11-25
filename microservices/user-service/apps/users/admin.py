from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # Поля для поиска
    search_fields = ('email',)

    # Порядок сортировки
    ordering = ('username',)

    # Переопределяем fieldsets для формы редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Поля для формы создания нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','is_staff', 'password1', 'password2'),
        }),
    )

    # Фильтр по горизонтали для групп и разрешений
    filter_horizontal = ('groups', 'user_permissions')
