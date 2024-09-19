import logging
import typing
from datetime import datetime
from dotenv import load_dotenv
import jwt
import os
from os.path import join, dirname
from typing import List, Optional
import requests
from role_based_app.users.domain.exceptions.invalid_token_error import InvalidTokenError
from role_based_app.users.domain.exceptions.invalid_credentials_error import InvalidCredentialsError
from role_based_app.users.domain.exceptions.token_expired_error import TokenExpiredError
from sqlalchemy.exc import DBAPIError
from role_based_app.users.domain.exceptions.internal_server_error import InternalServerError
from role_based_app.users.domain.exceptions.user_not_found import UserNotFoundError
from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from role_based_app.users.infrastructure.adapters.user_schema import User as UserModel
from role_based_app.users.domain.entities.user import UserDtoIn, UserDtoOut, UserAdminDtoIn
from role_based_app.shared.infrastructure.facebook import _parser as whatsapp_parser
from role_based_app.users.domain.repositories.user_repository import (
    EmailMessageRepository,
    PhoneMessageRepository,
    TokenAuthenticationRepository,
    UserRepository,
    OTPasswordRepository,
)
from role_based_app.users.domain.exceptions.invalid_message_parameter import (
    InvalidMessageParameter,
)
import boto3
from botocore.exceptions import ClientError

from role_based_app.users.infrastructure.persistance.utils import (
    authentication_phone_message_template,
    parse_user_model_to_user_dto
)


load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")
JWT_TOKEN_SECRET_KEY = os.environ.get("JWT_TOKEN_SECRET_KEY")
JWT_TOKEN_ALGORITHM = os.environ.get("JWT_TOKEN_ALGORITHM")
AWS_REGION = os.environ.get("AWS_REGION")
CONFIRMATION_EMAIL_SENDER = os.environ.get("CONFIRMATION_EMAIL_SENDER")
EMAIL_CONFIRMATION_SUBJECT = "Email Confirmation"
EMAIL_CONFIRMATION_BODY_TEXT = "This is an email confirmation message."
FACEBOOK_API_TOKEN = os.environ.get("FACEBOOK_API_TOKEN")
FACEBOOK_API_ID = os.environ.get("FACEBOOK_API_ID")


class PostgresqlUserRepository(UserRepository):
    def __init__(self, session: any):
        self._session = session

    def create(self, user: UserDtoIn | UserAdminDtoIn) -> Optional[UserDtoOut]:
        try:
            new_user = UserModel(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone_number=user.phone_number,
                password=user.password,
                roles=user.roles.__dict__,
                is_verified=user.is_verified,
                is_admin=getattr(user, "is_admin", False),
            )
            self._session.add(new_user)
            self._session.flush()
            return parse_user_model_to_user_dto(new_user)
        except DBAPIError as message:
            raise InternalServerError(message)

    def create_many(self, user_list: List[UserModel]) -> Optional[List[UserModel]]:
        # Search how to create many user in a posgresql table
        raise NotImplementedError

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self._session.query(UserModel).where(UserModel.email == email).one_or_none()

    def get_by_phone_number(self, phone_number: str) -> Optional[UserModel]:
        return (
            self._session.query(UserModel)
            .where(UserModel.phone_number == phone_number)
            .one_or_none()
        )

    def get_by_id(self, user_id: str) -> Optional[UserModel]:
        return self._session.query(UserModel).where(UserModel.id == user_id).one_or_none()

    def update(self, user_id: str, user: UserModel) -> Optional[UserModel]:
        try:
            if self.get_by_id(user_id):
                user_ref = self._session.query(UserModel).where(UserModel.id == user_id)
                user_ref.update(
                    {
                        UserModel.first_name: user.first_name,
                        UserModel.last_name: user.last_name,
                        UserModel.email: user.email,
                        UserModel.password: user.password,
                        UserModel.phone_number: user.phone_number,
                        UserModel.roles: user.roles,
                        UserModel.is_verified: user.is_verified,
                        UserModel.created_at: user.created_at,
                        UserModel.updated_at: datetime.utcnow(),
                        UserModel.unable_at: user.unable_at,
                    }
                )
                self._session.commit()
                return True
            raise UserNotFoundError(user.first_name)
        except DBAPIError as message:
            # TODO: Implement test for update DBAPIError
            raise InternalServerError(message)

    def delete(self, user_id: str) -> Optional[UserModel]:
        # Search how to delete user in a posgresql table
        raise NotImplementedError


class WhatsappMessageRepository(PhoneMessageRepository):
    def send_phone_message_code(self, phone_number: str, otp: str):
        if not phone_number or not otp:
            raise InvalidCredentialsError()
        response = whatsapp_parser.parse_send_whatsapp_message_response(
            self._send_whatsapp_message_request(
                payload=self._send_whatsapp_message_payload(phone_number, otp),
            )
        )
        return bool(response.get("content", {}).get("messages", [{}])[0].get("id"))

    def _send_whatsapp_message_request(
            self,
            payload: typing.Optional[typing.Dict],
    ) -> typing.Optional[requests.Response]:
        return whatsapp_parser.make_request(
            payload=payload,
            method="POST",
            url="/messages"
        )

    def _send_whatsapp_message_payload(self, phone_number: str, otp: str):
        return authentication_phone_message_template(phone_number, otp)


class BotoMessageRepository(EmailMessageRepository):
    def __init__(self):
        self.sender = CONFIRMATION_EMAIL_SENDER
        self.aws_region = AWS_REGION
        self.charset = "UTF-8"
        self.client = boto3.client("ses", region_name=self.aws_region)
        self.env = Environment(
            loader=ChoiceLoader(
                [
                    FileSystemLoader("role-based_app/users/infrastructure/templates/"),
                    FileSystemLoader("role-based_app/shared/commons/templates/"),
                ]
            )
        )

    def _get_email_parts(self, user: UserDtoIn, token: str):
        subject = EMAIL_CONFIRMATION_SUBJECT
        body_text = EMAIL_CONFIRMATION_BODY_TEXT
        template = self.env.get_template("confirmation_email.html.jinja")
        rendered_template = template.render(
            user=user, token=token, subject=subject, body_text=body_text
        )
        email_parts = {
            "subject": subject,
            "body_text": body_text,
            "body_html": rendered_template,
        }
        return email_parts

    def _send_email(self, subject, body_text, body_html, recipient):
        """Sends an email using Amazon SES."""
        try:
            response = self.client.send_email(
                Destination={
                    "ToAddresses": [
                        recipient,
                    ]
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": self.charset,
                            "Data": body_html,
                        },
                        "Text": {
                            "Charset": self.charset,
                            "Data": body_text,
                        },
                    },
                    "Subject": {
                        "Charset": self.charset,
                        "Data": subject,
                    },
                },
                Source=self.sender,
            )
            response["Subject"] = {"Data": subject}
            response["Body"] = {
                "Text": {"Data": body_text},
                "Html": {"Data": body_html},
            }
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            raise InvalidMessageParameter(error_message)
        else:
            logging.info(f'Email sent! Message ID: {response["MessageId"]}')
            return response

    def send_confirmation_email(self, user: UserDtoIn, token: str):
        email_parts = self._get_email_parts(user, token)
        return self._send_email(
            subject=email_parts["subject"],
            body_text=email_parts["body_text"],
            body_html=email_parts["body_html"],
            recipient=user.email,
        )


class JWTAuthenticationRepository(TokenAuthenticationRepository):
    def gen_verification_token(self, payload: dict) -> str:
        return jwt.encode(payload, JWT_TOKEN_SECRET_KEY, algorithm=JWT_TOKEN_ALGORITHM)

    def validate_code(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, JWT_TOKEN_SECRET_KEY, algorithms=[JWT_TOKEN_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError
        except jwt.PyJWTError:
            raise InvalidTokenError

        return payload


class PyOTPasswordRepository(OTPasswordRepository):
    def get_otp(self, phone_number: str):
        # TODO: BD-91
        return True
