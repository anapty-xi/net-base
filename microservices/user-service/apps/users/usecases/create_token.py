from typing import Optional, Tuple
from ..entities.user import User
from .user_gateway_protocol import CreateTokensProtocol as UserGateway

class CreateTokens:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self, user: User) -> Tuple[str, str]:
        return self.user_gateway.create_tokens(user)