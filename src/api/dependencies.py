from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from src.database import async_session_maker
from src.utils.db_manager import DbManager


async def get_db():
    async with DbManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DbManager, Depends(get_db)]


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="Страница")]
    per_page: Annotated[
        int | None,
        Query(5, ge=1, le=100, description="Количество объектов на странице"),
    ]


PaginationDep = Annotated[PaginationParams, Depends()]
