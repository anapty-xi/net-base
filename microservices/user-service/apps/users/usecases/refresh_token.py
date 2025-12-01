from typing import Optional, Tuple
from ..entities.user import User
from .user_gateway_protocol import RefreshTokenProtocol as UserGateway

class RefreshToken:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self, refresh_token: str) -> str | Exception:
        return self.user_gateway.get_access_token(refresh_token)
