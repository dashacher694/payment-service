import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.modules.utils.enums import Currency, PaymentStatus


class PaymentEntity(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(sa.String(3), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    meta: Mapped[dict] = mapped_column(sa.JSON, nullable=False, default=dict)
    webhook_url: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)
