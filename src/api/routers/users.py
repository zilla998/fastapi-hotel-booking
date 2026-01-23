from hmac import new
from tkinter.constants import E

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models.users import UsersOrm
from src.schemas.users import UserCreateSchema, UserReadSchema

router = APIRouter(
    prefix="/users", tags=["Пользователи"]
)  # Создаем отдельный router для users


@router.get(
    "",  # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    status_code=200,
)
async def get_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(UsersOrm))
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
async def get_user(id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(UsersOrm).where(UsersOrm.id == id)
    )  # Отправляем запрос в БД делает выборку из таблицы UsersOrm с фильтром по id
    user = (
        result.scalar_one_or_none()
    )  # Возвращает объект из результата. Если объекта нет, возвращает None
    if (
        user is None
    ):  # Если пользователя с таким id нет, возвращает статус код и сообщение об ошибки
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с id: {id} не найден",
        )
    return user


@router.post(
    "",  # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Создание пользователя",
    response_model=UserReadSchema,  # Указываем схему ответа без пароля для безопасности
    status_code=201,
)
async def add_user(
    user: UserCreateSchema, session: AsyncSession = Depends(get_async_session)
):  # session: Получаем готовую сессию без ручного создания и для управления ей (открытие/закрытие сессии)
    result = await session.execute(select(UsersOrm).where(UsersOrm.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:  # Проверяем существует ли пользователь с таким email
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже существует",
        )

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


@router.delete(
    "/{id}",
    summary="Удаление пользователя",
    status_code=204,
)
async def delete_user(id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(UsersOrm).where(UsersOrm.id == id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Пользователь с id: {id} не найден"
        )

    await session.delete(user)
    await session.commit()

    return Response(status_code=204)
