from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Схема запроса для аутентификации по email и паролю."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема успешной авторизации с возвратом JWT токена и данных пользователя."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    """Схема ответа после успешной первичной регистрации."""

    message: str = Field(
        default="Регистрация успешна! Ссылка для подтверждения отправлена на вашу электронную почту."
    )
    email: EmailStr


class MessageResponse(BaseModel):
    """Универсальная схема статусного текстового ответа."""

    message: str

class ResendVerificationRequest(BaseModel):
    """Схема запроса повторной отправки письма."""
    email: EmailStr