from rest_framework.permissions import BasePermission

class IsAuthenticatedCustom(BasePermission):
    '''
    Проверка аутентификации на основе атрибута вставленного middleware
    '''
    def has_permission(self, request, view):
        return hasattr(request, 'user_data')
    
class IsAdminCustom(BasePermission):
    '''
    Проверка админ ли пользователь на основе атрибута вставленного middleware
    '''
    def has_permission(self, request, view):
        return hasattr(request, 'user_data') and request.user_data['is_staff'] == True