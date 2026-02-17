from fastapi import APIRouter, Depends

from src.api.dependencies import DBDep
from src.api.routers.users import get_current_user, require_access_cookie
from src.schemas.booking import BookingSchema, BookingsReservationSchema
from src.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "", summary="Получение списка бронирования", response_model=list[BookingSchema]
)
async def get_all_booking(db: DBDep):
    return await db.booking.get_all()


@router.post(
    "",
    summary="Бронирование отеля",
    response_model=BookingSchema,
    dependencies=[Depends(require_access_cookie)],
)
async def hotel_reservation(
    booking: BookingsReservationSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    return await BookingService().add_booking(booking, db, current_user)
