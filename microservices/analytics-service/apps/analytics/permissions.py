from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    '''
    Проверка аутентификации на основе атрибута вставленного middleware
    '''
    def has_permission(self, request, view):
        return hasattr(request, 'user_data')