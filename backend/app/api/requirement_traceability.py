import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_traceability import (
    RequirementTraceabilityRequest,
    RequirementTraceabilityResponse,
)
from app.services.requirement_traceability_service import (
    RequirementTraceabilityAnalysisError,
    RequirementTraceabilityService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-traceability",
    tags=["Requirement Traceability Analyzer"],
)


@router.post(
    "/analyze",
    response_model=RequirementTraceabilityResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_traceability(
    request: RequirementTraceabilityRequest,
) -> RequirementTraceabilityResponse:
    service: RequirementTraceabilityService | None = None

    try:
        service = RequirementTraceabilityService()
        return await service.analyze(request)

    except RequirementTraceabilityAnalysisError as exc:
        logger.warning(
            "Traceability API failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected traceability error title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during requirement "
                "traceability analysis."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()