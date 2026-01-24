from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.DB_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Добавляю генератор
async def get_async_session():
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]