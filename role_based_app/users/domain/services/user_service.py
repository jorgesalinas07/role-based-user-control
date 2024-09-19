import typing
import os
from datetime import timedelta, datetime
from sqlalchemy_utils import PasswordType

from role_based_app.users.domain.entities.user import (
    UserDtoIn,
    UserLoginDto,
    UserNewPasswordDto,
)
from role_based_app.users.domain.exceptions.invalid_credentials_error import (
    InvalidCredentialsError,
)
from role_based_app.users.domain.exceptions.invalid_password_error import (
    InvalidPasswordError,
)
from role_based_app.users.domain.exceptions.invalid_token_error import InvalidTokenError
from role_based_app.users.domain.exceptions.not_active_account_error import (
    NotActiveAccountError,
)
from role_based_app.users.domain.exceptions.user_already_exist import UserAlreadyExist
from role_based_app.users.domain.exceptions.phone_number_not_provided import (
    PhoneNumberNotProvided,
)
from role_based_app.users.domain.repositories.user_repository import (
    EmailMessageRepository,
    PhoneMessageRepository,
    TokenAuthenticationRepository,
    UserRepository,
    OTPasswordRepository,
)

EMAIL_MESSAGE = "Hola"
EXP_TOKEN_SIGNUP_HOURS = datetime.now() + timedelta(hours=0.5)
EXP_TOKEN_LOGIN_HOURS = datetime.now() + timedelta(hours=24)
LOGIN_TOKEN_TYPE = "user_login"
SIGNUP_TOKEN_TYPE = "user_confirmation"
PHONE_MESSAGE_AUTHENTICATION_ALLOWED_ENVIRONMENTS = [
    "stage",
    "production",
]


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        phone_message_repository: PhoneMessageRepository,
        email_message_repository: EmailMessageRepository,
        token_authentication_repository: TokenAuthenticationRepository,
        ot_password_repository: OTPasswordRepository,
    ):
        self.user_repository = user_repository
        self.phone_message_repository = phone_message_repository
        self.email_message_repository = email_message_repository
        self.token_authentication_repository = token_authentication_repository
        self.ot_password_repository = ot_password_repository

    def signup(self, user: UserDtoIn):
        self.password_validator(user)
        if user.phone_number and self.user_repository.get_by_phone_number(
            phone_number=user.phone_number
        ):
            raise UserAlreadyExist(user.first_name)
        if (
            os.environ.get("ENVIRONMENT") not in
            PHONE_MESSAGE_AUTHENTICATION_ALLOWED_ENVIRONMENTS
        ):
            user = UserDtoIn(**{**user.__dict__, "is_verified": True})
        user = self.user_repository.create(user)
        return user

    def password_validator(self, user: UserDtoIn):
        password = user.password
        password_confirmation = user.password_confirmation
        if password != password_confirmation:
            raise InvalidPasswordError()
        return True

    def send_phone_message_code(self, user: UserDtoIn):
        if (
            os.environ.get("ENVIRONMENT") in
            PHONE_MESSAGE_AUTHENTICATION_ALLOWED_ENVIRONMENTS
        ):
            otp = self.ot_password_repository.get_otp(phone_number=user.phone_number)
            if (user.phone_number and otp):
                self.phone_message_repository.send_phone_message_code(
                    user.phone_number, otp
                )
                return True
            raise PhoneNumberNotProvided()
        return True

    def gen_verification_token(
        self, user: UserDtoIn, type_token: str, exp_hour: datetime
    ) -> str:
        payload = {
            "user_id": str(user.id),
            "exp": exp_hour,
            "type": type_token,
        }
        return self.token_authentication_repository.gen_verification_token(payload)

    def login(self, user: UserLoginDto):
        user_ref = self._get_user_ref(user)
        if self._is_correct_password(user.password, user_ref.password):
            token = self.gen_verification_token(
                user_ref, LOGIN_TOKEN_TYPE, EXP_TOKEN_LOGIN_HOURS
            )
            return token

    def _is_correct_password(
        self, provided_password: str, stored_password: PasswordType
    ):
        if provided_password == stored_password:
            return True
        raise InvalidCredentialsError()

    def validate_code(self, data):
        payload = self.token_authentication_repository.validate_code(data)
        if payload["type"] != SIGNUP_TOKEN_TYPE:
            raise InvalidTokenError()
        user = self.user_repository.get_by_id(user_id=payload["user_id"])
        if user:
            user.is_verified = True
            self.user_repository.update(user_id=user.id, user=user)
            return True
        raise InvalidCredentialsError("User not recognized")

    def _get_user_ref(self, user: typing.Union[UserLoginDto, UserNewPasswordDto]):
        user_ref = None
        if user.email:
            user_ref = self.user_repository.get_by_email(email=user.email)
        else:
            user_ref = self.user_repository.get_by_phone_number(
                phone_number=user.phone_number
            )

        if not user_ref:
            raise InvalidCredentialsError()
        if not user_ref.is_verified:
            raise NotActiveAccountError()

        return user_ref

    def _get_user_response(self, user: UserDtoIn):
        return {
            "phone_number": str(user.phone_number),
            "email": user.email,
            "roles": user.roles,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_verified": user.is_verified,
        }

    def save_new_password(self, user: UserNewPasswordDto):
        user_ref = self._get_user_ref(user)
        self._is_correct_password(user.password, user_ref.password)
        self._is_correct_password(user.new_password, user.new_password_confirmation)
        user_ref.password = user.new_password
        self.user_repository.update(user_ref.id, user_ref)
        return self._get_user_response(user_ref)

    def get(self):
        return []
