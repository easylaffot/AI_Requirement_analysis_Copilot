from typing import Literal

from pydantic import BaseModel, Field


CriterionType = Literal[
    "Positive",
    "Negative",
    "Boundary",
    "Permission",
    "Business Rule",
    "Failure",
]

CoverageStatus = Literal[
    "Covered",
    "Partially Covered",
    "Not Covered",
]


class AcceptanceCriteriaRequest(BaseModel):
    story_id: str = Field(min_length=2, max_length=100)
    story_title: str = Field(min_length=3, max_length=200)
    user_story: str = Field(min_length=20, max_length=5000)
    business_context: str = Field(min_length=10, max_length=5000)

    business_rules: list[str] = Field(default_factory=list)
    known_constraints: list[str] = Field(default_factory=list)
    existing_acceptance_criteria: list[str] = Field(
        default_factory=list
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class GeneratedAcceptanceCriterion(BaseModel):
    criterion_id: str
    criterion_type: CriterionType
    title: str

    given: str
    when: str
    then: str

    criterion: str = Field(
        description="Complete criterion in Given-When-Then format"
    )

    source_references: list[str] = Field(min_length=1)
    business_rules_applied: list[str]

    testable: bool
    testability_reason: str

    requires_human_validation: bool
    validation_reason: str | None = None


class CoverageEntry(BaseModel):
    coverage_area: str
    status: CoverageStatus
    criterion_ids: list[str]
    notes: str


class AcceptanceCriteriaResponse(BaseModel):
    story_summary: str = Field(min_length=10)

    confirmed_actor: str
    confirmed_goal: str
    confirmed_business_value: str

    preconditions: list[str]

    generated_criteria: list[
        GeneratedAcceptanceCriterion
    ] = Field(min_length=1)

    coverage: list[CoverageEntry] = Field(min_length=1)

    assumptions: list[str]
    ambiguities: list[str]
    missing_information: list[str]
    risks: list[str]

    duplicate_existing_criteria: list[str]

    human_validation_required: list[str] = Field(min_length=1)