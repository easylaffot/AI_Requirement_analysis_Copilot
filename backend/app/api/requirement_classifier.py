import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.requirement_classifier import (
    RequirementClassificationRequest,
    RequirementClassificationResponse,
)
from app.services.requirement_classifier_service import (
    RequirementClassificationError,
    RequirementClassifierService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/requirement-classifier",
    tags=["Requirement Classifier"],
)


@router.post(
    "/classify",
    response_model=RequirementClassificationResponse,
    status_code=status.HTTP_200_OK,
)
async def classify_requirements(
    request: RequirementClassificationRequest,
) -> RequirementClassificationResponse:
    service: RequirementClassifierService | None = None

    try:
        service = RequirementClassifierService()
        return await service.classify(request)

    except RequirementClassificationError as exc:
        logger.warning(
            "Requirement classification API failed title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected requirement classification error title=%s",
            request.analysis_title,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during requirement "
                "classification."
            ),
        ) from exc

    finally:
        if service is not None:
            await service.close()