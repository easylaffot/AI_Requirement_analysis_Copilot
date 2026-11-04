from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]


class UserStoryGenerationRequest(BaseModel):
    requirement_title: str = Field(
        min_length=3,
        max_length=200,
    )

    requirement_text: str = Field(
        min_length=20,
        max_length=10000,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    known_actors: list[str] = Field(
        default_factory=list,
    )

    business_rules: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class AcceptanceCriterion(BaseModel):
    criterion_id: str
    criterion: str

    criterion_type: Literal[
        "Positive",
        "Negative",
        "Boundary",
        "Business Rule",
    ]


class InvestAssessment(BaseModel):
    independent: bool
    independent_reason: str

    negotiable: bool
    negotiable_reason: str

    valuable: bool
    valuable_reason: str

    estimable: bool
    estimable_reason: str

    small: bool
    small_reason: str

    testable: bool
    testable_reason: str


class GeneratedUserStory(BaseModel):
    story_id: str
    title: str

    actor: str
    goal: str
    business_value: str

    story: str = Field(
        description=(
            "Story in As a, I want, so that format"
        ),
    )

    acceptance_criteria: list[AcceptanceCriterion] = Field(
        min_length=1,
    )

    source_requirement_references: list[str] = Field(
        min_length=1,
    )

    business_rules_applied: list[str]
    dependencies: list[str]

    priority: Priority
    priority_justification: str

    invest_assessment: InvestAssessment

    may_require_further_splitting: bool
    splitting_reason: str | None = None


class UserStoryGenerationResponse(BaseModel):
    requirement_summary: str = Field(
        min_length=10,
    )

    confirmed_actors: list[str]

    identified_user_goals: list[str] = Field(
        min_length=1,
    )

    generated_stories: list[GeneratedUserStory] = Field(
        min_length=1,
    )

    splitting_summary: str

    assumptions: list[str]
    ambiguities: list[str]
    missing_information: list[str]
    risks: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )
import logging

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

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
    """
    Convert a requirement into structured,
    traceable user stories.
    """

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