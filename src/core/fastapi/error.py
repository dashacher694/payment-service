from fastapi import status, Request, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.modules.utils.erorr import NotFoundError, BadRequestError


def init_error_handler(app: FastAPI, admin_email: str):
    @app.exception_handler(Exception)
    async def internal_server_error_handle(req: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(exc), "contact": admin_email},
        )

    @app.exception_handler(BadRequestError)
    async def bad_request_exception_handle(req: Request, exc: BadRequestError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handle(req: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handle(req: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation error", "details": exc.errors()},
        )
