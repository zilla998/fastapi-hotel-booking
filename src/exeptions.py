class BookingException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectIsAlreadyExistsException(BookingException):
    detail = "Объект уже существует"


class ObjectEmailOrPasswordNotValidException(BookingException):
    detail = "Неверные почта или пароль"
