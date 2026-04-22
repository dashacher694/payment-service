import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from src.modules.utils.enums import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: Currency
    description: str = Field(..., min_length=1, max_length=500)
    metadata: dict = Field(default_factory=dict)
    webhook_url: str


class CreatePaymentResponse(BaseModel):
    payment_id: uuid.UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: Currency
    description: str
    meta: dict
    status: PaymentStatus
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True
