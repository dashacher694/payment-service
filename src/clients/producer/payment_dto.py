import uuid
from decimal import Decimal
from pydantic import BaseModel


class PaymentCreatedDTO(BaseModel):
    payment_id: uuid.UUID
    amount: Decimal
    currency: str
    webhook_url: str
