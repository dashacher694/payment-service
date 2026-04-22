from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.adapters.rabbitmq.client import RabbitMQClient
from src.modules.healthcheck.infrastructure.dto import ReadinessCheckResponse


class ReadinessCheckUseCase:
    """
    Use case для проверки готовности сервиса к обработке запросов
    
    Проверяет доступность критических зависимостей:
    - База данных (PostgreSQL)
    - Брокер сообщений (RabbitMQ)
    """
    
    def __init__(self, engine: AsyncEngine, rabbitmq_client: RabbitMQClient):
        """
        Инициализация use case
        
        Args:
            engine: SQLAlchemy async engine для проверки БД
            rabbitmq_client: RabbitMQ клиент для проверки брокера
        """
        self.engine = engine
        self.rabbitmq_client = rabbitmq_client
    
    async def invoke(self) -> ReadinessCheckResponse:
        """
        Выполнить проверку готовности сервиса
        
        Проверяет:
        - Подключение к базе данных
        - Подключение к RabbitMQ
        
        Returns:
            ReadinessCheckResponse: Статус готовности и результаты проверок
        """
        checks = {
            "database": await self._check_database(),
            "rabbitmq": await self._check_rabbitmq(),
        }
        
        all_healthy = all(checks.values())
        status = "ready" if all_healthy else "not_ready"
        http_status_code = 200 if all_healthy else 503
        
        return ReadinessCheckResponse(
            status=status,
            checks=checks,
            http_status_code=http_status_code
        )
    
    async def _check_database(self) -> bool:
        """
        Проверить подключение к базе данных
        
        Returns:
            bool: True если подключение успешно, False в случае ошибки
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def _check_rabbitmq(self) -> bool:
        """
        Проверить подключение к RabbitMQ
        
        Returns:
            bool: True если подключение активно, False в случае ошибки
        """
        try:
            if self.rabbitmq_client.connection and not self.rabbitmq_client.connection.is_closed:
                return True
            logger.warning("RabbitMQ connection not established")
            return False
        except Exception as e:
            logger.error(f"RabbitMQ health check failed: {e}")
            return False
