from typing import Protocol, Optional, Tuple
from ..entities.user import User

class LoginUserProtocol(Protocol):        
    def authenticate(self, username: str, password: str) -> Optional[User]:
        ...
    def login(self, user: User) -> bool:
        ...

class CreateTokensProtocol(Protocol):
    def create_tokens(self, user: User) -> Tuple[str, str]:
        ...

class RefreshTokenProtocol(Protocol):
    def get_access_token(self, refresh_token: str) -> str | Exception:
        ...