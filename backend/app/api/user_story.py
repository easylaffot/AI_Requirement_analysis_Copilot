import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.user_story import (
    UserStoryGenerationRequest,
    UserStoryGenerationResponse,
)
from app.services.user_story_service import (
    UserStoryGenerationError,
    UserStoryService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/user-stories",
    tags=["User Story Generator"],
)


@router.post(
    "/generate",
    response_model=UserStoryGenerationResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_user_stories(
    request: UserStoryGenerationRequest,
) -> UserStoryGenerationResponse:
    service = UserStoryService()

    try:
        return await service.generate(request)

    except UserStoryGenerationError as exc:
        logger.warning(
            "User-story generation failed for requirement=%s: %s",
            request.requirement_title,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()