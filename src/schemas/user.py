from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Ваш пароль (минимум 8 символов)",
    )


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime