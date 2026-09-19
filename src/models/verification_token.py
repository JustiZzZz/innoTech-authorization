import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base
from src.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.user import User


class VerificationToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "verification_tokens"
    __table_args__ = (
        Index("ix_verification_tokens_token_hash", "token_hash", unique=True),
        Index("ix_verification_tokens_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="verification_tokens",
    )

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_used

    def __repr__(self) -> str:
        return (
            f"<VerificationToken id={self.id} user_id={self.user_id} "
            f"expires_at={self.expires_at} is_valid={self.is_valid}>"
        )