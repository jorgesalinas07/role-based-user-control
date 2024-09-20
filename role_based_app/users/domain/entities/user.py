import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, UUID4, BaseModel
import pydantic


class UserLoginDto(BaseModel):
    phone_number: Optional[str]
    email: Optional[EmailStr]
    password: str = Field(max_length=20)

    @pydantic.validator("email", pre=True, always=True)
    @classmethod
    def default_email(cls, value):
        return value or None


class UserNewPasswordDto(BaseModel):
    phone_number: Optional[str]
    email: Optional[EmailStr]
    password: str = Field(max_length=20)
    new_password: str = Field(max_length=20)
    new_password_confirmation: str = Field(max_length=20, exclude=True)

    @pydantic.validator("email", pre=True, always=True)
    @classmethod
    def default_email(cls, value):
        return value or None


class UserRole(BaseModel):
    is_chef: bool = False
    is_customer: bool = False
    is_waiter: bool = False
    is_cashier: bool = False
    is_delivery: bool = False
    is_owner: bool = True
    is_admin: bool = False

    class Config:
        orm_mode = True


class BaseUserDto(BaseModel):
    phone_number: str
    email: Optional[EmailStr]
    roles: UserRole
    id: UUID4 = str(uuid.uuid4())
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    is_verified: Optional[bool] = False

    @pydantic.validator("email", pre=True, always=True)
    @classmethod
    def default_email(cls, value):
        return value or None

    @pydantic.validator("phone_number", pre=True, always=True)
    @classmethod
    def default_phone_number(cls, value):
        return value or None

    class Config:
        orm_mode = True


class UserDtoIn(BaseUserDto):
    password: str = Field(max_length=20)
    password_confirmation: str = Field(max_length=20, exclude=True)


class UserDtoOut(BaseUserDto):
    created_at: datetime = None
    updated_at: datetime = None
    unable_at: datetime = None
    is_enabled: bool = True
    is_admin: bool = False


class UserAdminDtoIn(UserDtoIn):  # Model used to create a user with admin role
    is_admin: Optional[bool] = False
