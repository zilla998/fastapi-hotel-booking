from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import FacilitiesServiceDep
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.schemas.facilities import FacilitiesReadSchema, FatilitiesAddSchema

router = APIRouter(prefix="/facilities", tags=["Предметы в номерах"])


@router.get(
    "", summary="Получение списка предметов", response_model=list[FacilitiesReadSchema]
)
async def get_facilities(service: FacilitiesServiceDep):
    return await service.get_all()


@router.get(
    "/{facility_id}",
    summary="Получение конкретного предмета",
    response_model=FacilitiesReadSchema,
)
async def get_facility(facility_id: int, service: FacilitiesServiceDep):
    try:
        return await service.get_by_id(facility_id)
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет с таким id не найден"
        ) from err


@router.post("", summary="Добавление предмета")
async def add_facility(facility: FatilitiesAddSchema, service: FacilitiesServiceDep):
    try:
        return await service.add(facility)
    except ObjectIsAlreadyExistsException as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Предмет с таким названием уже существует",
        ) from err
