from src.models.bookings import BookingOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.booking import BookingSchema
from src.schemas.hotels import HotelsReadSchema
from src.schemas.rooms import RoomSchema
from src.schemas.users import UserInternalSchema


class HotelDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = HotelsReadSchema


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserInternalSchema

class RoomDataMapper(DataMapper):
    db_model = RoomsOrm
    schema = RoomSchema
    
class BookingDataMapper(DataMapper):
    db_model = BookingOrm
    schema = BookingSchema