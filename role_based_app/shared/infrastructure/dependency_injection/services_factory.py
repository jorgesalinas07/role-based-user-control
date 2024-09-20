from role_based_app.users.domain.services.user_service import UserService
from role_based_app.users.infrastructure.persistance.user_repository import (
    BotoMessageRepository,
    JWTAuthenticationRepository,
    PostgresqlUserRepository,
    WhatsappMessageRepository,
    PyOTPasswordRepository,
)


def user_service_factory(session) -> UserService:
    user_repository = PostgresqlUserRepository(session)
    phone_message_repository = WhatsappMessageRepository()
    email_message_repository = BotoMessageRepository()
    token_authentication_repository = JWTAuthenticationRepository()
    ot_password_repository = PyOTPasswordRepository()
    return UserService(
        user_repository,
        phone_message_repository,
        email_message_repository,
        token_authentication_repository,
        ot_password_repository,
    )
