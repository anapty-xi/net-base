from django.http import JsonResponse
import requests
from django.conf import settings

class JWTAuthenticationMiddleware:
    '''
    Middleware для проверки токена пользователя. Встраивает в request данные пользователя для views
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/health/', '/admin/']:
            return self.get_response(request)
        
        auth_header: str = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                user_data = requests.get(f'{settings.USER_SERVICE_URL}/user/user/',
                                          headers={'Authorization': f'Bearer {token}'}, 
                                          timeout=5)
                request.user_data = user_data
            except:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authentication required'}, status = 401)

        response = self.get_response(request)
        return response  