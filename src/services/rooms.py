from src.exceptions import ObjectNotFoundException
from src.schemas.rooms import AddRoomSchema, ChangeRoomSchema


class RoomsService:
    def __init__(self, db):
        self.db = db

    async def get_all(self):
        return await self.db.rooms.get_all()

    async def get_by_id(self, room_id: int):
        room = await self.db.rooms.get_one_or_none(id=room_id)
        if room is None:
            raise ObjectNotFoundException
        return room

    async def add(self, new_room: AddRoomSchema):
        room = await self.db.rooms.add(new_room)
        await self.db.commit()
        return room

    async def update(self, room_id: int, new_room: ChangeRoomSchema):
        updated = await self.db.rooms.edit(new_room, id=room_id)
        await self.db.commit()
        return updated

    async def delete(self, room_id: int):
        await self.db.rooms.delete(id=room_id)
        await self.db.commit()