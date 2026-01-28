from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, *, name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с таким {name} не найден",
        )


class UserAlreadyExists(HTTPException):
    def __init__(self, *, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с таким {name} уже существует",
        )
