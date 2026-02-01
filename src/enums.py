from enum import StrEnum


class BookingEnums(StrEnum):
    pass


class UserRoles(BookingEnums):
    owner = "Owner"
    admin = "Admin"
    user = "User"
