import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.gap_analysis import (
    GapAnalysisRequest,
    GapAnalysisResponse,
)
from app.services.gap_analysis_service import (
    GapAnalysisError,
    GapAnalysisService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/gap-analysis",
    tags=["Requirement Gap Analyzer"],
)


@router.post(
    "/analyze",
    response_model=GapAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_gaps(
    request: GapAnalysisRequest,
) -> GapAnalysisResponse:
    service = GapAnalysisService()

    try:
        return await service.analyze(request)
    except GapAnalysisError as exc:
        logger.warning(
            "Requirement gap analysis API failed requirement_id=%s",
            request.requirement_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    finally:
        await service.close()
