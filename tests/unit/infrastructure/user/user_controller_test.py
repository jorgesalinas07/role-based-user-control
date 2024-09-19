from http import HTTPStatus
from faker import Faker
import pytest
from typing import Callable
from role_based_app.users.application.user_login import UserLogin
from role_based_app.users.application.user_new_password import UserNewPassword
from role_based_app.users.application.user_signup import UserSignUp
from role_based_app.users.domain.exceptions.internal_server_error import InternalServerError
from role_based_app.users.domain.exceptions.invalid_credentials_error import (
    InvalidCredentialsError,
)
from role_based_app.users.domain.exceptions.invalid_password_error import (
    InvalidPasswordError,
)
from role_based_app.users.domain.exceptions.not_active_account_error import (
    NotActiveAccountError,
)
from role_based_app.users.domain.exceptions.user_already_exist import UserAlreadyExist
from role_based_app.users.infrastructure.user_controller import (
    create_user,
    login,
    new_password,
)
from role_based_app.users.domain.exceptions.whatsapp_response_error import (
    WhatsappResponseError,
)


@pytest.fixture(name="mock_user_use_case")
def _user_use_case_mocked(mocker) -> Callable:
    def _user_use_case(user_DTO: any, user_use_case) -> None:
        mocker.patch(
            "role_based_app.users.infrastructure.user_controller.user_service_factory",
            return_value=mocker.Mock(),
        )
        mocker.patch.object(user_use_case, "execute", side_effect=user_DTO)

    return _user_use_case


@pytest.mark.usefixtures("session_mock")
def test__create_user_returns_successful_response_when_user_is_created(
    mock_user_use_case,
    user_factory,
    mocker,
):
    user = user_factory()
    mock_user_use_case(mocker.Mock(return_value=user), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.CREATED
    assert result["body"] == user


# TODO: Update HTTPStatus in tests when decided


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_bad_request_error_when_user_already_exist(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(UserAlreadyExist("user_name"), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_bad_request_error_when_internal_server_error(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(InternalServerError("something happened"), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_bad_request_error_when_internal_server_error_(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(InvalidPasswordError(), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_internal_server_error_error_when_general_exception(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(Exception(), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_internal_server_error_error_when_base_exception(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(BaseException(), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("session_mock")
def test__create_user_return_internal_server_error_when_whatsapp_response_error(
    mock_user_use_case,
    user_factory,
):
    user = user_factory()
    mock_user_use_case(WhatsappResponseError(), UserSignUp)

    result = create_user(user)
    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("session_mock")
def test__login_user_returns_successful_response_when_user_is_logged(
    mock_user_use_case,
    user_login_factory,
    mocker,
):
    user = user_login_factory()
    token = Faker().uuid4()
    mock_user_use_case(mocker.Mock(return_value=token), UserLogin)

    result = login(user)
    assert result["statusCode"] == HTTPStatus.OK
    assert result["body"] == token


@pytest.mark.usefixtures("session_mock")
def test__login_user_return_bad_request_error_when_user_already_exist(
    mock_user_use_case,
    user_login_factory,
):
    user = user_login_factory()
    mock_user_use_case(NotActiveAccountError(), UserLogin)

    result = login(user)
    assert result["statusCode"] == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("session_mock")
def test__login_user_return_bad_request_error_when_internal_server_error(
    mock_user_use_case,
    user_login_factory,
):
    user = user_login_factory()
    mock_user_use_case(InternalServerError("Something went wrong"), UserLogin)

    result = login(user)
    assert result["statusCode"] == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures("session_mock")
def test__login_user_return_internal_server_error_error_when_general_exception(
    mock_user_use_case,
    user_login_factory,
):
    user = user_login_factory()
    mock_user_use_case(Exception(), UserLogin)

    result = login(user)
    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("session_mock")
def test__login_user_return_internal_server_error_error_when_base_exception(
    mock_user_use_case,
    user_login_factory,
):
    user = user_login_factory()
    mock_user_use_case(BaseException(), UserLogin)

    result = login(user)
    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.usefixtures("session_mock")
def test__user_new_password_returns_successful_response_when_user_is_logged(
    mock_user_use_case,
    user_new_password_factory,
    user_factory,
    mocker,
):
    user_new_password = user_new_password_factory()
    response = user_factory()
    mock_user_use_case(mocker.Mock(return_value=response), UserNewPassword)

    result = new_password(user_new_password)
    assert result["statusCode"] == HTTPStatus.OK
    assert result["body"] == response


@pytest.mark.parametrize(
    "exception, status_code",
    [
        (NotActiveAccountError(), HTTPStatus.BAD_REQUEST),
        (InvalidCredentialsError(), HTTPStatus.BAD_REQUEST),
        (NotImplementedError(), HTTPStatus.BAD_REQUEST),
        (InternalServerError("something happened"), HTTPStatus.BAD_REQUEST),
        (Exception(), HTTPStatus.INTERNAL_SERVER_ERROR),
        (BaseException(), HTTPStatus.INTERNAL_SERVER_ERROR),
    ],
)
@pytest.mark.usefixtures("session_mock")
def test__user_new_password_return_error_when_use_case_raises_an_exception(
    exception,
    status_code,
    mock_user_use_case,
    user_login_factory,
):
    user = user_login_factory()
    mock_user_use_case(exception, UserNewPassword)

    result = new_password(user)
    assert result["statusCode"] == status_code
