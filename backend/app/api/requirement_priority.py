import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_priority import (
    RequirementPriorityRequest,
    RequirementPriorityResponse,
)
from app.services.requirement_priority_service import (
    RequirementPriorityAnalysisError,
    RequirementPriorityService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-priorities",
    tags=["Requirement Prioritization Assistant"],
)


@router.post(
    "/analyze",
    response_model=RequirementPriorityResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_priorities(
    request: RequirementPriorityRequest,
) -> RequirementPriorityResponse:
    service: RequirementPriorityService | None = None

    try:
        service = RequirementPriorityService()
        return await service.prioritize(request)

    except RequirementPriorityAnalysisError as exc:
        logger.warning(
            "Prioritization API failed title=%s",
            request.analysis_title,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected prioritization error title=%s",
            request.analysis_title,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during requirement "
                "prioritization."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()