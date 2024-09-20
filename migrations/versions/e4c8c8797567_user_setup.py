"""User setup

Revision ID: e4c8c8797567
Revises:
Create Date: 2023-05-06 16:41:55.826751

"""

import uuid

from alembic import op
from sqlalchemy_utils.types.phone_number import PhoneNumberType
from sqlalchemy import JSON, VARCHAR, TIMESTAMP, Boolean, Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType, PasswordType
# revision identifiers, used by Alembic.
revision = 'e4c8c8797567'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    #Add comments to db fields
    op.create_table(
        "user",
        Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment=""),
        Column("first_name", VARCHAR(20), nullable=False),
        Column("last_name", VARCHAR(20), nullable=False),
        Column("email", EmailType),
        Column("phone_number", PhoneNumberType, nullable=False),
        Column("password", PasswordType, nullable=False),
        Column("roles", JSON, nullable=False),
        Column("is_verified", Boolean),
        Column("created_at", TIMESTAMP),
        Column("updated_at", TIMESTAMP),
        Column("is_enabled", Boolean),
        Column("unable_at", TIMESTAMP),
        Column("is_admin", Boolean),
    )


def downgrade() -> None:
    pass
