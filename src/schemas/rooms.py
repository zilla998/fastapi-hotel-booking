from pydantic import BaseModel, ConfigDict, Field


class RoomSchema(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    quantity: int

    hotel_id: int

    model_config = ConfigDict(from_attributes=True)


class AddRoomSchema(BaseModel):
    title: str
    description: str | None
    price: float
    quantity: int
    hotel_id: int


class ChangeRoomSchema(AddRoomSchema):
    pass
