import uuid
import datetime
from sqlalchemy import Column, VARCHAR, DateTime, Boolean, JSON
from sqlalchemy_utils import UUIDType, EmailType, PasswordType
from sqlalchemy_utils.types.phone_number import PhoneNumberType
from role_based_app.shared.infrastructure.postgresql.setting import base


class User(base):
    __tablename__ = "user"

    id = Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name = Column(VARCHAR(100), nullable=False)
    last_name = Column(VARCHAR(20), nullable=False)
    email = Column(EmailType, nullable=True)
    phone_number = Column(PhoneNumberType(), nullable=False)
    password = Column(
        PasswordType(
            schemes=["pbkdf2_sha512", "md5_crypt"],
            deprecated=["md5_crypt"],
        ),
        nullable=False,
    )
    roles = Column(JSON(), nullable=False)
    is_enabled = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    updated_at = Column(DateTime, nullable=True)
    unable_at = Column(Boolean, nullable=True)
    is_admin = Column(Boolean, default=False)
