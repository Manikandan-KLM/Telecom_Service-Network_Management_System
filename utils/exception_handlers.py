from fastapi import (
    FastAPI,
    Request,
    status
)

from fastapi.exceptions import (
    RequestValidationError
)

from fastapi.responses import JSONResponse

from sqlalchemy.exc import (
    IntegrityError
)


def register_exception_handlers(
    app: FastAPI
):

    @app.exception_handler(
        RequestValidationError
    )
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Request validation failed",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(
        IntegrityError
    )
    async def integrity_exception_handler(
        request: Request,
        exc: IntegrityError
    ):

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "message": "Database integrity error"
            }
        )

    @app.exception_handler(
        Exception
    )
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error"
            }
        )