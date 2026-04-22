from src.modules.healthcheck.infrastructure.dto import HealthCheckResponse


class HealthCheckUseCase:

    async def invoke(self) -> HealthCheckResponse:
        return HealthCheckResponse(status="healthy")
