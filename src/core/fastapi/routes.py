from fastapi import FastAPI

from src.modules.payment.usecase import router as payment_router
from src.modules.outbox.usecase import router as outbox_router

from src.modules.payment.usecase.create_payment.api import create_payment
from src.modules.payment.usecase.get_payment.api import get_payment
from src.modules.outbox.usecase.process_outbox.api import process_outbox

def add_routes(app: FastAPI):
    app.include_router(payment_router)
    app.include_router(outbox_router, prefix="/internal/scheduler")
