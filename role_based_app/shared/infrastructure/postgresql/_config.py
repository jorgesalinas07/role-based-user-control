import typing
import os
from role_based_app.shared.infrastructure.postgresql.setting import db_string
from role_based_app.shared.infrastructure.postgresql.setting import db_test_string


class Config(typing.NamedTuple):
    DB_CONNECTION_STRING: str


def load_config():
    if os.environ.get("ENVIRONMENT") == "test":
        return Config(db_test_string)

    return Config(db_string)
