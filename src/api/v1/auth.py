from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.exceptions import (
    InvalidTokenError,
    TokenAlreadyUsedError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from src.schemas.auth import RegisterResponse, TokenResponse
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(email=data.email, password=data.password)
        return RegisterResponse(
            message="Регистрация успешна! Ссылка для входа отправлена на вашу почту.",
            email=user.email,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/verify",
    response_model=TokenResponse,
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        user, access_token = await auth_service.verify_email_and_authorize(raw_token=token)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except (InvalidTokenError, TokenExpiredError, TokenAlreadyUsedError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
