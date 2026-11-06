import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.nfr import (
    NfrRecommendationRequest,
    NfrRecommendationResponse,
)
from app.services.nfr_service import (
    NfrRecommendationError,
    NfrService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/nfr",
    tags=["NFR Recommender"],
)


@router.post(
    "/recommend",
    response_model=NfrRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
async def recommend_nfrs(
    request: NfrRecommendationRequest,
) -> NfrRecommendationResponse:
    """
    Analyze a functional requirement and recommend
    relevant non-functional requirements.
    """

    service = NfrService()

    try:
        return await service.recommend(request)

    except NfrRecommendationError as exc:
        logger.warning(
            "NFR recommendation failed for requirement_id=%s: %s",
            request.requirement_id,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()