from typing import Literal

from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import ApplicationError
from app.core.logging import get_logger
from app.db.session import Database

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database is unavailable"}},
)
def health(request: Request) -> HealthResponse:
    database: Database = request.app.state.database
    try:
        database.check_connection()
    except SQLAlchemyError as exc:
        logger.warning("Database readiness check failed", exc_info=exc)
        raise ApplicationError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="database_unavailable",
            message="The database is unavailable",
        ) from exc
    return HealthResponse(status="ok", database="ok")
