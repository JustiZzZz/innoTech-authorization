from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenAlreadyUsedError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotVerifiedError,
)
from src.schemas.auth import LoginRequest, RegisterResponse, TokenResponse
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация"])
templates = Jinja2Templates(directory="src/templates")


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Регистрирует нового пользователя, хеширует пароль и отправляет письмо со ссылкой активации."""
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(email=data.email, password=data.password)
        return RegisterResponse(
            message="Регистрация успешна! Ссылка для входа отправлена на вашу почту.",
            email=user.email,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход по логину и паролю",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Аутентифицирует пользователя по паролю и выдает JWT токен доступа."""
    auth_service = AuthService(db)
    try:
        user, access_token = await auth_service.authenticate_by_password(
            email=data.email, password=data.password
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserNotVerifiedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/verify",
    response_model=TokenResponse,
    summary="Верификация email (гибридный ответ: HTML или JSON)",
)
async def verify_email(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Подтверждает email по одноразовому токену:

    Эндпоинт сделан гибридным: если пользователь кликает по ссылке в почтовом клиенте,
    браузер запрашивает text/html и получает готовый веб-экран с подтверждением и токеном.
    При обращении от мобилок или через Swagger возвращается классический JSON TokenResponse.
    """
    auth_service = AuthService(db)
    try:
        user, access_token = await auth_service.verify_email_and_authorize(raw_token=token)

        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return templates.TemplateResponse(
                request=request,
                name="success.html",
                context={
                    "email": user.email,
                    "access_token": access_token,
                },
            )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except (InvalidTokenError, TokenExpiredError, TokenAlreadyUsedError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))