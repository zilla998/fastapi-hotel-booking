from pydantic import BaseModel, ConfigDict, Field

from schemas.rooms import RoomSchema


class FacilitiesReadSchema(BaseModel):
    id: int
    title: str

    rooms: list[RoomSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FatilitiesAddSchema(BaseModel):
    title: str
    rooms: list[RoomSchema]
