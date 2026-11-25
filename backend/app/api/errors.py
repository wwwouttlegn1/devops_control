from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.bll.errors import DomainError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(
        _request: Request, error: DomainError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": str(error)},
        )

