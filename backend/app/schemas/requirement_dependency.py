from typing import Literal

from pydantic import BaseModel, Field


RequirementCategory = Literal[
    "Functional",
    "Non-Functional",
    "Business Rule",
    "Data",
    "Security",
    "Privacy",
    "Compliance",
    "Integration",
    "Constraint",
    "Unknown",
]

DependencyType = Literal[
    "Prerequisite",
    "Sequence",
    "Data",
    "Business Rule",
    "Permission",
    "Integration",
    "Technical",
    "External",
    "Shared Resource",
    "Potential Dependency",
]

DependencyStrength = Literal[
    "Hard",
    "Soft",
    "Potential",
]

DependencyConfidence = Literal[
    "High",
    "Medium",
    "Low",
]

DependencyStatus = Literal[
    "Confirmed",
    "Inferred",
    "Needs Clarification",
]

ReadinessStatus = Literal[
    "Ready",
    "Needs Clarification",
    "Blocked",
]


class DependencyRequirementItem(BaseModel):
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


class RequirementDependencyRequest(BaseModel):
    analysis_title: str = Field(
        min_length=3,
        max_length=200,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    requirements: list[DependencyRequirementItem] = Field(
        min_length=2,
        max_length=100,
    )

    known_dependencies: list[str] = Field(
        default_factory=list,
    )

    known_constraints: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class DependencyEvidence(BaseModel):
    source_reference: str
    evidence_text: str
    explanation: str


class RequirementDependencyFinding(BaseModel):
    dependency_id: str

    source_requirement_id: str
    target_requirement_id: str

    dependency_type: DependencyType
    dependency_strength: DependencyStrength
    status: DependencyStatus
    confidence: DependencyConfidence

    description: str
    rationale: str

    evidence: list[DependencyEvidence]

    delivery_impact: str
    testing_impact: str

    blocks_target: bool

    missing_information: list[str]
    clarification_questions: list[str]

    requires_human_validation: bool
    suggested_owner: str


class RequirementDependencyRelationship(BaseModel):
    requirement_id: str

    depends_on_requirement_ids: list[str]
    required_by_requirement_ids: list[str]

    dependency_ids: list[str]

    blocked: bool
    blocking_reasons: list[str]

    standalone: bool
    notes: str


class DeliveryStage(BaseModel):
    stage_number: int = Field(ge=1)
    stage_name: str
    requirement_ids: list[str]
    rationale: str


class DependencySummaryEntry(BaseModel):
    dependency_type: DependencyType
    count: int = Field(ge=0)
    dependency_ids: list[str]


class RequirementDependencyResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    confirmed_information: list[str]

    dependency_findings: list[
        RequirementDependencyFinding
    ]

    requirement_relationships: list[
        RequirementDependencyRelationship
    ]

    dependency_summary: list[
        DependencySummaryEntry
    ]

    recommended_delivery_stages: list[DeliveryStage]

    blocking_requirement_ids: list[str]

    circular_dependency_detected: bool
    circular_dependency_paths: list[str]

    readiness_status: ReadinessStatus

    assumptions: list[str]
    missing_information: list[str]
    risks: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )