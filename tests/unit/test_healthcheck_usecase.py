import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.healthcheck.usecase.check_health.impl import HealthCheckUseCase
from src.modules.healthcheck.usecase.check_readiness.impl import ReadinessCheckUseCase


@pytest.mark.unit
class TestHealthCheckUseCase:
    """Unit tests for HealthCheckUseCase"""
    
    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(self):
        """Test health check always returns healthy status"""
        use_case = HealthCheckUseCase()
        
        result = await use_case.invoke()
        
        assert result.status == "healthy"


@pytest.mark.unit
class TestReadinessCheckUseCase:
    """Unit tests for ReadinessCheckUseCase"""
    
    @pytest.mark.asyncio
    async def test_readiness_check_all_healthy(self):
        """Test readiness check when all dependencies are healthy"""
        # Mock engine
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_engine.connect = MagicMock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        
        # Mock RabbitMQ client
        mock_rabbitmq = MagicMock()
        mock_rabbitmq.connection = MagicMock()
        mock_rabbitmq.connection.is_closed = False
        
        use_case = ReadinessCheckUseCase(
            engine=mock_engine,
            rabbitmq_client=mock_rabbitmq
        )
        
        result = await use_case.invoke()
        
        assert result.status == "ready"
        assert result.checks["database"] is True
        assert result.checks["rabbitmq"] is True
        assert result.http_status_code == 200
    
    @pytest.mark.asyncio
    async def test_readiness_check_database_unhealthy(self):
        """Test readiness check when database is unhealthy"""
        # Mock engine that raises exception
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Database connection failed")
        
        # Mock healthy RabbitMQ
        mock_rabbitmq = MagicMock()
        mock_rabbitmq.connection = MagicMock()
        mock_rabbitmq.connection.is_closed = False
        
        use_case = ReadinessCheckUseCase(
            engine=mock_engine,
            rabbitmq_client=mock_rabbitmq
        )
        
        result = await use_case.invoke()
        
        assert result.status == "not_ready"
        assert result.checks["database"] is False
        assert result.checks["rabbitmq"] is True
        assert result.http_status_code == 503
    
    @pytest.mark.asyncio
    async def test_readiness_check_rabbitmq_unhealthy(self):
        """Test readiness check when RabbitMQ is unhealthy"""
        # Mock healthy engine
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_engine.connect = MagicMock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        
        # Mock unhealthy RabbitMQ
        mock_rabbitmq = MagicMock()
        mock_rabbitmq.connection = None
        
        use_case = ReadinessCheckUseCase(
            engine=mock_engine,
            rabbitmq_client=mock_rabbitmq
        )
        
        result = await use_case.invoke()
        
        assert result.status == "not_ready"
        assert result.checks["database"] is True
        assert result.checks["rabbitmq"] is False
        assert result.http_status_code == 503
