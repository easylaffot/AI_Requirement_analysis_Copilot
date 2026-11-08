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

ConflictType = Literal[
    "Direct Contradiction",
    "Permission Conflict",
    "Boundary Conflict",
    "Timing Conflict",
    "Workflow Conflict",
    "Data Conflict",
    "Channel Conflict",
    "Priority Conflict",
    "Scope Conflict",
    "Terminology Conflict",
    "Potential Conflict",
]

ConflictSeverity = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]

ResolutionStatus = Literal[
    "Requires Decision",
    "Requires Clarification",
    "Can Coexist",
    "No Conflict",
]

RecommendedAction = Literal[
    "Select One Requirement",
    "Rewrite Conflicting Requirements",
    "Define Conditional Rules",
    "Define Source Authority",
    "Split Scope",
    "Clarify Terminology",
    "Keep Both",
    "No Action",
]


class ConflictRequirementItem(BaseModel):
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

    category: RequirementCategory = "Unknown"

    source_document: str | None = Field(
        default=None,
        max_length=300,
    )

    source_section: str | None = Field(
        default=None,
        max_length=200,
    )

    source_authority: str | None = Field(
        default=None,
        max_length=200,
    )


class ConflictAnalysisRequest(BaseModel):
    analysis_title: str = Field(
        min_length=3,
        max_length=200,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    requirements: list[ConflictRequirementItem] = Field(
        min_length=2,
        max_length=100,
    )

    known_business_rules: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class RequirementValue(BaseModel):
    requirement_id: str
    value: str


class ConflictDifference(BaseModel):
    comparison_area: str
    requirement_values: list[RequirementValue]
    conflict_reason: str


class ConflictFinding(BaseModel):
    conflict_id: str

    requirement_ids: list[str] = Field(
        min_length=2,
    )

    conflict_type: ConflictType
    severity: ConflictSeverity

    summary: str
    explanation: str

    conflicting_statements: list[RequirementValue]

    differences: list[ConflictDifference]

    business_impact: str
    implementation_impact: str
    testing_impact: str

    resolution_status: ResolutionStatus

    recommended_action: RecommendedAction
    action_rationale: str

    clarification_questions: list[str] = Field(
        min_length=1,
    )

    source_references: list[str] = Field(
        min_length=2,
    )

    requires_human_validation: bool
    suggested_owner: str


class RequirementConflictRelationship(BaseModel):
    requirement_id: str
    conflicting_requirement_ids: list[str]
    conflict_ids: list[str]
    conflict_free: bool
    notes: str


class ConflictAnalysisResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    confirmed_information: list[str]

    conflict_findings: list[ConflictFinding]

    requirement_relationships: list[
        RequirementConflictRelationship
    ]

    critical_conflict_count: int = Field(ge=0)
    high_conflict_count: int = Field(ge=0)
    medium_conflict_count: int = Field(ge=0)
    low_conflict_count: int = Field(ge=0)
    conflict_free_requirement_count: int = Field(ge=0)

    unresolved_decisions: list[str]
    assumptions: list[str]
    missing_information: list[str]
    risks: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )