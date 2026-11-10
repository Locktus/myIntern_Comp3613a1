from fastapi import HTTPException, status

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.user import UserRepository
from app.routers import api_router
from app.schemas import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService


@api_router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
async def register_api(payload: RegisterRequest, db: SessionDep):
    user = AuthService(UserRepository(db)).register_user(
        payload.first_name,
        payload.last_name,
        payload.username,
        str(payload.email),
        payload.password,
    )
    return user


@api_router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in",
)
async def login_api(payload: LoginRequest, db: SessionDep):
    repo = UserRepository(db)
    token = AuthService(repo).authenticate_user(payload.username, payload.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user = repo.get_by_username(payload.username)
    return TokenResponse(access_token=token, role=user.role)


@api_router.get(
    "/auth/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user",
)
async def me_api(user: AuthDep):
    return user
