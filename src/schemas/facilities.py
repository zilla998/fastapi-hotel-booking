from pydantic import BaseModel, ConfigDict


class FacilitiesReadSchema(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)
