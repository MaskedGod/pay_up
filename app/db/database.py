from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.config.settings import settings


engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)


async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    "Dependency to get database session"
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed",
            )
        finally:
            await session.close()


class Base(DeclarativeBase):
    pass
