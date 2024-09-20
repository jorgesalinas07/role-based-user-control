from operator import itemgetter
from faker import Faker
import pytest
from role_based_app.users.domain.exceptions.invalid_credentials_error import (
    InvalidCredentialsError,
)
from role_based_app.users.domain.exceptions.invalid_password_error import (
    InvalidPasswordError,
)
from role_based_app.users.domain.exceptions.invalid_token_error import InvalidTokenError

from role_based_app.users.domain.exceptions.not_active_account_error import (
    NotActiveAccountError,
)

from role_based_app.users.domain.services.user_service import (
    # EMAIL_MESSAGE,
    EXP_TOKEN_SIGNUP_HOURS,
    SIGNUP_TOKEN_TYPE,
    UserService,
)

faker = Faker()


@pytest.fixture(name="dependencies")
def _service_dependencies(mocker):
    user_repository = mocker.Mock()
    phone_message_repository = mocker.Mock()
    email_message_repository = mocker.Mock()
    token_authentication_repository = mocker.Mock()
    ot_password_repository = mocker.Mock()
    user_service = UserService(
        user_repository=user_repository,
        phone_message_repository=phone_message_repository,
        email_message_repository=email_message_repository,
        token_authentication_repository=token_authentication_repository,
        ot_password_repository=ot_password_repository,
    )
    return {
        "user_repository": user_repository,
        "phone_message_repository": phone_message_repository,
        "email_message_repository": email_message_repository,
        "token_authentication_repository": token_authentication_repository,
        "ot_password_repository": ot_password_repository,
        "service": user_service,
    }


def test__password_validator_returns_true_when_valid_password(dependencies, user_factory):
    service = itemgetter("service")(dependencies)
    password = faker.random_int()
    user = user_factory(password=password, password_confirmation=password)

    result = service.password_validator(user)

    assert result is True


def test__password_validator_raise_invalid_password_when_passwords_dont_match(
    dependencies, user_factory
):
    service = itemgetter("service")(dependencies)

    user = user_factory()

    with pytest.raises(InvalidPasswordError):
        service.password_validator(user)


def test_gen_verification_token_was_called_correctly(dependencies, user_factory):
    service = itemgetter("service")(dependencies)
    token_authentication_repository = itemgetter("token_authentication_repository")(dependencies)
    user = user_factory()
    payload = {
        "user_id": str(user.id),
        "exp": EXP_TOKEN_SIGNUP_HOURS,
        "type": "email_confirmation",
    }
    service.gen_verification_token(user, "email_confirmation", EXP_TOKEN_SIGNUP_HOURS)
    token_authentication_repository.gen_verification_token.assert_called_with(payload)


def test_send_phone_message_code_was_called_correctly_in_phone_auth_allowed_environment(
    dependencies, mocker, user_factory, monkeypatch
):
    monkeypatch.setenv("ENVIRONMENT", "production")

    service = itemgetter("service")(dependencies)
    phone_message_repository = itemgetter("phone_message_repository")(dependencies)
    ot_password_repository = itemgetter("ot_password_repository")(dependencies)
    otp = "123456"
    ot_password_repository.get_otp = mocker.Mock(return_value=otp)
    user = user_factory(email=None, phone_number=Faker().random_number(digits=15))
    service.send_phone_message_code(user)
    phone_message_repository.send_phone_message_code.assert_called_once_with(
        user.phone_number, otp
    )


def test_send_phone_message_code_was_not_called_when_test_environment_on(
    dependencies,
    mocker,
    user_factory,
):

    service = itemgetter("service")(dependencies)
    phone_message_repository = itemgetter("phone_message_repository")(dependencies)
    ot_password_repository = itemgetter("ot_password_repository")(dependencies)
    otp = "123456"
    ot_password_repository.get_otp = mocker.Mock(return_value=otp)
    user = user_factory(email=None, phone_number=Faker().random_number(digits=15))
    service.send_phone_message_code(user)
    phone_message_repository.send_phone_message_code.assert_not_called()


def test_login_raises_invalid_credentials_error(dependencies, mocker, user_login_factory):
    service = itemgetter("service")(dependencies)
    user_repository = itemgetter("user_repository")(dependencies)
    user = user_login_factory()
    empty_user = None
    user_repository.get_by_email = mocker.Mock(return_value=empty_user)

    with pytest.raises(InvalidCredentialsError):
        service.login(user)


def test_login_raises_not_active_account_error(dependencies, mocker, user_factory):
    user_repository = itemgetter("user_repository")(dependencies)
    service = itemgetter("service")(dependencies)
    user = user_factory(phone_number=faker.random_number(digits=15), is_verified=False, email=None)
    user_repository.get_by_phone_number = mocker.Mock(return_value=user)

    with pytest.raises(NotActiveAccountError):
        service.login(user)


def test_login_returns_token_when_valid_credentials_active_account_and_correct_password(
    dependencies, mocker, user_login_factory, user_factory
):
    user_repository = itemgetter("user_repository")(dependencies)
    service = itemgetter("service")(dependencies)
    user_login = user_login_factory()
    user = user_factory(is_verified=True)
    service._is_correct_password = mocker.Mock(return_value=True)
    token_authentication_repository = itemgetter("token_authentication_repository")(dependencies)
    user_repository.get_by_email = mocker.Mock(return_value=user)

    token = faker.uuid4()

    token_authentication_repository.gen_verification_token = mocker.Mock(return_value=token)

    result = service.login(user_login)

    assert result == token


def test_validate_code_raises_invalid_token_when_type_is_not_email_confirmation(
    dependencies, mocker
):
    service = itemgetter("service")(dependencies)
    token_authentication_repository = itemgetter("token_authentication_repository")(dependencies)
    payload = {
        "user_id": "user.id",
        "exp": EXP_TOKEN_SIGNUP_HOURS,
        "type": "not_email_confirmation",
    }
    token_authentication_repository.validate_code = mocker.Mock(return_value=payload)

    with pytest.raises(InvalidTokenError):
        service.validate_code(payload)


def test_validate_code_returns_true_when_successful_authentication_completed(
    dependencies, mocker, user_factory
):
    service = itemgetter("service")(dependencies)
    token_authentication_repository = itemgetter("token_authentication_repository")(dependencies)
    user_repository = itemgetter("user_repository")(dependencies)
    user = user_factory()
    user_authenticated = user_factory(is_verified=True)
    payload = {
        "user_id": "user.id",
        "exp": EXP_TOKEN_SIGNUP_HOURS,
        "type": SIGNUP_TOKEN_TYPE,
    }
    token_authentication_repository.validate_code = mocker.Mock(return_value=payload)
    user_repository.get_by_id = mocker.Mock(return_value=user)
    user_repository.update = mocker.Mock(return_value=user_authenticated)

    result = service.validate_code(payload)

    assert result is True


def test_is_correct_password_returns_true_when_correct_password_provided(dependencies):
    provided_password = "12345"
    stored_password = "12345"

    service = itemgetter("service")(dependencies)

    result = service._is_correct_password(provided_password, stored_password)

    assert result is True


def test_is_correct_password_raises_invalid_credentials_error_when_incorrect_password_provided(
    dependencies,
):
    provided_password = "1234"
    stored_password = "12345"

    service = itemgetter("service")(dependencies)

    with pytest.raises(InvalidCredentialsError):
        service._is_correct_password(provided_password, stored_password)


def test_save_new_password_returns_user_data_when_request_body_was_correct(
    dependencies,
    mocker,
    user_factory,
    user_new_password_factory,
):
    password = faker.random_number(digits=15)
    new_password = faker.random_number(digits=15)
    email = faker.email()

    user_new_password = user_new_password_factory(
        email=email,
        password=password,
        new_password=new_password,
        new_password_confirmation=new_password,
    )
    user = user_factory(
        email=email,
        password=password,
        is_verified=True,
    )
    service = itemgetter("service")(dependencies)
    user_repository = itemgetter("user_repository")(dependencies)
    user_repository.get_by_email = mocker.Mock(return_value=user)
    result = service.save_new_password(user_new_password)

    assert result["phone_number"] == user.phone_number
    assert result["email"] == user.email
    assert result["roles"] == user.roles
    assert result["first_name"] == user.first_name
    assert result["last_name"] == user.last_name
    assert result["is_verified"] == user.is_verified


@pytest.mark.parametrize(
    "password, password_provided, new_password, new_password_confirmation",
    [
        ("123", "123", "1234", "123"),
        ("123", "123", "123", "1234"),
        ("123", "1234", "123", "123"),
        ("1234", "123", "123", "123"),
    ],
)
def test_save_new_password_raise_an_error_when_request_body_was_incorrect(
    password,
    password_provided,
    new_password,
    new_password_confirmation,
    dependencies,
    mocker,
    user_factory,
    user_new_password_factory,
):
    email = faker.email()

    user_new_password = user_new_password_factory(
        email=email,
        password=password_provided,
        new_password=new_password,
        new_password_confirmation=new_password_confirmation,
    )
    user = user_factory(
        email=email,
        password=password,
        is_verified=True,
    )
    service = itemgetter("service")(dependencies)
    user_repository = itemgetter("user_repository")(dependencies)
    user_repository.get_by_email = mocker.Mock(return_value=user)
    with pytest.raises(InvalidCredentialsError):
        service.save_new_password(user_new_password)


def test_send_phone_message_code_returns_true_when_phone_number_exists(
    dependencies, mocker, user_factory
):
    service = itemgetter("service")(dependencies)
    phone_message_repository = itemgetter("phone_message_repository")(dependencies)
    user = user_factory(phone_number=Faker().random_number(digits=15))
    phone_message_repository.send_phone_message_code = mocker.Mock(return_value=True)

    assert service.send_phone_message_code(user) is True
