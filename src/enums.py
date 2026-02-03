from enum import StrEnum


class BookingEnums(StrEnum):
    pass


class UserRoles(BookingEnums):
    admin = "Admin"
    user = "User"
