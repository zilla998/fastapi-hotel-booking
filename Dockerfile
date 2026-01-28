FROM python:3.12.12-slim

# Отключает создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1
 # Логи Python сразу выводятся в stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем uv + не сохраняем pip-кеш
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
