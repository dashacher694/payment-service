from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from src.dependency.container import Container
from src.modules.healthcheck.infrastructure.dto import HealthCheckResponse
from src.modules.healthcheck.usecase import router
from src.modules.healthcheck.usecase.check_health.impl import HealthCheckUseCase


@router.get(
    "/health",
    name="Health Check",
    summary="Проверка работоспособности сервиса",
    response_model=HealthCheckResponse,
)
@inject
async def health_check(
    uc: HealthCheckUseCase = Depends(Provide[Container.health_check_use_case]),
) -> HealthCheckResponse:
    """
    Базовая проверка работоспособности сервиса
    
    Returns:
        HealthCheckResponse: Статус работоспособности
    """
    return await uc.invoke()
