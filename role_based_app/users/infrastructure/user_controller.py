import logging
from http import HTTPStatus
from role_based_app.users.application.user_phone_message import UserPhoneMessage
from role_based_app.users.application.user_login import UserLogin
from role_based_app.users.application.user_signup import UserSignUp
from role_based_app.users.application.user_new_password import UserNewPassword
from role_based_app.shared.infrastructure.dependency_injection.services_factory import (
    user_service_factory,
)
from role_based_app.shared.infrastructure.postgresql.session_db import SessionDb
from role_based_app.users.domain.entities.user import UserDtoIn, UserLoginDto, UserNewPasswordDto
from role_based_app.users.domain.exceptions.internal_server_error import InternalServerError
from role_based_app.users.domain.exceptions.invalid_credentials_error import InvalidCredentialsError
from role_based_app.users.domain.exceptions.invalid_password_error import InvalidPasswordError
from role_based_app.users.domain.exceptions.not_active_account_error import NotActiveAccountError
from role_based_app.users.domain.exceptions.phone_number_not_provided import PhoneNumberNotProvided
from role_based_app.users.domain.exceptions.user_already_exist import UserAlreadyExist
from role_based_app.users.domain.exceptions.whatsapp_response_error import WhatsappResponseError


def create_user(user: UserDtoIn):
    try:
        session = SessionDb()
        user_service = user_service_factory(session)
        create_user_use_case = UserSignUp(user_service=user_service)
        send_phone_message_code_use_case = UserPhoneMessage(user_service=user_service)
        new_user = create_user_use_case.execute(user)
        session.commit()
        send_phone_message_code_use_case.execute(new_user)
        return {
            "statusCode": HTTPStatus.CREATED,
            "message": "User created successfully",
            "body": new_user,
        }
    except UserAlreadyExist as error:
        logging.error(msg=str(error))
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": str(error),
        }
    except InternalServerError as error:
        session.rollback()
        logging.error(msg=error.args)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error.args,
        }
    except InvalidPasswordError as error:
        logging.error(error.args)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error.args,
        }
    except WhatsappResponseError as error:
        logging.error(error.args)
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": error.args,
        }
    except PhoneNumberNotProvided as error:
        logging.error(error.args)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error.args,
        }
    except NotImplementedError:
        logging.error(msg="Function not implemented")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": "Function not implemented",
        }
    except Exception as error:
        session.rollback()
        logging.error(msg={"error": str(error.args) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error.args) + " INTERNAL_SERVER_ERROR",
        }
    except BaseException as error:
        session.rollback()
        logging.error(msg={"error": str(error.args) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error.args) + " INTERNAL_SERVER_ERROR",
        }


def login(user: UserLoginDto):
    try:
        session = SessionDb()
        user_service = user_service_factory(session)
        create_user_use_case = UserLogin(user_service=user_service)
        token = create_user_use_case.execute(user)
        session.commit()

        return {
            "statusCode": HTTPStatus.OK,
            "message": "Login successfully",
            "body": token,
        }
    except NotActiveAccountError as error:
        logging.error(msg=str(error))
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": str(error),
        }
    except NotImplementedError:
        logging.error(msg="Function not implemented")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": "Function not implemented",
        }
    except InvalidCredentialsError as error:
        logging.error(error)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error.args,
        }
    except InternalServerError as error:
        session.rollback()
        logging.error(msg=error)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error,
        }
    except Exception as error:
        logging.error(msg={"error": str(error) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error) + " INTERNAL_SERVER_ERROR",
        }
    except BaseException as error:
        logging.error(msg={"error": str(error) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error) + " INTERNAL_SERVER_ERROR",
        }
    # TODO: Add errors related with Token sending.


def new_password(user: UserNewPasswordDto):
    try:
        session = SessionDb()
        user_service = user_service_factory(session)
        change_user_password_case = UserNewPassword(user_service=user_service)
        response = change_user_password_case.execute(user)
        session.commit()

        return {
            "statusCode": HTTPStatus.OK,
            "message": "Password changed successfully",
            "body": response,
        }
    except NotActiveAccountError as error:
        logging.error(msg=str(error))
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": str(error),
        }
    except NotImplementedError:
        logging.error(msg="Function not implemented")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": "Function not implemented",
        }
    except InvalidCredentialsError as error:
        logging.error(error)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error.args,
        }
    except InternalServerError as error:
        session.rollback()
        logging.error(msg=error)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "error": error,
        }
    except Exception as error:
        logging.error(msg={"error": str(error) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error) + " INTERNAL_SERVER_ERROR",
        }
    except BaseException as error:
        logging.error(msg={"error": str(error) + " INTERNAL_SERVER_ERROR"})
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "error": str(error) + " INTERNAL_SERVER_ERROR",
        }
