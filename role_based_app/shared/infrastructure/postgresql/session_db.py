from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from role_based_app.shared.infrastructure.postgresql import _config


class SessionDb:
    _session = None
    connection_db_string = _config.load_config().DB_CONNECTION_STRING

    def __new__(cls, *args, **kwargs):
        if not cls._session:
            db = create_engine(cls.connection_db_string)
            Session = sessionmaker(db)
            cls._session = Session()
        return cls._session
