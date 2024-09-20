import jwt
import pytest
from role_based_app.shared.infrastructure.postgresql.session_db import SessionDb
from role_based_app.users.domain.exceptions.internal_server_error import InternalServerError
from role_based_app.users.domain.exceptions.invalid_token_error import InvalidTokenError
from role_based_app.users.domain.exceptions.token_expired_error import TokenExpiredError
from role_based_app.users.domain.exceptions.user_not_found import UserNotFoundError
from role_based_app.users.infrastructure.adapters.user_schema import User
from role_based_app.users.infrastructure.persistance.user_repository import (
    JWTAuthenticationRepository,
    PostgresqlUserRepository,
    BotoMessageRepository,
)
from datetime import datetime, timedelta, timezone
from faker import Faker
from dotenv import load_dotenv
import os
from os.path import join, dirname
from moto import mock_ses
from botocore.exceptions import ClientError
from role_based_app.users.domain.exceptions.invalid_message_parameter import (
    InvalidMessageParameter,
)

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")
SECRET_KEY = os.environ.get("JWT_TOKEN_SECRET_KEY")


@pytest.fixture(name="clean_user_database", autouse=True)
def _clean_user_database():
    yield
    db_fake = SessionDb()
    db_fake.query(User).delete()
    db_fake.commit()


@pytest.mark.usefixtures("session")
def test__create_user__returns_a_user(user_factory, session):
    user_repository = PostgresqlUserRepository(session)
    expected_user = user_factory()

    user = user_repository.create(expected_user)

    assert user.first_name == expected_user.first_name


@pytest.mark.usefixtures("session")
def test__create_user__raises_internal_server_error_when_database_error(
    user_factory,
    session,
):
    user_repository = PostgresqlUserRepository(session)
    not_valid_phone_number = "+5725179842315 Ext2315"
    expected_user = user_factory(phone_number=not_valid_phone_number)
    with pytest.raises(InternalServerError):
        user_repository.create(expected_user)


@pytest.mark.usefixtures("session")
def test__get_user_by_id__return_a_user(session, create_fake_user):
    id = Faker().uuid4()
    user_repository = PostgresqlUserRepository(session)

    created_user = create_fake_user(id=id)
    user = user_repository.get_by_id(id)

    assert created_user.id == user.id


@pytest.mark.usefixtures("session")
def test__get_user_by_email__return_a_user(session, create_fake_user):
    email = Faker().email()
    user_repository = PostgresqlUserRepository(session)

    created_user = create_fake_user(email=email)
    user = user_repository.get_by_email(email)

    assert created_user.email == user.email


@pytest.mark.usefixtures("session")
def test__update_user__returns_a_user_when_successfully_updated(
    session, create_fake_user, user_model_factory
):
    id = Faker().uuid4()
    email = Faker().email()
    updated_email = Faker().email()
    user = user_model_factory(id=id, email=updated_email)
    user_repository = PostgresqlUserRepository(session)

    create_fake_user(id=id, email=email)
    result = user_repository.update(user_id=id, user=user)

    assert result


@pytest.mark.usefixtures("session")
def test__update_user__raises_user_not_found_error(session, user_model_factory):
    user = user_model_factory()
    id = Faker().uuid4()
    user_repository = PostgresqlUserRepository(session)

    with pytest.raises(UserNotFoundError):
        user = user_repository.update(user_id=id, user=user)


def test__gen_verification_token__returns_token():
    repository = JWTAuthenticationRepository()
    exp_hour = 2
    user_id = Faker().uuid4()
    expected_exp = datetime.now(timezone.utc) + timedelta(hours=exp_hour)
    expected_type = "type_token"
    payload = {
        "user_id": user_id,
        "exp": expected_exp,
        "type": expected_type,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    generated_token = repository.gen_verification_token(payload)
    result = jwt.decode(generated_token, SECRET_KEY, algorithms=["HS256"])

    assert result["user_id"] == user_id
    assert result["type"] == expected_type
    assert token == generated_token
    assert result["exp"] == int(expected_exp.timestamp())


def test__validate_code_returns_payload():
    repository = JWTAuthenticationRepository()
    exp_hour = 2
    user_id = Faker().uuid4()
    expected_exp = datetime.now(timezone.utc) + timedelta(hours=exp_hour)
    expected_type = "type_token"
    payload = {
        "user_id": user_id,
        "exp": expected_exp,
        "type": expected_type,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    result = repository.validate_code(token)

    assert result["user_id"] == user_id
    assert result["type"] == expected_type
    assert result["exp"] == int(expected_exp.timestamp())


def test__validate_code_raises_token_expired_error():
    repository = JWTAuthenticationRepository()
    expected_exp = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "user_id": Faker().uuid4(),
        "exp": expected_exp,
        "type": "type_token",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    with pytest.raises(TokenExpiredError):
        repository.validate_code(token)


def test__validate_code_raises_invalid_token_email():
    repository = JWTAuthenticationRepository()
    expected_exp = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "user_id": Faker().uuid4(),
        "exp": expected_exp,
        "type": "type_token",
    }
    token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        repository.validate_code(token)


@mock_ses
def test_send_confirmation_email_returns_reponse_successfully(user_model_factory):
    repository = BotoMessageRepository()
    token = "123456"
    user = user_model_factory(email="adriana@kaumer.com")

    repository.client.verify_email_identity(EmailAddress=repository.sender)

    response = repository.send_confirmation_email(user, token)

    assert isinstance(response, dict)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert response["MessageId"] is not None
    assert response["Subject"]["Data"] == "Email Confirmation"
    assert response["Body"]["Text"]["Data"] == "This is an email confirmation message."

    sent_emails = repository.client.list_identities()
    assert user.email in sent_emails["Identities"]


@mock_ses
def test_send_confirmation_email_raises_invalid_message_parameter_when_client_error(
    mocker, user_model_factory
):
    repository = BotoMessageRepository()
    token = "123456"
    user = user_model_factory(email="adriana@role-based.com")

    error = {
        "Error": {
            "Code": "MessageRejected",
            "Message": "Email address is not verified.",
        }
    }

    send_email_mock = mocker.patch.object(
        repository.client, "send_email", side_effect=ClientError(error, "send_email")
    )

    with pytest.raises(InvalidMessageParameter):
        repository.send_confirmation_email(user, token)

    send_email_mock.assert_called_once()
