from entities.user import User
from user_gateway_protocol import UserGateway


class CreateUser:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self, username: str, password: str) -> User:
        if not username:
            raise ValueError("Username обязательное поле")
        if not password:
            raise ValueError("Password обязательное поле")

        user = User(username=username)
        return self.user_gateway.save(user)