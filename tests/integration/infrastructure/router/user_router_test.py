from faker import Faker
from fastapi.testclient import TestClient
from role_based_app.main import app
import pytest
from role_based_app.users.domain.services.user_service import (
    EXP_TOKEN_LOGIN_HOURS,
    LOGIN_TOKEN_TYPE,
)
from role_based_app.users.infrastructure.persistance.user_repository import (
    JWTAuthenticationRepository,
)

client = TestClient(app)
faker = Faker()


def user_sign_up_payload(
    password_confirmation="1234",
    phone_number=str(faker.random_number(digits=15)),
    is_verified=False,
):
    def _factory():
        return {
            "phone_number": phone_number,
            "email": faker.email(),
            "password": "1234",
            "roles": {
                "is_chef": faker.boolean(),
                "is_customer": faker.boolean(),
                "is_waiter": faker.boolean(),
                "is_cashier": faker.boolean(),
                "is_delivery": faker.boolean(),
                "is_owner": faker.boolean(),
                "is_admin": faker.boolean(),
            },
            "id": faker.uuid4(),
            "first_name": faker.text(15),
            "last_name": faker.text(15),
            "is_verified": is_verified,
            "password_confirmation": password_confirmation,
            "is_admin": False,
        }

    return _factory()


@pytest.mark.parametrize(
    "user_payload, expected_exception, environment",
    [
        (
            user_sign_up_payload(is_verified=True),
            None,
            "debug",
        ),
        (
            {
                "id": faker.uuid4(),
                "first_name": faker.text(15),
                "last_name": faker.text(15),
                "is_verified": False,
                "password_confirmation": "1234",
            },
            422,
            "stage",
        ),
        (
            user_sign_up_payload(password_confirmation="12345"),
            400,
            None,
        ),
        (
            user_sign_up_payload(phone_number=None),
            422,
            None,
        ),
    ],
)
def test_sign_up(user_payload, expected_exception, environment, monkeypatch):
    if environment:
        monkeypatch.setenv("ENVIRONMENT", environment)
    user = user_payload
    response = client.post("/user/signup", json=user)
    if expected_exception:
        assert response.status_code == expected_exception
    else:
        user.pop("password_confirmation")
        user.pop("password")
        user["updated_at"] = None
        user["unable_at"] = None
        user["is_enabled"] = True
        user["is_admin"] = False
        assert response.status_code == 200
        response_json = response.json()
        response_json["body"].pop("created_at", None)
        assert response_json == {
            "statusCode": 201,
            "message": "User created successfully",
            "body": user,
        }


@pytest.mark.parametrize(
    "phone_number, email, password, expected_exception",
    [
        (
            str(faker.random_number(digits=15)),
            None,
            "1234",
            None,
        ),
        (
            None,
            faker.email(),
            "1234",
            None,
        ),
        (
            str(faker.random_number(digits=15)),
            None,
            "",
            400,
        ),
    ],
)
def test_login(
    phone_number,
    email,
    password,
    user_login_factory,
    create_fake_user,
    expected_exception,
):
    phone_number_back_up = str(faker.random_number(digits=15))
    user_created = create_fake_user(
        phone_number=phone_number if phone_number else phone_number_back_up,
        email=email,
        password=password if password else "12345",
        is_verified=True,
    )
    user = user_login_factory(
        phone_number=phone_number,
        email=email,
        password=password,
    )
    response = client.post("/user/login", json=user.__dict__)
    if expected_exception:
        assert response.status_code == expected_exception
    else:
        payload = {
            "user_id": str(user_created.id),
            "exp": EXP_TOKEN_LOGIN_HOURS,
            "type": LOGIN_TOKEN_TYPE,
        }
        token_repository = JWTAuthenticationRepository()
        token = token_repository.gen_verification_token(payload)
        assert response.status_code == 200
        assert response.json() == {
            "statusCode": 200,
            "message": "Login successfully",
            "body": token,
        }


def test__home_returns_message_when_valid_token():
    payload = {
        "user_id": "1234",
        "exp": EXP_TOKEN_LOGIN_HOURS,
        "type": LOGIN_TOKEN_TYPE,
    }
    token_repository = JWTAuthenticationRepository()
    token = token_repository.gen_verification_token(payload)
    response = client.get(
        "/user/healthy-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"healthy-check": "healthy"}


def test__home_raises_exception_when_invalid_token():
    payload = {
        "user_id": "1234",
        "exp": EXP_TOKEN_LOGIN_HOURS,
        "type": "wrong_token_type",
    }
    token_repository = JWTAuthenticationRepository()
    token = token_repository.gen_verification_token(payload)
    response = client.get(
        "/user/healthy-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid authentication token"}


def test__user_new_password_return_user_data_on_success(
    create_fake_user,
    user_login_factory,
):
    common_payload = {
        "phone_number": "0987654321",
        "email": "jon_doe@gmail.com",
        "password": "old_password",
    }
    payload = {
        **common_payload,
        "new_password": "new_password",
        "new_password_confirmation": "new_password",
    }
    user = create_fake_user(**common_payload, is_verified=True)
    user_login_dto = user_login_factory(**common_payload)
    response_login = client.post("/user/login", json=user_login_dto.__dict__)
    token = response_login.json().get("body")
    response = client.post(
        "/user/new_password", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    json_response = response.json()
    response_body = json_response["body"]
    assert response.status_code == 200
    assert json_response["message"] == "Password changed successfully"
    assert response_body["last_name"] == user.last_name
    assert response_body["first_name"] == user.first_name
    assert response_body["email"] == user.email
    assert response_body["roles"] == user.roles
    assert response_body["is_verified"] == user.is_verified
    assert response_body["roles"] == user.roles
