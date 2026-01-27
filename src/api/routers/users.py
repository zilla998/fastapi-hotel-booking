from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select

from src.config import config as authx_config
from src.config import security
from src.database import SessionDep
from src.exceptions.users import UserAlreadyExists, UserNotFound
from src.models.users import UsersOrm
from src.schemas.users import UserCreateSchema, UserLoginSchema, UserReadSchema

router = APIRouter(
    prefix="/users", tags=["Пользователи"]
)  # Создаем отдельный router для users


@router.get(
    "",
    # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    dependencies=[Depends(security.access_token_required)],
    status_code=200,
)
async def get_users(session: SessionDep):
    query = select(UsersOrm)
    result = await session.execute(query)
    users = (
        result.scalars().all()
    )  # scalars это что то типа objects в Django (User.objects.all())
    return users


@router.get(
    "/{id}",
    summary="Получение пользователя по id",
    response_model=UserReadSchema,  # Указываем схему, по которой будет возвращаться наш запрос
    status_code=200,
)
async def get_user(id: int, session: SessionDep):
    query = select(UsersOrm).where(UsersOrm.id == id)
    result = await session.execute(
        query
    )  # Отправляем запрос в БД делает выборку из таблицы UsersOrm с фильтром по id
    user = (
        result.scalar_one_or_none()
    )  # Возвращает объект из результата. Если объекта нет, возвращает None
    if (
        user is None
    ):  # Если пользователя с таким id нет, возвращает статус код и сообщение об ошибки
        raise UserNotFound(id)
    return user


@router.post(
    "",
    # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Создание пользователя",
    response_model=UserReadSchema,  # Указываем схему ответа без пароля для безопасности
    status_code=201,
)
async def add_user(
    user: UserCreateSchema, session: SessionDep
):  # session: Получаем готовую сессию без ручного создания и для управления ей (открытие/закрытие сессии)
    query = select(UsersOrm).where(UsersOrm.email == user.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:  # Проверяем существует ли пользователь с таким email
        raise UserAlreadyExists()

    # Создаем новый ORM-объект
    new_user = UsersOrm(email=str(user.email), hashed_password=user.password)

    # Записываем его в БД
    """
    добавляет объект new_user в текущую сессию SQLAlchemy и помечает его как “pending” (готов к вставке).
    Сам INSERT в БД ещё не выполняется.
    """
    session.add(new_user)
    """
    фиксирует транзакцию:
    перед этим SQLAlchemy выполнит нужные SQL (INSERT и т. п.) и затем сделает COMMIT.
    Только после этого запись гарантированно сохранена в БД.
    """
    await session.commit()

    # Перечитывает состояние объекта из базы данных и обновляет его поля значениями из БД.
    await session.refresh(new_user)
    """
    Что это дает на практике:
        • Подтягивает значения,
            которые сгенерировала БД: id, created_at, значения по умолчанию, триггерные поля и т.п.
        • Полезно после commit() или flush(), если нужно быть уверенным,
            что объект содержит актуальные значения именно из базы.
    """

    return new_user


# Вход пользователя в аккаунт
@router.post(
    "/login",
    summary="Вход пользователя",
)
async def login(credentials: UserLoginSchema, response: Response, session: SessionDep):
    query = select(UsersOrm).where(
        (UsersOrm.email == credentials.email)
        & (UsersOrm.hashed_password == credentials.password)
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404, detail="Пользователь с такими данными не найден"
        )

    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(authx_config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}


@router.get(
    "/protected",
    dependencies=[Depends(security.access_token_required)],
)
async def protected():
    return {"data": "secret"}


# Выход пользователя из аккаунта
@router.post(
    "/logout",
    summary="Выход пользователя",
)
async def user_logout(response: Response, session: SessionDep):
    response.delete_cookie(authx_config.JWT_ACCESS_COOKIE_NAME)
    return {"logout": True}


# Удаление пользователя
@router.delete(
    "/{id}",
    summary="Удаление пользователя",
)
async def delete_user(id: int, session: SessionDep):
    query = select(UsersOrm).where(UsersOrm.id == id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFound(id)

    await session.delete(user)
    await session.commit()

    return Response(status_code=204)
