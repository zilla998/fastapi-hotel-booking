class BookingException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectIsAlreadyExistsException(BookingException):
    detail = "Объект уже существует"


# TODO: FIX NAME - change to ObjectNotValidException
class ObjectEmailOrPasswordNotValidException(BookingException):
    detail = "Неверные почта или пароль"


class ObjectNotValidException(BookingException):
    detail = "Невалидный объект"


class ObjectNotFoundException(BookingException):
    detail = "Объект не найден"
