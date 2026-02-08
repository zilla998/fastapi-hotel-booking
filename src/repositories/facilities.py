from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.facilities import FacilitiesOrm
from src.repositories.base import BaseRepository


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm

    async def get_all(self):
        query = select(self.model).options(selectinload(self.model.rooms))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .options(selectinload(self.model.rooms))
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()


"""

  File "/home/zilla998/Developer/Python/fastapi-hotel-booking/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 215, in serialize_response
    raise ResponseValidationError(
fastapi.exceptions.ResponseValidationError: 2 validation errors:
  {'type': 'get_attribute_error', 'loc': ('response', 0, 'rooms'), 'msg': "Error extracting attribute: MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)", 'input': <src.models.facilities.FacilitiesOrm object at 0x7f9c5901db80>, 'ctx': {'error': "MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)"}}
  {'type': 'get_attribute_error', 'loc': ('response', 1, 'rooms'), 'msg': "Error extracting attribute: MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)", 'input': <src.models.facilities.FacilitiesOrm object at 0x7f9c5901d3d0>, 'ctx': {'error': "MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)"}}

  File "/home/zilla998/Developer/Python/fastapi-hotel-booking/src/api/routers/facilities.py", line 11, in get_facilities
    GET /facilities


Причину поймали верно: это lazy loading связи rooms в async-контексте, из-за чего FastAPI при сериализации ответа вызывает догрузку
  и получает MissingGreenlet.

  Что исправил:

  - В src/repositories/facilities.py переопределил методы:

  1. get_all()
  2. get_one_or_none()

  - Добавил eager loading связи:

  .options(selectinload(self.model.rooms))

  Почему это работает:

  - selectinload подгружает rooms заранее в рамках текущего async-запроса к БД.
  - К моменту, когда Pydantic читает поле rooms из FacilitiesReadSchema, данные уже загружены и дополнительный I/O не нужен.
  - Поэтому ResponseValidationError с MissingGreenlet исчезает.

  Проверка:

  - Синтаксис проекта проверен командой python -m compileall -q src (ошибок нет).

  Теперь можно повторить GET /facilities и GET /facilities/{id}. Если хотите, следующим шагом могу так же аккуратно вынести поддержку
  eager loading в базовый репозиторий, чтобы не дублировать это в каждом конкретном репозитории.
"""
