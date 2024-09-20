import pytest

from role_based_app.users.domain.exceptions.invalid_credentials_error import (
    InvalidCredentialsError,
)
from role_based_app.users.infrastructure.persistance.user_repository import (
    WhatsappMessageRepository,
)


@pytest.fixture
def whatsapp_message_repository():
    return WhatsappMessageRepository()


def test__send_phone_message_code_raises_phone_number_not_provided(whatsapp_message_repository):
    with pytest.raises(InvalidCredentialsError):
        whatsapp_message_repository.send_phone_message_code(None, "123456")


def test__send_phone_message_code_raises_otp_not_provided(whatsapp_message_repository):
    with pytest.raises(InvalidCredentialsError):
        whatsapp_message_repository.send_phone_message_code("1234567890", None)
