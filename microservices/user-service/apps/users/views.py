import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from .serializers import UserSerializer
from . import services

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    '''вход пользователя: отправка accsess, refresh токинов'''

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        logger.error(f'Input data is not defined')
        return Response(
            {'error': 'Юзернейм и пароль необходимы для входа'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = services.authenticate(username=username, password=password)
    logger.info('User authenticated')
    refresh = services.get_tokens_for_user(user)
    if refresh:
        logger.info('user login')
        return Response ({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
            }
        })
    logger.info(f'{username}, {password} are invalid data')
    return Response(
        {'error', 'Неверные учетные данные'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    '''отправка новых refresh, accsess токенов по refresh токену пользователя'''

    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Токен обновления обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        access = services.get_access_by_refresh(refresh_token)
        return Response ({
            'access': str(access)
        })
    except Exception as e:
        return Response (
            {'error': e},
            status=status.HTTP_401_UNAUTHORIZED
        )
    

class UserView(generics.RetrieveAPIView):
    '''отправка данных пользователя, если предоставлен access токен'''
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user