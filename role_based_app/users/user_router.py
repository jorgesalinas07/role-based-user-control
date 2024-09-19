""" Handel User Fast Api Requests"""


from role_based_app.shared.commons.utils import check_error
from role_based_app.shared.infrastructure.auth.auth_bearer import JWTBearer
from role_based_app.users.infrastructure import user_controller
from role_based_app.users.domain.entities.user import (
    UserDtoIn,
    UserLoginDto,
    UserNewPasswordDto,
)

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/user", tags=["User"])


@router.post(path="/signup", summary="Create user")
async def signup(user: UserDtoIn) -> dict:
    response = user_controller.create_user(user)
    check_error(response)
    return response


@router.post(path="/login", summary="Login user")
async def login(user: UserLoginDto) -> str:
    response = user_controller.login(user)
    check_error(response)
    return response


@router.get(
    path="/healthy-check",
    summary="healthy check",
    dependencies=[Depends(JWTBearer())],
)
async def healthy_check() -> str:
    return {"healthy-check": "healthy"}


@router.post(
    path="/new_password",
    summary="Authenticated user can change their password",
    dependencies=[Depends(JWTBearer())],
)
async def new_password(user: UserNewPasswordDto) -> str:
    response = user_controller.new_password(user)
    check_error(response)
    return response
