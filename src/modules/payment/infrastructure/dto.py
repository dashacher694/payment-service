import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from src.modules.utils.enums import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str
    description: str = Field(..., min_length=1, max_length=500)
    metadata: dict = Field(default_factory=dict, alias="metadata")
    webhook_url: str

    class Config:
        populate_by_name = True


class CreatePaymentResponse(BaseModel):
    payment_id: uuid.UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: str
    description: str
    meta: dict = Field(alias="metadata")
    status: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True
        populate_by_name = True
