from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository


class RoomsRepository(BaseRepository):
    model = RoomsOrm

    async def add(self, data: BaseModel):
        hotel_query = select(HotelsOrm).filter_by(id=data.hotel_id)
        hotel_result = await self.session.execute(hotel_query)
        if hotel_result.scalars().one_or_none() is None:
            raise ObjectNotFoundException
        try:
            query = insert(self.model).values(**data.model_dump()).returning(self.model)
            model = await self.session.execute(query)
            return model.scalars().one()
        except IntegrityError:
            raise ObjectIsAlreadyExistsException
