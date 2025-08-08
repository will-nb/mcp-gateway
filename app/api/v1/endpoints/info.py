from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


from app.schemas.response import SuccessResponse


@router.get(
    "/info",
    response_model=SuccessResponse[HealthResponse],
    summary="Application info",
)
def get_info() -> SuccessResponse[HealthResponse]:
    settings = get_settings()
    return SuccessResponse(data=HealthResponse(status="ok", version=settings.version))
