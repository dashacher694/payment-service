from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status

from src.dependency.container import Container
from src.modules.outbox.infrastructure.dto import SchedulerOutboxResponse
from src.modules.outbox.usecase.process_outbox.impl import ProcessOutboxUseCase
from src.modules.outbox.usecase import router


@router.post(
    "/process",
    name="Process Outbox",
    summary="Обработка outbox событий",
    status_code=status.HTTP_200_OK,
    response_model=SchedulerOutboxResponse,
)
@inject
async def process_outbox(
    uc: ProcessOutboxUseCase = Depends(Provide[Container.process_outbox_use_case]),
):
    """
    Обработка unsent событий из outbox
    
    Отправляет несохраненные события в RabbitMQ.
    """
    result = await uc.invoke()
    
    return result
