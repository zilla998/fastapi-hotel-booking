from sqladmin import Admin, ModelView
from src.database import engine
from src.models.hotels import HotelsOrm
from src.models.users import UsersOrm


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


def setup_admin(app):
    admin = Admin(app, engine=engine)
    admin.add_view(UsersAdmin)
    admin.add_view(HotelsAdmin)
    return admin
