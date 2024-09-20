from role_based_app.users.domain.services.user_service import UserService
from role_based_app.users.domain.entities.user import UserDtoIn, UserNewPasswordDto


class UserNewPassword:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def execute(self, user: UserNewPasswordDto) -> UserDtoIn:
        return self.user_service.save_new_password(user)
