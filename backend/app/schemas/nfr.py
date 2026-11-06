from typing import Literal

from pydantic import BaseModel, Field


NfrCategory = Literal[
    "Security",
    "Performance",
    "Availability",
    "Reliability",
    "Scalability",
    "Privacy",
    "Auditability",
    "Accessibility",
    "Usability",
    "Maintainability",
    "Observability",
    "Recoverability",
    "Compatibility",
    "Compliance",
]

DataSensitivity = Literal[
    "Public",
    "Internal",
    "Confidential",
    "Restricted",
    "Unknown",
]

Criticality = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
    "Unknown",
]

RecommendationStatus = Literal[
    "Ready",
    "Needs Target",
    "Needs Clarification",
]


class NfrRecommendationRequest(BaseModel):
    requirement_id: str = Field(
        min_length=2,
        max_length=100,
    )

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

    business_domain: str = Field(
        min_length=2,
        max_length=100,
    )

    data_sensitivity: DataSensitivity = "Unknown"
    criticality: Criticality = "Unknown"

    known_constraints: list[str] = Field(
        default_factory=list,
    )

    existing_nfrs: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class RecommendedNfr(BaseModel):
    nfr_id: str
    category: NfrCategory
    title: str
    requirement: str
    rationale: str

    source_references: list[str] = Field(
        min_length=1,
    )

    measurable: bool
    measurement_method: str

    status: RecommendationStatus

    missing_target: str | None = None

    assumptions: list[str]

    requires_human_validation: bool
    validation_reason: str | None = None


class NfrCategoryAssessment(BaseModel):
    category: NfrCategory
    relevant: bool
    rationale: str
    recommendation_ids: list[str]


class NfrRecommendationResponse(BaseModel):
    requirement_summary: str = Field(
        min_length=10,
    )

    relevant_categories: list[NfrCategoryAssessment] = Field(
        min_length=1,
    )

    recommendations: list[RecommendedNfr] = Field(
        min_length=1,
    )

    existing_nfr_coverage: list[str]

    duplicate_existing_nfrs: list[str]

    assumptions: list[str]

    ambiguities: list[str]

    missing_information: list[str]

    risks: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )