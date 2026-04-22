from fastapi import FastAPI

from src.modules.payment.usecase import router as payment_router
from src.modules.outbox.usecase.process_outbox.api import router as outbox_router

def add_routes(app: FastAPI):
    app.include_router(payment_router)
    app.include_router(outbox_router)
