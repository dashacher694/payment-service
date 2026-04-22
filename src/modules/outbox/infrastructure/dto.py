from pydantic import BaseModel


class OutboxEventData(BaseModel):
    payment_id: str
    amount: str
    currency: str
    webhook_url: str


class SchedulerOutboxResponse(BaseModel):
    success_sent_events_count: int
    error_sent_events_count: int
