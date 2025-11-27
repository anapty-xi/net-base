from typing import Protocol
from ..entities.user import User
from user_gateway_protocol import UserGateway

class LoginUser:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self, username: str, password: str) -> bool:
        if not username:
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')
        
        authenticated_user = self.user_gateway.authenticate(username=username, password=password)
        if authenticated_user:
            if authenticated_user.is_active:
                return self.user_gateway.login(authenticated_user)