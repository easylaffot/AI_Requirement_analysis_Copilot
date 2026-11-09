import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.regulatory_impact import (
    RegulatoryImpactRequest,
    RegulatoryImpactResponse,
)
from app.services.regulatory_impact_service import (
    RegulatoryImpactAnalysisError,
    RegulatoryImpactService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/regulatory-impact",
    tags=["Regulatory Impact Analyzer"],
)


@router.post(
    "/analyze",
    response_model=RegulatoryImpactResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_regulatory_impact(
    request: RegulatoryImpactRequest,
) -> RegulatoryImpactResponse:
    service: RegulatoryImpactService | None = None

    try:
        service = RegulatoryImpactService()
        return await service.analyze(request)

    except RegulatoryImpactAnalysisError as exc:
        logger.warning(
            "Regulatory impact API failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected regulatory impact error title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during regulatory "
                "impact analysis."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()