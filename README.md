# Payment Service

Асинхронный микросервис для обработки платежей с архитектурой DDD.

## Описание

Сервис обрабатывает платежи асинхронно через RabbitMQ, используя Domain-Driven Design (DDD) паттерны для разделения логики слоев.

## Архитектура

- **DDD (Domain-Driven Design)** - разделение на Domain, Application, Infrastructure слои
- **Mapper Pattern** - маппинг доменных моделей на таблицы через mapper_registry
- **Unit of Work** - управление транзакциями через UoW
- **@async_transactional** - декоратор для автоматического управления транзакциями
- **Event-Driven** - асинхронная обработка через RabbitMQ
- **Idempotency** - защита от дублей через Idempotency-Key
- **Retry & DLQ** - 3 попытки обработки с экспоненциальной задержкой

## Технологический стек

- Python 3.11+
- FastAPI + Pydantic 2
- PostgreSQL + SQLAlchemy 2.0 (async)
- RabbitMQ + FastStream
- Alembic (миграции)
- Docker & Docker Compose
- httpx (webhook клиент)
- loguru (логирование)

## Структура проекта

```
payment-service/
├── src/
│   ├── application.py              # FastAPI app
│   ├── consumer.py                 # FastStream consumer
│   ├── main.py                     # Точка входа
│   ├── core/                       # Конфигурация и общие компоненты
│   ├── db/                         # База данных и транзакции
│   ├── adapters/                   # RabbitMQ клиент
│   └── modules/
│       ├── payment/                # Модуль платежей (Domain, Infrastructure, UseCase)
│       └── outbox/                 # Модуль Outbox pattern
├── migrations/                     # Alembic миграции
├── docker-compose.yaml
├── Dockerfile
└── pyproject.toml
```

## Запуск

### 1. Через Docker Compose (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up -d

# Применение миграций
docker-compose exec api alembic upgrade head

# Просмотр логов
docker-compose logs -f api
docker-compose logs -f consumer
```

Сервисы будут доступны:
- API: http://localhost:8020
- Swagger UI: http://localhost:8020/internal/api/payment-service/docs
- Prometheus Metrics: http://localhost:8020/metrics
- Healthcheck: http://localhost:8020/health
- Readiness: http://localhost:8020/ready
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- PostgreSQL: localhost:5432

### 2. Локальная разработка

```bash
# Установка зависимостей
poetry install

# Запуск PostgreSQL и RabbitMQ
docker-compose up -d postgres rabbitmq

# Применение миграций
alembic upgrade head

# Запуск API
poetry run uvicorn src.main:app --reload --port 8020

# Запуск Consumer (в отдельном терминале)
poetry run python src/consumer.py
```

## Использование API

### Аутентификация

Все API эндпоинты требуют API ключ в заголовке `X-API-Key`. Swagger UI имеет кнопку "Authorize" для ввода ключа.

### Создание платежа

```bash
curl -X POST http://localhost:8020/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret-api-key-12345" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{
    "amount": "1000.50",
    "currency": "RUB",
    "description": "Оплата заказа #12345",
    "metadata": {"order_id": "12345", "customer_id": "67890"},
    "webhookUrl": "https://webhook.site/your-unique-url"
  }'
```

Ответ:
```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2026-04-22T08:00:00Z"
}
```

### Получение информации о платеже

```bash
curl -X GET http://localhost:8020/api/v1/payments/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: secret-api-key-12345"
```

Ответ:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "1000.50",
  "currency": "RUB",
  "description": "Оплата заказа #12345",
  "metadata": {"order_id": "12345", "customer_id": "67890"},
  "status": "succeeded",
  "webhook_url": "https://webhook.site/your-unique-url",
  "created_at": "2026-04-22T08:00:00Z",
  "processed_at": "2026-04-22T08:00:05Z"
}
```

### Обработка Outbox событий

```bash
curl -X POST http://localhost:8020/internal/scheduler/outbox/process \
  -H "X-API-Key: secret-api-key-12345"
```

## Webhook уведомления

После обработки платежа сервис отправит POST запрос на указанный `webhookUrl`:

```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "1000.50",
  "currency": "RUB",
  "status": "succeeded",
  "created_at": "2026-04-22T08:00:00.000000"
}
```

**Важно:** URL webhook должен включать протокол (`http://` или `https://`).

## Тестирование

```bash
# Запуск всех тестов с покрытием
poetry run pytest

# Только unit тесты
poetry run pytest -m unit

# HTML отчет по покрытию
poetry run pytest --cov-report=html
```

**Coverage:** 70% | **Тестов:** 8 (7 unit, 1 integration)

## Качество кода

```bash
# Линтинг и автофикс
poetry run ruff check src/ --fix

# Проверка типов
poetry run mypy src/
```



## Особенности реализации

- **DDD Architecture** - разделение на Domain, Application, Infrastructure слои
- **Mapper Pattern** - маппинг доменных моделей через SQLAlchemy mapper_registry
- **Unit of Work** - управление транзакциями через декоратор @async_transactional
- **Outbox Pattern** - гарантированная доставка событий в RabbitMQ
- **Idempotency** - защита от дублей через Idempotency-Key заголовок
- **Retry & DLQ** - 3 попытки с экспоненциальной задержкой, DLQ для неудачных сообщений
- **API Key Authentication** - FastAPI Security с X-API-Key заголовком
- **Healthchecks** - /health и /ready эндпоинты для мониторинга
- **Prometheus Metrics** - метрики HTTP запросов, latency, ошибок

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://payment:payment@localhost:5432/payment_db` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://guest:guest@localhost:5672/` |
| `API_KEY` | API ключ для аутентификации | **Обязательный параметр** |
| `SERVER_HOST` | Хост API | `0.0.0.0` |
| `SERVER_PORT` | Порт API | `8020` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

## Мониторинг

- **RabbitMQ Management UI**: http://localhost:15672
  - Мониторинг очередей
  - Просмотр DLQ
  - Статистика сообщений

- **Логи**: Структурированное логирование через Loguru
  ```bash
  docker-compose logs -f api
  docker-compose logs -f consumer
  ```

## Остановка

```bash
docker-compose down

# С удалением volumes (БД)
docker-compose down -v
```
