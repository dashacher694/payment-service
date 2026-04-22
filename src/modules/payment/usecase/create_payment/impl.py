from datetime import datetime
from src.db.transaction import async_transactional
from src.modules.payment.domain.aggregate.model import Payment
from src.modules.utils.enums import PaymentStatus
from src.modules.payment.infrastructure.uow import PaymentUnitOfWork
from src.modules.payment.infrastructure.dto import CreatePaymentRequest, CreatePaymentResponse
from src.modules.outbox.domain.aggregate.model import Outbox
from src.modules.outbox.infrastructure.dto import OutboxEventData

SERVICE_SOURCE = "payment-service"


class CreatePaymentUseCase:
    def __init__(self, uow: PaymentUnitOfWork):
        self.uow = uow

    @async_transactional()
    async def invoke(
        self, request: CreatePaymentRequest, idempotency_key: str
    ) -> CreatePaymentResponse:

        existing = await self.uow.repository.get_by_idempotency_key(idempotency_key)
        if existing:
            return CreatePaymentResponse(
                payment_id=existing.id,
                status=existing.status,
                created_at=existing.created_at,
            )

        payment = Payment(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            meta=request.metadata,
            webhook_url=request.webhook_url,
            idempotency_key=idempotency_key,
            status=PaymentStatus.pending,
            created_at=datetime.utcnow(),
        )
        
        self.uow.session.add(payment)
        
        outbox_data = OutboxEventData(
            payment_id=str(payment.id),
            amount=str(payment.amount),
            currency=payment.currency.value,
            webhook_url=payment.webhook_url,
        )
        
        outbox = Outbox(
            payment_id=payment.id,
            data=outbox_data.model_dump(),
            send_status=False,
            is_validation=True,
            service_source=SERVICE_SOURCE,
            created_at=datetime.utcnow(),
            processed_at=None,
        )
        
        self.uow.session.add(outbox)

        return CreatePaymentResponse(
            payment_id=payment.id,
            status=payment.status,
            created_at=payment.created_at,
        )
