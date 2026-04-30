from src.exceptions import ObjectNotFoundException
from src.schemas.facilities import FatilitiesAddSchema


class FacilitiesService:
    def __init__(self, db):
        self.db = db

    async def get_all(self):
        return await self.db.facilities.get_all()

    async def get_by_id(self, facility_id: int):
        facility = await self.db.facilities.get_one_or_none(id=facility_id)
        if facility is None:
            raise ObjectNotFoundException
        return facility

    async def add(self, facility: FatilitiesAddSchema):
        result = await self.db.facilities.add(facility)
        await self.db.commit()
        return result
