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
- RabbitMQ + aio-pika
- Alembic (миграции)
- Docker & Docker Compose
- httpx (webhook клиент)
- loguru (логирование)

## Структура проекта

```
payment-service/
├── src/
│   ├── application.py              # Конфигурация FastAPI app
│   ├── consumer.py                 # RabbitMQ consumer
│   ├── main.py                     # Точка входа
│   ├── core/                       # Ядро приложения
│   │   ├── config.py               # Конфигурация (Settings)
│   │   ├── errors.py               # Кастомные исключения
│   │   └── fastapi/
│   │       ├── error.py            # Error handlers
│   │       ├── mapper.py           # Агрегация всех мапперов
│   │       └── routes.py           # Routes
│   ├── db/                         # База данных
│   │   ├── base.py                 # mapper_registry и metadata
│   │   ├── connection.py           # Подключение к БД
│   │   └── transaction.py          # Декоратор @async_transactional
│   ├── adapters/                   # Внешние адаптеры
│   │   └── rabbitmq/
│   │       └── client.py           # RabbitMQ клиент
│   ├── clients/                    # Централизованные клиенты
│   │   └── producer/
│   │       └── rabbitmq_producer.py # RabbitMQ продюсер
│   └── modules/
│       └── payment/                # Модуль платежей
│           ├── domain/             # Доменная логика
│           │   ├── enums/          # Enum'ы
│           │   │   ├── payment_status.py
│           │   │   └── currency.py
│           │   └── aggregate/
│           │       └── model.py    # Domain модель
│           ├── infrastructure/     # Инфраструктура модуля
│           │   ├── dto.py          # Pydantic DTO
│           │   ├── mapper.py       # Маппинг Domain → Table
│           │   ├── repository.py   # Repository
│           │   └── uow.py          # Unit of Work
│           └── usecase/           # Use Cases
│               ├── __init__.py     # Router
│               ├── create_payment/
│               │   ├── impl.py     # Use Case логика
│               │   └── api.py      # Endpoint
│               └── get_payment/
│                   ├── impl.py     # Use Case логика
│                   └── api.py      # Endpoint
├── migrations/                     # Alembic миграции
│   ├── env.py
│   └── script.py.mako
├── docker-compose.yaml             # PostgreSQL + RabbitMQ + API + Consumer
├── Dockerfile
├── pyproject.toml
└── README.md
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
- API: http://localhost:8000
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
poetry run uvicorn src.main:app --reload --port 8000

# Запуск Consumer (в отдельном терминале)
poetry run python src/consumer.py
```

## Использование API

### Создание платежа

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{
    "amount": "1000.50",
    "currency": "RUB",
    "description": "Оплата заказа #12345",
    "metadata": {"order_id": "12345", "customer_id": "67890"},
    "webhook_url": "https://webhook.site/your-unique-url"
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
curl -X GET http://localhost:8000/api/v1/payments/550e8400-e29b-41d4-a716-446655440000
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

### Health Check

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy"
}
```

## Webhook уведомления

После обработки платежа сервис отправит POST запрос на указанный `webhook_url`:

```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "succeeded",
  "amount": "1000.50",
  "currency": "RUB",
  "processed_at": "2026-04-22T08:00:05Z"
}
```

## Особенности реализации

### DDD Architecture
- **Domain Layer** - доменные модели (Payment) и value objects (PaymentStatus, Currency)
- **Application Layer** - Use Cases с декоратором @async_transactional
- **Infrastructure Layer** - Repository, Mapper, Unit of Work

### Mapper Pattern
- Маппинг доменных моделей на таблицы через SQLAlchemy mapper_registry
- Маппинг инициализируется при старте приложения (start_mapper)
- Repository работает напрямую с доменными моделями через mapper

### Unit of Work
- Управление транзакциями через UoW
- Декоратор @async_transactional автоматически открывает/закрывает транзакции
- Поддержка read-only транзакций

### Idempotency
- Заголовок `Idempotency-Key` обязателен для создания платежа
- Повторные запросы с тем же ключом возвращают существующий платеж

### Retry & Dead Letter Queue
- 3 попытки обработки с экспоненциальной задержкой (1s, 2s, 4s)
- После 3 неудачных попыток сообщение попадает в DLQ
- DLQ можно мониторить через RabbitMQ Management UI

### Error Handling
- Кастомные исключения (NotFoundError, BadRequestError)
- Централизованные error handlers в src/core/fastapi/error.py
- Стандартизированный формат ответов об ошибках

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://payment:payment@localhost:5432/payment_db` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://guest:guest@localhost:5672/` |
| `API_KEY` | API ключ для аутентификации | **Обязательный параметр** |
| `SERVER_HOST` | Хост API | `0.0.0.0` |
| `SERVER_PORT` | Порт API | `8000` |
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

---

© 2026 Payment Service.
