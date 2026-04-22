"""
Основной модуль приложения для Payment Service.

Этот модуль содержит настройку FastAPI приложения,
конфигурацию и инициализацию всех необходимых компонентов.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.orm import clear_mappers

from src.core.config import settings
from src.core.fastapi.routes import add_routes
from src.core.fastapi.mapper import start_mapper
from src.core.fastapi.error import init_error_handler
from src.dependency.container import Container


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Payment Service",
        description="Асинхронный сервис процессинга платежей",
        version="1.0.0",
        docs_url="/internal/api/payment-service/docs",
        redoc_url="/internal/api/payment-service/redoc",
        openapi_url="/internal/api/payment-service/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_routes(app)

    init_error_handler(app, "admin@example.com")

    container = Container()
    container.wire()

    @app.on_event("startup")
    async def on_startup():
        logger.info("Starting Payment Service...")
        start_mapper()
        logger.info("Mapper started")

        container = Container()
        await container.rabbitmq_client().connect()
        logger.info("RabbitMQ initialized")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("Shutting down Payment Service...")
        clear_mappers()
        logger.info("Mapper cleared")

    return app


app = create_app()
