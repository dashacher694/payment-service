import asyncio
from contextlib import asynccontextmanager

from faststream import FastStream
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from loguru import logger
from sqlalchemy.orm import clear_mappers

from src.core.config import settings
from src.core.fastapi.mapper import start_mapper
from src.db.connection import get_engine
from src.dependency.container import Container


def create_consumer() -> FastStream:
    """Создание FastStream consumer"""

    broker = RabbitBroker(settings.rabbitmq.rabbitmq_url)

    @asynccontextmanager
    async def lifespan():
        engine = get_engine(settings.db.asyncpg_uri)
        container = Container()

        await engine.connect()
        start_mapper()
        logger.info("Consumer started")

        yield

        clear_mappers()
        await engine.dispose()
        logger.info("Consumer stopped")

    main_queue = RabbitQueue(
        "payments.new",
        durable=True,
        routing_key="payment.created",
        arguments={
            "x-dead-letter-exchange": "payments",
            "x-dead-letter-routing-key": "payment.dlq",
        }
    )

    exchange = RabbitExchange("payments", durable=True, type=ExchangeType.TOPIC)

    @broker.subscriber(main_queue, exchange, retry=3)
    async def process_payment_handler(body: dict):
        container = Container()
        use_case = container.process_payment_consumer_use_case()
        await use_case.invoke(body)

    application = FastStream(broker, lifespan=lifespan)
    return application


async def start_consumer():
    app = create_consumer()
    await app.run()


if __name__ == "__main__":
    asyncio.run(start_consumer())
