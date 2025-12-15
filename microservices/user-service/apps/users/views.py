import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from .serializers import UserSerializer
from .usecases.login_user import LoginUser
from .usecases.create_token import CreateTokens
from .usecases.refresh_token import RefreshToken
from .infrastructure.jwt_django_authentication import JWTAuthentication

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
    auth_infrastructure = JWTAuthentication()
    user = LoginUser(auth_infrastructure).execute(username, password)
    logger.info('User login')
    refresh, access = CreateTokens(auth_infrastructure).execute(user)
    if refresh:
        logger.info('User login')
        return Response ({
            'access': access,
            'refresh': refresh,
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
        token_infrastructure = JWTAuthentication()
        access = RefreshToken(token_infrastructure).execute(refresh_token)
        return Response ({
            'access': str(access)
        })
    except Exception as e:
        return Response (
            {'error': str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )
    

class UserView(generics.RetrieveAPIView):
    '''отправка данных пользователя, если предоставлен access токен'''
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        print(f'client got user data\n {self.request.user}')
        logger.info(f'client got user data\n {self.request.user}')
        return self.request.user