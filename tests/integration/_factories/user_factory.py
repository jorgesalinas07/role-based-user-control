import pytest
from faker import Faker
from role_based_app.users.domain.entities.user import UserRole

from role_based_app.users.infrastructure.adapters.user_schema import User

faker = Faker()


@pytest.fixture
def user_model_factory():
    def _factory(**kwargs):
        args = {
            **{
                "id": faker.uuid4(),
                "first_name": faker.text(15),
                "last_name": faker.text(15),
                "password": str(faker.random_number(digits=15)),
                "email": faker.email(),
                "roles": fake_user_rol().__dict__,
                "phone_number": str(faker.random_number(digits=15)),
                "is_verified": False,
                "is_enabled": True,
            },
            **kwargs,
        }
        return User(**args)

    return _factory


@pytest.fixture(name="create_fake_user")
def create_fake_user(session, user_model_factory) -> dict:
    def _new_user(**kwargs):
        db_session = session
        new_user = user_model_factory(**kwargs)
        db_session.add(new_user)
        db_session.commit()
        return new_user

    return _new_user


def fake_user_rol(**kwargs):
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
