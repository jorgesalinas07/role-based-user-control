import pytest
from fastapi import HTTPException, Request

from role_based_app.shared.infrastructure.auth.auth_bearer import JWTBearer
from role_based_app.users.domain.services.user_service import (
    EXP_TOKEN_LOGIN_HOURS,
    LOGIN_TOKEN_TYPE,
)
from role_based_app.users.infrastructure.persistance.user_repository import (
    JWTAuthenticationRepository,
)


@pytest.mark.asyncio
async def test__JWTBearer_returns_credentials_when_successful():
    payload = {
        "user_id": "12345",
        "exp": EXP_TOKEN_LOGIN_HOURS,
        "type": LOGIN_TOKEN_TYPE,
    }
    token_repository = JWTAuthenticationRepository()
    token = token_repository.gen_verification_token(payload)
    request = Request(
        scope={
            "type": "http",
            "headers": [[bytes("authorization", "latin-1"), bytes(f"bearer {token}", "latin-1")]],
        }
    )
    authorization = JWTBearer()
    response = await authorization.__call__(request)
    assert response == token


@pytest.mark.asyncio
async def test__JWTBearer_raises_HTTP_exception_when_invalid_schema_provided():
    payload = {
        "user_id": "12345",
        "exp": EXP_TOKEN_LOGIN_HOURS,
        "type": LOGIN_TOKEN_TYPE,
    }
    token_repository = JWTAuthenticationRepository()
    token = token_repository.gen_verification_token(payload)
    request = Request(
        scope={
            "type": "http",
            "headers": [
                [bytes("authorization", "latin-1"), bytes(f"JWT Bearer {token}", "latin-1")]
            ],
        }
    )
    authorization = JWTBearer()
    with pytest.raises(HTTPException):
        response = await authorization.__call__(request)
        assert response.json() == {"detail": "Invalid authentication credentials"}


@pytest.mark.asyncio
async def test__JWTBearer_raises_HTTP_exception_when_invalid_token_provided():
    payload = {
        "user_id": "12345",
        "exp": EXP_TOKEN_LOGIN_HOURS,
        "type": "wrong_token_type",
    }
    token_repository = JWTAuthenticationRepository()
    token = token_repository.gen_verification_token(payload)
    request = Request(
        scope={
            "type": "http",
            "headers": [[bytes("authorization", "latin-1"), bytes(f"Bearer {token}", "latin-1")]],
        }
    )
    authorization = JWTBearer()
    with pytest.raises(HTTPException):
        response = await authorization.__call__(request)
        assert response.json() == {"detail": "Invalid authentication token"}
