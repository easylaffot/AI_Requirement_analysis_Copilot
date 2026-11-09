import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_dependency import (
    RequirementDependencyRequest,
    RequirementDependencyResponse,
)
from app.services.requirement_dependency_service import (
    RequirementDependencyAnalysisError,
    RequirementDependencyService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-dependencies",
    tags=["Requirement Dependency Mapper"],
)


@router.post(
    "/analyze",
    response_model=RequirementDependencyResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_requirement_dependencies(
    request: RequirementDependencyRequest,
) -> RequirementDependencyResponse:
    service: RequirementDependencyService | None = None

    try:
        service = RequirementDependencyService()
        return await service.analyze(request)

    except RequirementDependencyAnalysisError as exc:
        logger.warning(
            "Dependency analysis API failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected dependency analysis error title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during requirement "
                "dependency analysis."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()