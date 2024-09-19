from role_based_app.users.domain.entities.user import UserDtoIn, UserLoginDto
from role_based_app.users.domain.services.user_service import UserService


class UserLogin:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def execute(self, user: UserLoginDto) -> UserDtoIn:
        return self.user_service.login(user)
