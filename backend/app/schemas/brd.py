from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]

RequirementCategory = Literal[
    "Functional",
    "Non-Functional",
    "Business Rule",
    "Data",
    "Security",
    "Compliance",
    "Integration",
    "Constraint",
]


class BrdAnalysisRequest(BaseModel):
    brd_title: str = Field(
        min_length=3,
        max_length=200,
    )

    project_name: str = Field(
        min_length=3,
        max_length=200,
    )

    business_domain: str = Field(
        min_length=2,
        max_length=100,
    )

    brd_content: str = Field(
        min_length=100,
        description="Complete BRD content supplied as plain text",
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class ExtractedRequirement(BaseModel):
    requirement_id: str
    requirement_text: str
    category: RequirementCategory
    source_reference: str

    confidence: Literal[
        "High",
        "Medium",
        "Low",
    ]


class AcceptanceCriterion(BaseModel):
    criterion_id: str
    criterion: str


class UserStory(BaseModel):
    story_id: str
    title: str
    story: str
    acceptance_criteria: list[AcceptanceCriterion] = Field(
        min_length=1,
    )
    source_requirement_ids: list[str] = Field(
        min_length=1,
    )
    priority: Priority
    priority_justification: str
    dependencies: list[str]
    may_require_splitting: bool
    splitting_reason: str | None = None


class Feature(BaseModel):
    feature_id: str
    name: str
    description: str
    source_requirement_ids: list[str] = Field(
        min_length=1,
    )
    user_stories: list[UserStory] = Field(
        min_length=1,
    )


class Epic(BaseModel):
    epic_id: str
    name: str
    business_value: str
    source_requirement_ids: list[str] = Field(
        min_length=1,
    )
    features: list[Feature] = Field(
        min_length=1,
    )


class TraceabilityEntry(BaseModel):
    requirement_id: str
    backlog_item_ids: list[str]
    coverage_status: Literal[
        "Covered",
        "Partially Covered",
        "Not Covered",
    ]
    notes: str


class BrdAnalysisResponse(BaseModel):
    brd_summary: str = Field(
        min_length=20,
    )

    business_problem: str = Field(
        min_length=10,
    )

    business_goals: list[str] = Field(
        min_length=1,
    )

    stakeholders_and_actors: list[str]

    confirmed_scope: list[str]

    extracted_requirements: list[ExtractedRequirement] = Field(
        min_length=1,
    )

    epics: list[Epic] = Field(
        min_length=1,
    )

    assumptions: list[str]

    ambiguities: list[str]

    missing_information: list[str]

    risks: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )

    traceability: list[TraceabilityEntry] = Field(
        min_length=1,
    )