import pytest
from faker import Faker

from role_based_app.users.domain.entities.user import (
    UserDtoIn,
    UserLoginDto,
    UserRole,
    UserNewPasswordDto,
)

faker = Faker()


@pytest.fixture
def user_factory():
    def _factory(**kwargs):
        args = {
            **{
                "id": faker.uuid4(),
                "first_name": faker.text(15),
                "last_name": faker.text(15),
                "password": faker.random_number(digits=15),
                "email": faker.email(),
                "roles": fake_user_rol(),
                "phone_number": str(faker.random_number(digits=15)),
                "password_confirmation": faker.random_number(digits=15),
                "is_verified": False,
                "is_enabled": True,
            },
            **kwargs,
        }
        return UserDtoIn(**args)

    return _factory


@pytest.fixture
def user_login_factory():
    def _factory(**kwargs):
        args = {
            **{
                "email": faker.email(),
                "phone_number": faker.uuid4(),
                "password": faker.random_number(digits=15),
            },
            **kwargs,
        }
        return UserLoginDto(**args)

    return _factory


@pytest.fixture(name="user_new_password_factory")
def user_new_password_factory():
    def _factory(**kwargs):
        new_password = faker.random_number(digits=15)
        args = {
            **{
                "phone_number": faker.random_number(digits=10),
                "email": faker.email(),
                "password": faker.random_number(digits=15),
                "new_password": new_password,
                "new_password_confirmation": new_password,
            },
            **kwargs,
        }
        return UserNewPasswordDto(**args)

    return _factory


def fake_user_rol() -> UserRole:
    def _user_rol(**kwargs):
        args = {
            **{
                "is_chef": faker.boolean(),
                "is_customer": faker.boolean(),
                "is_waiter": faker.boolean(),
                "is_cashier": faker.boolean(),
                "is_delivery": faker.boolean(),
                "is_owner": faker.boolean(),
                "is_admin": faker.boolean(),
            },
            **kwargs,
        }
        return UserRole(**args)

    return _user_rol
