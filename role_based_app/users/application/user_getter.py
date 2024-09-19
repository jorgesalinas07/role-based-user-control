from role_based_app.users.domain.entities.user import UserDtoIn
from role_based_app.users.domain.services.user_service import UserService


class UserGetter:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def execute(self, user_id: str) -> UserDtoIn:
        return self.user_service.get(user_id)
