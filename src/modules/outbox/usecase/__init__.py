from fastapi import APIRouter

router = APIRouter(prefix="/outbox", tags=["Outbox"])
