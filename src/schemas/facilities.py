from pydantic import BaseModel, ConfigDict

from schemas.rooms import RoomSchema


class FacilitiesReadSchema(BaseModel):
    id: int
    title: str

    rooms: list

    model_config = ConfigDict(from_attributes=True)
