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

Priority = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
    "Unknown",
]

PriorityMethod = Literal[
    "MoSCoW",
    "Value and Risk",
    "Evidence-Based Recommendation",
]

MoSCoWCategory = Literal[
    "Must Have",
    "Should Have",
    "Could Have",
    "Won't Have This Release",
    "Unclassified",
]

EvidenceStrength = Literal[
    "Strong",
    "Moderate",
    "Weak",
    "Insufficient",
]

ReadinessStatus = Literal[
    "Ready for Prioritization",
    "Needs Clarification",
    "Not Ready",
]


class PriorityRequirementItem(BaseModel):
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

    stated_priority: Priority = "Unknown"

    source_document: str | None = Field(
        default=None,
        max_length=300,
    )

    source_section: str | None = Field(
        default=None,
        max_length=200,
    )


class RequirementPriorityRequest(BaseModel):
    analysis_title: str = Field(
        min_length=3,
        max_length=200,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    release_objective: str = Field(
        min_length=10,
        max_length=2000,
    )

    prioritization_method: PriorityMethod = (
        "Evidence-Based Recommendation"
    )

    requirements: list[PriorityRequirementItem] = Field(
        min_length=1,
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


class PriorityEvidence(BaseModel):
    evidence_id: str
    source_reference: str
    evidence_text: str
    explanation: str


class PriorityFactor(BaseModel):
    factor: Literal[
        "Business Value",
        "Customer Impact",
        "Urgency",
        "Risk Reduction",
        "Compliance Need",
        "Security Need",
        "Dependency Importance",
        "Operational Impact",
        "Implementation Readiness",
    ]

    assessment: Literal[
        "High",
        "Medium",
        "Low",
        "Unknown",
    ]

    rationale: str

    evidence_ids: list[str]


class PrioritizedRequirement(BaseModel):
    requirement_id: str
    title: str

    recommended_priority: Priority
    moscow_category: MoSCoWCategory

    evidence_strength: EvidenceStrength

    priority_rationale: str

    factors: list[PriorityFactor]

    evidence: list[PriorityEvidence]

    dependency_ids: list[str]

    priority_conflict_detected: bool
    priority_conflict_explanation: str | None = None

    implementation_ready: bool
    readiness_explanation: str

    missing_information: list[str]
    clarification_questions: list[str]

    requires_human_validation: bool
    suggested_owner: str


class PrioritySummaryEntry(BaseModel):
    priority: Priority
    count: int = Field(ge=0)
    requirement_ids: list[str]


class RequirementPriorityResponse(BaseModel):
    analysis_summary: str = Field(min_length=10)

    release_objective_summary: str

    prioritized_requirements: list[
        PrioritizedRequirement
    ] = Field(min_length=1)

    priority_summary: list[
        PrioritySummaryEntry
    ] = Field(min_length=1)

    recommended_delivery_order: list[str]

    blocking_requirement_ids: list[str]

    readiness_status: ReadinessStatus

    assumptions: list[str]
    missing_information: list[str]
    risks: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )