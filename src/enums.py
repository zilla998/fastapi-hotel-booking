from enum import StrEnum


class ErrorCode(StrEnum):
    UNAUTHORIZED = "unauthorized"
    USER_NOT_FOUND = "user_not_found"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"
    FORBIDDEN = "forbidden"


class BookingEnums(StrEnum):
    pass


class UserRoles(BookingEnums):
    admin = "Admin"
    user = "User"
