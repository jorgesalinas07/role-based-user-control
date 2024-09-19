import pytest


@pytest.fixture(name="session_mock")
def _session_mock(mocker):
    session_mock = mocker.Mock()
    mocker.patch(
        "role-based_app.shared.infrastructure.postgresql.session_db.SessionDb.__new__",
        return_value=session_mock,
    )
    return session_mock
