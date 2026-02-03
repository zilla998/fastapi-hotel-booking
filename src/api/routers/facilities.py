from fastapi import APIRouter

from src.database import SessionDep
from src.repositories.facilities import FacilitiesRepository
from src.schemas.facilities import FacilitiesReadSchema

router = APIRouter(prefix="/facilities", tags=["Предметы"])


@router.get(
    "", summary="Получение списка предметов", response_model=list[FacilitiesReadSchema]
)
async def get_facilities(session: SessionDep):
    facilities_model = await FacilitiesRepository(session).get_all()
    return facilities_model
