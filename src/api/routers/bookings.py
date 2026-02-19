from fastapi import APIRouter, Depends

from src.api.dependencies import DBDep
from src.api.routers.users import get_current_user, require_access_cookie
from src.schemas.booking import BookingCreateSchema, BookingReadSchema
from src.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "", summary="Получение списка бронирования", response_model=list[BookingReadSchema]
)
async def get_all_booking(db: DBDep):
    return await db.booking.get_all()


@router.post(
    "",
    summary="Бронирование отеля",
    response_model=BookingReadSchema,
    dependencies=[Depends(require_access_cookie)],
)
async def hotel_reservation(
    booking: BookingCreateSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    return await BookingService(db).add_booking(booking, current_user)
