from role_based_app.users.domain.entities.user import UserDtoIn, UserDtoOut
from role_based_app.users.domain.services.user_service import UserService


class UserSignUp:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def execute(self, user: UserDtoIn) -> UserDtoOut:
        return self.user_service.signup(user)
