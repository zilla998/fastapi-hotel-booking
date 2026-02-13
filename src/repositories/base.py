from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, limit=10, offset=0):
        query = select(self.model)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity_pyd(model)
            for model in result.scalars().all()
        ]

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        return self.mapper.map_to_domain_entity_pyd(model)

    async def add(self, data: BaseModel):
        try:
            query = insert(self.model).values(**data.model_dump()).returning(self.model)
            model = await self.session.execute(query)
            return self.mapper.map_to_domain_entity_pyd(model.scalars().one())
        except IntegrityError:
            raise ObjectIsAlreadyExistsException

    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([d.model_dump() for d in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, new_model: BaseModel, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalar_one_or_none()
        if model is None:
            raise ObjectNotFoundException

        model = new_model
        await self.session.commit()
        await self.session.refresh(model)

        return self.mapper.map_to_domain_entity_pyd(model)

    async def delete(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalar_one_or_none()
        if model is None:
            raise ObjectNotFoundException

        await self.session.delete(model)
        await self.session.commit()

    async def patch(self, column_name: str, new_value: str, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalar_one_or_none()
        if model is None:
            raise ObjectNotFoundException

        setattr(model, column_name, new_value)
        await self.session.commit()
        await self.session.refresh(model)

        return self.mapper.map_to_domain_entity_pyd(model)
