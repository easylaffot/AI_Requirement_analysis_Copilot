import logging

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.schemas.brd import (
    BrdAnalysisRequest,
    BrdAnalysisResponse,
)
from app.services.brd_service import (
    BrdAnalysisError,
    BrdService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/brd",
    tags=["BRD Analyzer"],
)


@router.post(
    "/analyze",
    response_model=BrdAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_brd(
    request: BrdAnalysisRequest,
) -> BrdAnalysisResponse:
    """
    Analyze a Business Requirements Document and generate
    a structured draft Agile backlog.
    """

    service = BrdService()

    try:
        return await service.analyze(request)

    except BrdAnalysisError as exc:
        logger.warning(
            "BRD analysis failed for project=%s: %s",
            request.project_name,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()