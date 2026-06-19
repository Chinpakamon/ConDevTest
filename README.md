# Booking Service

Backend-сервис для записи на встречи: REST API создаёт брони, Celery-воркер асинхронно подтверждает их через очередь Redis, а состояние хранится в PostgreSQL.

## Стек

- **FastAPI**
- **SQLAlchemy ORM + Alembic**
- **Celery + Redis**
- **pytest**
- **JSON logging**

## Быстрый запуск

`.env.example` уже содержит рабочие значения для Docker Compose. Если нужно переопределить настройки локально, скопируйте его в `.env` и измените значения.

Чтобы скопировать настройки в `.env` выполните:
```bash
cp .env.example .env
```

А далее выполните:
```bash
docker-compose up --build
```

При необходимости миграции можно применить командой `docker-compose run --rm api alembic upgrade head`; приложение также создаёт таблицы при старте для удобства тестового запуска. После запуска API доступен на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

## Примеры API

Создать бронь:

```bash
curl -X POST http://localhost:8000/bookings \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","datetime":"2030-01-01T10:00:00Z","service_type":"consultation"}'
```

Получить статус:

```bash
curl http://localhost:8000/bookings/1
```

Список с фильтром и пагинацией:

```bash
curl 'http://localhost:8000/bookings?status=confirmed&limit=20&offset=0'
```

Отменить pending-бронь:

```bash
curl -X DELETE http://localhost:8000/bookings/1
```

## Тесты и качество

Установить зависимости и запустить тесты из корня репозитория:

```bash
pip install -e '.[dev]'
pytest
```

Дополнительно:

```bash
make test
make lint
```

## Технические решения

- **Разделение слоёв**: HTTP-детали находятся в `router`, бизнес-правила — в `service`, а работа с БД — в `repository`.
- **Идемпотентность воркера**: задача меняет только брони в статусе `pending`. Повторный запуск для `confirmed`, `failed` или `cancelled` возвращает текущий статус и не отправляет повторное уведомление.
- **Имитация сбоя внешнего сервиса**: воркер использует вероятность `BOOKING_FAILURE_PROBABILITY` (`0.15` по умолчанию). При сбое статус становится `failed`, при успехе — `confirmed` и пишется mock-лог уведомления.
- **Retry/backoff**: Celery-задача настроена с `retry_backoff` и `retry_jitter`. Бизнес-сбой по условию тестового задания фиксируется как `failed`, а инфраструктурные ошибки Celery может ретраить.
- **Rate limiting**: `POST /bookings` ограничен простым in-memory лимитом(`RATE_LIMIT_PER_MINUTE`).
- **Тестируемость без Docker**: FastAPI dependency override подменяет БД на SQLite in-memory, а отправка Celery-задачи мокается в API-тестах.

## Структура проекта

```text
app/
  api/
    booking/
      consts.py       # booking statuses and constants
      exceptions.py   # domain exceptions
      repository.py   # database access layer
      service.py      # business logic
      router.py       # HTTP layer
      schemas.py      # request/response DTOs
  core/
    settings.py       # application settings
    database/
      core.py         # engine, session and Base setup
      models/         # SQLAlchemy models
  tasks.py            # Celery worker task
tests/                # pytest suite
```
