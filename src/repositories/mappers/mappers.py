from src.models.hotels import HotelsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.hotels import HotelsReadSchema
from src.schemas.users import UserInternalSchema


class HotelDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = HotelsReadSchema


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserInternalSchema
