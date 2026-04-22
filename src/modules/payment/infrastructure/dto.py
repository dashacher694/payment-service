import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from src.modules.utils.enums import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., pattern="^(RUB|USD|EUR)$")
    description: str = Field(..., min_length=1, max_length=500)
    metadata: dict = Field(default_factory=dict)
    webhook_url: str = Field(..., alias="webhookUrl")

    class Config:
        from_attributes = True
        populate_by_name = True


class CreatePaymentResponse(BaseModel):
    payment_id: uuid.UUID = Field(..., alias="paymentId")
    status: str
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class PaymentResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: str
    description: str
    meta: dict = Field(alias="metadata")
    status: str
    webhook_url: str = Field(..., alias="webhookUrl")
    created_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True
        populate_by_name = True


class WebhookPayloadDTO(BaseModel):
    payment_id: str
    amount: str
    currency: str
    status: str
    created_at: str
