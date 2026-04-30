from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.facilities import FacilitiesOrm
from src.repositories.base import BaseRepository


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm

    async def get_all(self):
        query = select(self.model).options(selectinload(self.model.rooms))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .options(selectinload(self.model.rooms))
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
