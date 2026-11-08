from typing import Literal

from pydantic import BaseModel, Field


RequirementType = Literal[
    "Functional",
    "Non-Functional",
    "Business Rule",
    "Data",
    "Security",
    "Privacy",
    "Compliance",
    "Integration",
    "Constraint",
    "Assumption",
    "Business Goal",
    "Scope",
    "Unknown",
]

RequirementSubtype = Literal[
    "User Interaction",
    "Workflow",
    "Validation",
    "Calculation",
    "Notification",
    "Authorization",
    "Authentication",
    "Data Capture",
    "Data Retrieval",
    "Data Retention",
    "Auditability",
    "Performance",
    "Availability",
    "Reliability",
    "Scalability",
    "Recoverability",
    "Accessibility",
    "Usability",
    "Maintainability",
    "Observability",
    "External Integration",
    "Policy",
    "Eligibility",
    "Restriction",
    "Business Objective",
    "Project Boundary",
    "Unclassified",
]

Confidence = Literal[
    "High",
    "Medium",
    "Low",
]

ClassificationStatus = Literal[
    "Classified",
    "Needs Clarification",
    "Mixed Requirement",
]

RequirementQuality = Literal[
    "Clear",
    "Partially Clear",
    "Ambiguous",
    "Incomplete",
]

Priority = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
    "Unknown",
]


class RequirementClassificationItem(BaseModel):
    requirement_id: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    requirement_text: str = Field(
        min_length=10,
        max_length=10000,
    )

    source_document: str | None = Field(
        default=None,
        max_length=300,
    )

    source_section: str | None = Field(
        default=None,
        max_length=200,
    )


class RequirementClassificationRequest(BaseModel):
    analysis_title: str = Field(
        min_length=3,
        max_length=200,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    business_domain: str = Field(
        min_length=2,
        max_length=100,
    )

    requirements: list[
        RequirementClassificationItem
    ] = Field(
        min_length=1,
        max_length=100,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class ClassificationEvidence(BaseModel):
    evidence_text: str
    explanation: str


class ClassificationLabel(BaseModel):
    requirement_type: RequirementType
    requirement_subtype: RequirementSubtype
    confidence: Confidence
    rationale: str
    evidence: list[ClassificationEvidence]


class ClassifiedRequirement(BaseModel):
    requirement_id: str
    original_title: str
    original_text: str

    primary_classification: ClassificationLabel

    secondary_classifications: list[
        ClassificationLabel
    ]

    classification_status: ClassificationStatus

    requirement_quality: RequirementQuality

    quality_explanation: str

    suggested_priority: Priority

    priority_rationale: str

    contains_multiple_requirements: bool

    splitting_recommended: bool

    splitting_reason: str | None = None

    missing_information: list[str]

    clarification_questions: list[str]

    requires_human_validation: bool

    validation_owner: str


class ClassificationSummaryEntry(BaseModel):
    requirement_type: RequirementType
    count: int = Field(ge=0)
    requirement_ids: list[str]


class RequirementClassificationResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    classified_requirements: list[
        ClassifiedRequirement
    ] = Field(
        min_length=1,
    )

    classification_summary: list[
        ClassificationSummaryEntry
    ] = Field(
        min_length=1,
    )

    mixed_requirement_ids: list[str]

    unclear_requirement_ids: list[str]

    assumptions: list[str]

    risks: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )