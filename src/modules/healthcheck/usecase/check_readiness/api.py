from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.responses import JSONResponse

from src.dependency.container import Container
from src.modules.healthcheck.usecase import router
from src.modules.healthcheck.usecase.check_readiness.impl import ReadinessCheckUseCase


@router.get(
    "/ready",
    name="Readiness Check",
    summary="Проверка готовности сервиса",
)
@inject
async def readiness_check(
    uc: ReadinessCheckUseCase = Depends(Provide[Container.readiness_check_use_case]),
) -> JSONResponse:
    """
    Проверка готовности сервиса к обработке запросов
    
    Проверяет подключение к БД и RabbitMQ
    
    Returns:
        JSONResponse: Статус готовности с результатами проверок зависимостей
    """
    result = await uc.invoke()
    
    return JSONResponse(
        status_code=result.http_status_code,
        content={
            "status": result.status,
            "checks": result.checks,
        }
    )
