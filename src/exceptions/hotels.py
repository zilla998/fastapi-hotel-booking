from fastapi import HTTPException,status


class HotelNotFound(HTTPException):
    def __init__(self, hotel_id: int | None, title: str | None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Отель с таким" f"id {hotel_id}" if hotel_id else f"название {title}" f"не найден"
        )