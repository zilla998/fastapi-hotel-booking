from fastapi import APIRouter, HTTPException, status

from src.database import SessionDep
from src.exceptions import ObjectNotFoundException
from src.repositories.facilities import FacilitiesRepository
from src.schemas.facilities import FacilitiesReadSchema, FatilitiesAddSchema

router = APIRouter(prefix="/facilities", tags=["Предметы в номерах"])


@router.get(
    "", summary="Получение списка предметов", response_model=list[FacilitiesReadSchema]
)
async def get_facilities(session: SessionDep):
    facilities_model = await FacilitiesRepository(session).get_all()
    return facilities_model


@router.get(
    "/{facility_id}",
    summary="Получение конкретного предмета",
    response_model=FacilitiesReadSchema,
)
async def get_facility(facility_id: int, session: SessionDep):
    try:
        facility_model = await FacilitiesRepository(session).get_one_or_none(
            id=facility_id
        )
        if facility_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет с таким id не найден"
        )

    return facility_model


@router.post("", summary="Добавление предмета")
async def delete_fatility(fatility: FatilitiesAddSchema, session: SessionDep):
    try:
        fatility_model = await FacilitiesRepository(session).add(fatility)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Предмет с таким названием уже существует",
        )

    await session.commit()

    return fatility_model
