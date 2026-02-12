from sqlalchemy import update

from exceptions import ObjectNotFoundException
from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def set_password(self, user_id, new_hashed_password):
        query = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ObjectNotFoundException
