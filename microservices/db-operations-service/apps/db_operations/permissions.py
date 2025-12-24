import logging

from rest_framework.permissions import BasePermission
from django.conf import settings

logger= logging.getLogger(__name__)

class IsAuthenticatedCustom(BasePermission):
    '''
    Проверка аутентификации на основе атрибута вставленного middleware
    '''
    def has_permission(self, request, view):
        if hasattr(request, 'user_data'):
            return True

        api_key =  request.headers.get('X-API-Key')
        if api_key == settings.API_KEY:
            return True
        logger.error('unauth request')
        return False
    
class IsAdminCustom(BasePermission):
    '''
    Проверка админ ли пользователь на основе атрибута вставленного middleware
    '''
    def has_permission(self, request, view):
        if hasattr(request, 'user_data'):
            return request.user_data['is_staff'] == True