from typing import Protocol, Optional
from ..entities import User

class UserGateway(Protocol):
    def save(self, user: User) -> User:
        ...
    def authenticate(self, username: str, password: str) -> Optional[User]:
        ...
    def login(self, user: User) -> Optional[User]:
        ...