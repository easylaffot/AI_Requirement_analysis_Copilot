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

RiskCategory = Literal[
    "Business",
    "Scope",
    "Requirement Quality",
    "Delivery",
    "Dependency",
    "Integration",
    "Data",
    "Security",
    "Privacy",
    "Compliance",
    "Operational",
    "Performance",
    "Availability",
    "Recoverability",
    "Testing",
    "Stakeholder",
]

RiskLikelihood = Literal[
    "High",
    "Medium",
    "Low",
    "Unknown",
]

RiskImpact = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]

RiskSeverity = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]

RiskStatus = Literal[
    "Confirmed Risk",
    "Potential Risk",
    "Needs Clarification",
]

MitigationStatus = Literal[
    "Ready",
    "Needs Decision",
    "Needs Specialist Review",
]

ReadinessStatus = Literal[
    "Ready",
    "Proceed with Caution",
    "Not Ready",
]


class RiskRequirementItem(BaseModel):
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


class RequirementRiskRequest(BaseModel):
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

    requirements: list[RiskRequirementItem] = Field(
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


class RiskEvidence(BaseModel):
    requirement_id: str
    evidence_text: str
    explanation: str


class RiskMitigation(BaseModel):
    mitigation_id: str
    action: str
    rationale: str
    owner: str
    status: MitigationStatus
    validation_required: bool


class RequirementRiskFinding(BaseModel):
    risk_id: str

    title: str

    category: RiskCategory

    status: RiskStatus

    likelihood: RiskLikelihood

    impact: RiskImpact

    severity: RiskSeverity

    risk_statement: str

    cause: str

    consequence: str

    affected_requirement_ids: list[str] = Field(
        min_length=1,
    )

    evidence: list[RiskEvidence] = Field(
        min_length=1,
    )

    assumptions: list[str]

    mitigation_actions: list[RiskMitigation]

    monitoring_indicators: list[str]

    blocks_implementation: bool

    blocks_testing: bool

    requires_human_validation: bool

    validation_questions: list[str]

    suggested_owner: str


class RequirementRiskRelationship(BaseModel):
    requirement_id: str
    risk_ids: list[str]
    highest_severity: RiskSeverity | None = None
    risk_free: bool
    notes: str


class RiskSummaryEntry(BaseModel):
    severity: RiskSeverity
    count: int = Field(ge=0)
    risk_ids: list[str]


class RequirementRiskResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    confirmed_information: list[str]

    risk_findings: list[RequirementRiskFinding]

    risk_summary: list[RiskSummaryEntry]

    requirement_relationships: list[
        RequirementRiskRelationship
    ]

    overall_readiness: ReadinessStatus

    overall_risk_score: int = Field(
        ge=0,
        le=100,
    )

    score_explanation: str

    assumptions: list[str]

    missing_information: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )