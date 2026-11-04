import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.acceptance_criteria import (
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
)
from app.services.acceptance_criteria_service import (
    AcceptanceCriteriaGenerationError,
    AcceptanceCriteriaService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/acceptance-criteria",
    tags=["Acceptance Criteria Generator"],
)


@router.post(
    "/generate",
    response_model=AcceptanceCriteriaResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_acceptance_criteria(
    request: AcceptanceCriteriaRequest,
) -> AcceptanceCriteriaResponse:
    service = AcceptanceCriteriaService()

    try:
        return await service.generate(request)

    except AcceptanceCriteriaGenerationError as exc:
        logger.warning(
            "Acceptance-criteria generation failed "
            "for story_id=%s: %s",
            request.story_id,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()