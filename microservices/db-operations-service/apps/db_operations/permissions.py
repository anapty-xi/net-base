from rest_framework.permissions import BasePermission

class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'user_data')
    
class IsAdminCustom(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'user_data') and request.user_data['is_staff'] == True