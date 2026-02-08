class BookingException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectIsAlreadyExistsException(BookingException):
    detail = "Объект уже существует"


class ObjectNotValidException(BookingException):
    detail = "Невалидный объект"


class ObjectNotFoundException(BookingException):
    detail = "Объект не найден"


class ObjectNotAllowedException(BookingException):
    detail = "Доступ к объекту запрещен"
