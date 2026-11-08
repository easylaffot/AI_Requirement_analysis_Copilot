from typing import Literal

from pydantic import BaseModel, Field


RequirementCategory = Literal[
    "Functional",
    "Non-Functional",
    "Business Rule",
    "Security",
    "Compliance",
    "Integration",
    "Constraint",
    "Unknown",
]

DuplicateClassification = Literal[
    "Exact Duplicate",
    "Semantic Duplicate",
    "Near Duplicate",
    "Partial Overlap",
    "Related but Distinct",
    "Not Duplicate",
]

RecommendedAction = Literal[
    "Keep Both",
    "Merge",
    "Remove One After Validation",
    "Rewrite Both",
    "Establish Parent-Child Relationship",
    "Clarify Before Deciding",
]

Confidence = Literal[
    "High",
    "Medium",
    "Low",
]


class RequirementItem(BaseModel):
    requirement_id: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=3, max_length=200)
    requirement_text: str = Field(
        min_length=10,
        max_length=10000,
    )

    category: RequirementCategory = "Unknown"

    source_document: str | None = Field(
        default=None,
        max_length=300,
    )

    source_section: str | None = Field(
        default=None,
        max_length=200,
    )


class DuplicateAnalysisRequest(BaseModel):
    analysis_title: str = Field(min_length=3, max_length=200)
    business_context: str = Field(min_length=10, max_length=5000)

    requirements: list[RequirementItem] = Field(
        min_length=2,
        max_length=100,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class RequirementDifference(BaseModel):
    requirement_id: str
    unique_information: list[str]


class DuplicateFinding(BaseModel):
    finding_id: str

    requirement_ids: list[str] = Field(min_length=2)

    classification: DuplicateClassification
    confidence: Confidence

    explanation: str
    shared_meaning: list[str]
    differences: list[RequirementDifference]

    conflict_detected: bool
    conflict_description: str | None = None

    recommended_action: RecommendedAction
    action_rationale: str

    consolidated_requirement: str | None = None

    source_references: list[str] = Field(min_length=2)

    requires_human_validation: bool
    validation_questions: list[str]


class RequirementRelationship(BaseModel):
    requirement_id: str
    related_requirement_ids: list[str]
    covered_by_finding_ids: list[str]
    standalone: bool
    notes: str


class DuplicateAnalysisResponse(BaseModel):
    analysis_summary: str = Field(min_length=10)

    findings: list[DuplicateFinding]

    requirement_relationships: list[
        RequirementRelationship
    ]

    exact_duplicate_count: int = Field(ge=0)
    semantic_duplicate_count: int = Field(ge=0)
    partial_overlap_count: int = Field(ge=0)
    distinct_requirement_count: int = Field(ge=0)

    conflicts: list[str]
    assumptions: list[str]
    missing_information: list[str]
    risks: list[str]

    human_validation_required: list[str] = Field(min_length=1)