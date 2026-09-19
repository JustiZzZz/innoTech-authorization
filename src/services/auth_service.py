from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenAlreadyUsedError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserNotVerifiedError,
)
from src.core.security import (
    create_access_token,
    generate_verification_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.models.user import User
from src.repositories.token_repository import VerificationTokenRepository
from src.repositories.user_repository import UserRepository
from src.services.email_service import EmailService

settings = get_settings()


class AuthService:

    def __init__(
        self,
        session: AsyncSession,
        email_service: EmailService | None = None,
    ) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = VerificationTokenRepository(session)
        self.email_service = email_service or EmailService()

    async def register(self, email: str, password: str) -> User:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"Пользователь с почтой '{email}' уже зарегистрирован.")

        pwd_hash = hash_password(password)
        user = await self.user_repo.create(email=email, password_hash=pwd_hash)

        raw_token, token_hash = generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        await self.token_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await self.session.commit()

        verification_link = (
            f"{settings.APP_BASE_URL}/api/v1/auth/verify?token={raw_token}"
        )
        await self.email_service.send_verification_email(
            to_email=user.email,
            verification_link=verification_link,
        )

        return user

    async def verify_email_and_authorize(self, raw_token: str) -> tuple[User, str]:
        token_hash = hash_token(raw_token)
        token = await self.token_repo.get_by_hash(token_hash)

        if not token:
            raise InvalidTokenError("Ссылка для подтверждения недействительна или повреждена.")

        if token.is_used:
            raise TokenAlreadyUsedError("Эта ссылка для подтверждения уже была использована ранее.")

        if token.is_expired:
            raise TokenExpiredError(
                "Срок действия ссылки для подтверждения истёк. Пожалуйста, запросите новую."
            )

        user = await self.user_repo.get_by_id(token.user_id)
        if not user:
            raise UserNotFoundError("Связанный аккаунт пользователя не найден.")

        await self.user_repo.mark_as_verified(user)
        await self.token_repo.mark_as_used(token)

        await self.session.commit()
        await self.session.refresh(user)

        access_token = create_access_token(user_id=user.id, email=user.email)

        return user, access_token

    async def authenticate_by_password(self, email: str, password: str) -> tuple[User, str]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Неверный адрес электронной почты или пароль.")

        if not user.is_active:
            raise InvalidCredentialsError("Учётная запись пользователя заблокирована.")

        if not user.is_verified:
            raise UserNotVerifiedError(
                "Ваш email ещё не подтверждён. Пожалуйста, перейдите по ссылке из отправленного письма."
            )

        access_token = create_access_token(user_id=user.id, email=user.email)
        return user, access_token