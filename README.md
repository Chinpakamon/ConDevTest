# Booking Service

Backend-сервис для записи на встречи. REST API создаёт брони, Celery-воркер получает задачу из Redis, асинхронно подтверждает запись или помечает её как failed, а данные хранятся в PostgreSQL.

## Стек

- **FastAPI** - HTTP-слой.
- **SQLAlchemy ORM + Alembic** - доступ к PostgreSQL и миграции.
- **Celery + Redis** - очередь фоновой обработки и result backend.
- **pytest** - тесты API и бизнес-логики воркера без поднятого Docker.
- **JSON logging** - структурированные логи приложения и mock-уведомления.

## Быстрый запуск

1. Подготовьте переменные окружения:

```bash
cp .env.example .env
```

2. Поднимите весь стек одной командой:

```bash
docker-compose up --build
```

Контейнер `api` перед стартом применяет миграции командой `alembic upgrade head`. После запуска:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

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

Отменить бронь, если она ещё `pending`:

```bash
curl -X DELETE http://localhost:8000/bookings/1
```

## Тесты и качество

Вариант через Poetry:

```bash
poetry install --with dev
poetry run pytest
```

Если зависимости уже установлены в окружение, тесты запускаются из корня репозитория без Docker:

```bash
pytest
```

Дополнительные команды:

```bash
make test
make lint
```

## Технические решения

- **Разделение слоёв**: `router` содержит только HTTP-контракты, dependency injection, query/body параметры и маппинг доменных ошибок в HTTP-коды; `service` содержит бизнес-правила; `repository` изолирует работу с БД через ORM.
- **Статусы**: используются значения `pending`, `confirmed`, `failed`, `cancelled`, чтобы API соответствовал тестовому заданию.
- **Очередь сразу после создания**: `BookingService.create_booking` создаёт запись в БД и ставит `process_booking.delay(booking.id)` в Celery.
- **Идемпотентность воркера**: обработка выполняется только для `pending`. Повторный запуск для уже `confirmed`, `failed` или `cancelled` возвращает текущий статус и не отправляет повторное уведомление.
- **Имитация внешнего сбоя**: вероятность задаётся через `BOOKING_FAILURE_PROBABILITY` (`0.15` по умолчанию). При сбое статус становится `failed`, при успехе — `confirmed`, а mock-уведомление пишется в JSON-лог и сохраняется в поле `notification_log`.
- **Retry/backoff**: Celery-задача настроена на retry с экспоненциальным backoff для инфраструктурных ошибок (`ConnectionError`, `TimeoutError`). Бизнес-сбой по условию задания фиксируется как `failed`.
- **Rate limiting**: `POST /bookings` защищён простым in-memory лимитом по IP (`RATE_LIMIT_PER_MINUTE`). Для production лучше заменить его на Redis-based limiter.
- **Тестируемость без Docker**: API-тесты подменяют service-слой, а worker-тесты проверяют бизнес-логику на fake repository. Это позволяет запускать `pytest` без PostgreSQL/Redis/Docker, сохраняя разделение слоёв.

## Структура проекта

```text
app/
  api/
    booking/
      consts.py       # booking statuses and ordering constants
      exceptions.py   # domain exceptions
      repository.py   # database access layer only
      service.py      # business logic only
      router.py       # HTTP layer only
      schemas.py      # request/response DTOs
  core/
    settings.py       # application settings
    logging.py        # JSON logging setup
    database/
      core.py         # engine, session and Base setup
      models/         # SQLAlchemy models
  celery_app.py       # Celery application
  tasks.py            # Celery task entrypoint
alembic/              # migrations
tests/                # pytest suite
```
