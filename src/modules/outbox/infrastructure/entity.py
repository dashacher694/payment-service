import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class OutboxEntity(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    data: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    send_status: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    is_validation: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    service_source: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
