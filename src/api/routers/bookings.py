from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import BookingServiceDep, PaginationDep, get_current_user, require_access_cookie
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotAllowedException, ObjectNotFoundException
from src.schemas.booking import BookingCreateSchema, BookingReadSchema

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "/my",
    summary="Мои брони",
    response_model=list[BookingReadSchema],
    dependencies=[Depends(require_access_cookie)],
)
async def get_my_bookings(
    service: BookingServiceDep,
    pagination: PaginationDep,
    current_user=Depends(get_current_user),
):
    """Возвращает список броней текущего авторизованного пользователя."""
    return await service.get_user_bookings(
        user_id=current_user.id,
        limit=pagination.per_page,
        offset=pagination.offset,
    )


@router.post(
    "",
    summary="Бронирование отеля",
    response_model=BookingReadSchema,
    dependencies=[Depends(require_access_cookie)],
)
async def add_booking(
    booking: BookingCreateSchema,
    service: BookingServiceDep,
    current_user=Depends(get_current_user),
):
    """Добавление брони. Пользователь может забронировать только себе."""
    try:
        return await service.add_booking(booking, current_user)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот номер уже забронирован на выбранные даты.",
        )
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена"
        )


@router.delete(
    "/{booking_id}",
    dependencies=[Depends(require_access_cookie)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_booking(
    booking_id: int,
    service: BookingServiceDep,
    current_user=Depends(get_current_user),
):
    """Удаляет бронь. Пользователь может удалить только свою бронь."""
    try:
        await service.delete_booking(booking_id, current_user.id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронь не найдена"
        )
    except ObjectNotAllowedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить чужую бронь",
        )
