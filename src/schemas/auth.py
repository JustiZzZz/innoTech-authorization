from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str = Field(
        default="Регистрация успешна! Ссылка для подтверждения отправлена на вашу электронную почту."
    )
    email: EmailStr


class MessageResponse(BaseModel):
    message: str