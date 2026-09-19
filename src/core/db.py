from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from collections.abc import AsyncGenerator

from src.core.config import get_settings

settings = get_settings()

class Base(DeclarativeBase):

    pass

engine = create_async_engine(url=settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)

async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False,
                                           autocommit=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


