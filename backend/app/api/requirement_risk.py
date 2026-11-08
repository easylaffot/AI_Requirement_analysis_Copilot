import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_risk import (
    RequirementRiskRequest,
    RequirementRiskResponse,
)
from app.services.requirement_risk_service import (
    RequirementRiskAnalysisError,
    RequirementRiskService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-risks",
    tags=["Requirement Risk Analyzer"],
)


@router.post(
    "/analyze",
    response_model=RequirementRiskResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_risks(
    request: RequirementRiskRequest,
) -> RequirementRiskResponse:
    service: RequirementRiskService | None = None

    try:
        service = RequirementRiskService()
        return await service.analyze(request)

    except RequirementRiskAnalysisError as exc:
        logger.warning(
            "Requirement risk API failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected requirement risk error title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during requirement "
                "risk analysis."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()