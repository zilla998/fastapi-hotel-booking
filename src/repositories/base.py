from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.exceptions import (
    ObjectIsAlreadyExistsException,
)


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalars().one_or_none()

        # TODO: return None to raise ObjectNotFoundException
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
