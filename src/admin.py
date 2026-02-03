from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from src.config import config, security
from src.database import async_session_maker, engine
from src.enums import UserRoles
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.users import UsersRepository


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        # sqladmin AuthenticationBackend requires a secret key
        super().__init__(secret_key=config.JWT_SECRET_KEY)

    async def login(self, request: Request) -> bool:
        """Автоматический вход, если токен уже есть и он валиден"""
        # Если authenticate вернул True, sqladmin сам пустит.
        # Но если мы попали на страницу логина (/admin/login),
        # значит authenticate вернул False.
        # В этом методе login обычно обрабатывается POST запрос с формой.
        return True

    async def logout(self, request: Request) -> bool:
        """Выход из админки"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Проверка, что пользователь - администратор"""
        # Проверяем, есть ли уже данные в сессии sqladmin
        if request.session.get("token"):
            return True

        # Если в сессии нет, проверяем JWT из куки
        access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME, None)
        if access_token is None:
            return False

        try:
            payload = security._decode_token(access_token)
            user_id = int(payload.sub)
            async with async_session_maker() as session:
                user = await UsersRepository(session).get_one_or_none(id=user_id)
                if user and user.role == UserRoles.admin:
                    # Сохраняем признак аутентификации в сессию для sqladmin
                    request.session.update({"token": access_token})
                    return True
        except Exception as e:
            print("verify_access_token error:", repr(e))
            return False

        return False


class UsersAdmin(ModelView, model=UsersOrm):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [UsersOrm.id, UsersOrm.email]
    column_searchable_list = [UsersOrm.email]


class HotelsAdmin(ModelView, model=HotelsOrm):
    name = "Отель"
    name_plural = "Отели"
    column_list = [HotelsOrm.id, HotelsOrm.title, HotelsOrm.location]
    column_searchable_list = [HotelsOrm.title, HotelsOrm.location]


class RoomsAdmin(ModelView, model=RoomsOrm):
    name = "Комната"
    name_plural = "Комнаты"
    # column_list = [
    #     RoomsOrm.id,
    #     RoomsOrm.title,
    #     RoomsOrm.description,
    #     RoomsOrm.price,
    #     RoomsOrm.quantity,
    #     RoomsOrm.hotel_id,
    # ]
    column_list = "__all__"
    column_searchable_list = [RoomsOrm.title, RoomsOrm.price, RoomsOrm.quantity]


class FacilitiesAdmin(ModelView, model=FacilitiesOrm):
    name = "Предмет"
    name_plural = "Предметы"
    # column_list = [FacilitiesOrm.id, FacilitiesOrm.title, FacilitiesOrm.rooms]
    column_list = "__all__"
    column_searchable_list = [FacilitiesOrm.title, FacilitiesOrm.rooms]


def setup_admin(app):
    admin = Admin(app, engine=engine, authentication_backend=AdminAuth())
    admin.add_view(UsersAdmin)
    admin.add_view(HotelsAdmin)
    admin.add_view(RoomsAdmin)
    admin.add_view(FacilitiesAdmin)
    return admin
