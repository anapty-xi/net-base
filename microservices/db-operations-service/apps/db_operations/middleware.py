from .services import get_user_from_token
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/health/', '/admin/']:
            return self.get_response(request)
        
        auth_header: str = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            user_data = get_user_from_token(token)
            if user_data:
                request.user_data = user_data
            else:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authentication required'}, status = 401)

        response = self.get_response(request)
        return response            