from pydantic import BaseModel, ConfigDict, Field


class HotelsReadSchema(BaseModel):
    id: int
    title: str
    location: str

    model_config = ConfigDict(from_attributes=True)


class HotelsSchema(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    location: str = Field(max_length=50)