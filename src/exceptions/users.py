from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id {user_id} не найден"
        )


class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с таки email уже существует"
        )
