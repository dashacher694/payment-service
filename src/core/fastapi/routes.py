from fastapi import FastAPI

from src.modules.healthcheck.usecase import router as healthcheck_router
from src.modules.outbox.usecase import router as outbox_router
from src.modules.payment.usecase import router as payment_router


def add_routes(app: FastAPI):
    app.include_router(healthcheck_router)
    app.include_router(payment_router)
    app.include_router(outbox_router, prefix="/internal/scheduler")
