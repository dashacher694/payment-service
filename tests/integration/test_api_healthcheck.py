import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthcheckAPI:
    """Integration tests for healthcheck endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test /health endpoint returns healthy status"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
