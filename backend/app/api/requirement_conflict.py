import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_conflict import (
    ConflictAnalysisRequest,
    ConflictAnalysisResponse,
)
from app.services.requirement_conflict_service import (
    RequirementConflictAnalysisError,
    RequirementConflictService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-conflicts",
    tags=["Requirement Conflict Detector"],
)


@router.post(
    "/analyze",
    response_model=ConflictAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_conflicts(
    request: ConflictAnalysisRequest,
) -> ConflictAnalysisResponse:
    service: RequirementConflictService | None = None

    try:
        service = RequirementConflictService()
        return await service.analyze(request)

    except RequirementConflictAnalysisError as exc:
        logger.warning(
            "Requirement conflict API request failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected requirement conflict analysis failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete requirement conflict analysis.",
        ) from exc

    finally:
        if service is not None:
            try:
                await service.close()
            except Exception as exc:
                logger.exception("Unexpected requirement conflict service close failure")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to complete requirement conflict analysis.",
                ) from exc