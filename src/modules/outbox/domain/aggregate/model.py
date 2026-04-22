from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Outbox:
    payment_id: UUID
    event_type: str
    data: dict
    send_status: bool
    is_validation: bool
    service_source: str
    created_at: datetime
    processed_at: datetime | None
