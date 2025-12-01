from typing import Optional
from ..entities.user import User
from .user_gateway_protocol import LoginUserProtocol as UserGateway

class LoginUser:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self, username: str, password: str) -> Optional[User]:
        if not username:
            raise ValueError('Username is required')
        
        if not password:
            raise ValueError('Password is required')
        
        authenticated_user = self.user_gateway.authenticate(username=username, password=password)
        if not authenticated_user:
            return None
        
        if not authenticated_user.is_active:
            return None
        
        if self.user_gateway.login(authenticated_user):
            return authenticated_user
        return None