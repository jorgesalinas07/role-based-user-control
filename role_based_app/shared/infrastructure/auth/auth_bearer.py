from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dotenv import load_dotenv
import os
from os.path import join, dirname
from role_based_app.users.domain.exceptions.invalid_token_error import InvalidTokenError
from role_based_app.users.domain.exceptions.token_expired_error import TokenExpiredError
from role_based_app.users.domain.services.user_service import LOGIN_TOKEN_TYPE
from starlette.status import HTTP_403_FORBIDDEN

from role_based_app.users.infrastructure.persistance.user_repository import (
    JWTAuthenticationRepository
)

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")
SECRET_KEY = os.environ.get("SECRET_KEY")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            self._validate_token(credentials.credentials)
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication credentials"
            )

    def _validate_token(self, token: str) -> bool:
        token_authentication_repository = JWTAuthenticationRepository()
        try:
            payload = token_authentication_repository.validate_code(token)
            if payload["type"] != LOGIN_TOKEN_TYPE:
                raise InvalidTokenError()
        except (
            InvalidTokenError,
            TokenExpiredError,
        ):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid authentication token",
            )
        return True
