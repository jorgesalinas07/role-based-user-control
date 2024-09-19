from faker import Faker
import pytest
from role_based_app.shared.infrastructure.postgresql import _config
from sqlalchemy import create_engine
from role_based_app.shared.infrastructure.postgresql.session_db import SessionDb

connection_db_string = _config.load_config().DB_CONNECTION_STRING

engine = create_engine(connection_db_string)
Session = SessionDb
faker = Faker()


@pytest.fixture(name="test_db")
def _test_db() -> SessionDb:
    db_fake = SessionDb()
    return db_fake


@pytest.fixture(name="session_mock")
def _session_mock(mocker):
    session_mock = mocker.Mock()
    mocker.patch(
        "role-based_app.shared.infrastructure.postgresql.session_db.SessionDb.__new__",
        return_value=session_mock,
    )
    return session_mock


@pytest.fixture()
def connection():
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def session(connection):
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
