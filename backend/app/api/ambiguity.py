import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.ambiguity import (
    AmbiguityAnalysisRequest,
    AmbiguityAnalysisResponse,
)
from app.services.ambiguity_service import (
    AmbiguityAnalysisError,
    AmbiguityService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ambiguity",
    tags=["Ambiguity Detector"],
)


@router.post(
    "/analyze",
    response_model=AmbiguityAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_ambiguity(
    request: AmbiguityAnalysisRequest,
) -> AmbiguityAnalysisResponse:
    service = AmbiguityService()

    try:
        return await service.analyze(request)

    except AmbiguityAnalysisError as exc:
        logger.warning(
            "Ambiguity API request failed requirement_id=%s",
            request.requirement_id,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()