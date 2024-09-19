from role_based_app.users.domain.entities.user import UserDtoIn
from role_based_app.users.domain.services.user_service import UserService


class UserVerification:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def execute(self, data) -> UserDtoIn:
        return self.user_service.verification(data)
