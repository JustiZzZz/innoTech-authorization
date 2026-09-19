from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        stmt = select(User).where(User.email == normalized_email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> User:
        normalized_email = email.strip().lower()
        user = User(
            email=normalized_email,
            password_hash=password_hash,
            is_active=True,
            is_verified=False,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def mark_as_verified(self, user: User) -> User:
        user.is_verified = True
        await self.session.flush()
        return user