from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from exeptions import ObjectIsAlreadyExistsException


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalars().one_or_none()

        if model is None:
            return None

        return model

    async def add(self, data: BaseModel):
        try:
            query = insert(self.model).values(**data.model_dump()).returning(self.model)

            model = await self.session.execute(query)
            return model.scalars().one()
        except IntegrityError:
            raise ObjectIsAlreadyExistsException
