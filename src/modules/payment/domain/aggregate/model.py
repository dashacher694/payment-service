import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.modules.utils.enums import PaymentStatus


@dataclass
class Payment:
    amount: Decimal
    currency: str
    description: str
    meta: dict
    webhook_url: str
    idempotency_key: str
    status: PaymentStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = field(default=None)
    processed_at: datetime | None = field(default=None)
