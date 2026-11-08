import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.duplicate_requirement import (
    DuplicateAnalysisRequest,
    DuplicateAnalysisResponse,
)
from app.services.duplicate_requirement_service import (
    DuplicateRequirementAnalysisError,
    DuplicateRequirementService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/duplicate-requirements",
    tags=["Duplicate Requirement Detector"],
)


@router.post(
    "/analyze",
    response_model=DuplicateAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_duplicate_requirements(
    request: DuplicateAnalysisRequest,
) -> DuplicateAnalysisResponse:
    service = DuplicateRequirementService()

    try:
        return await service.analyze(request)

    except DuplicateRequirementAnalysisError as exc:
        logger.warning(
            "Duplicate requirement API request failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()