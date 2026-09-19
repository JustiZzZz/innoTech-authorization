from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.verification_token import VerificationToken
from src.repositories.base import BaseRepository


class VerificationTokenRepository(BaseRepository):

    async def create(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> VerificationToken:

        token = VerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used_at=None,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> VerificationToken | None:

        stmt = select(VerificationToken).where(VerificationToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_used(self, token: VerificationToken) -> VerificationToken:

        token.used_at = datetime.now(timezone.utc)
        await self.session.flush()
        return token