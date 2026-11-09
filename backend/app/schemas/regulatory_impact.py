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

ObligationCategory = Literal[
    "Access Control",
    "Data Protection",
    "Data Retention",
    "Consent",
    "Customer Communication",
    "Auditability",
    "Reporting",
    "Record Keeping",
    "Security",
    "Privacy",
    "Operational Control",
    "Business Process",
    "Other",
]

ImpactType = Literal[
    "New Requirement",
    "Requirement Update",
    "Requirement Removal",
    "Control Update",
    "Process Update",
    "Testing Update",
    "Documentation Update",
    "Potential Impact",
    "No Impact",
]

CoverageStatus = Literal[
    "Covered",
    "Partially Covered",
    "Not Covered",
    "Potentially Covered",
    "Not Applicable",
]

ImpactSeverity = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]

Confidence = Literal[
    "High",
    "Medium",
    "Low",
]

ReadinessStatus = Literal[
    "Ready for Review",
    "Needs Clarification",
    "Not Ready",
]


class RegulatoryObligationItem(BaseModel):
    obligation_id: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=3,
        max_length=300,
    )

    obligation_text: str = Field(
        min_length=10,
        max_length=10000,
    )

    category: ObligationCategory = "Other"

    source_name: str = Field(
        min_length=2,
        max_length=300,
    )

    source_section: str | None = Field(
        default=None,
        max_length=300,
    )

    effective_date: str | None = Field(
        default=None,
        max_length=100,
    )

    jurisdiction: str | None = Field(
        default=None,
        max_length=200,
    )


class RegulatoryRequirementItem(BaseModel):
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


class RegulatoryImpactRequest(BaseModel):
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

    obligations: list[RegulatoryObligationItem] = Field(
        min_length=1,
        max_length=100,
    )

    requirements: list[RegulatoryRequirementItem] = Field(
        min_length=1,
        max_length=200,
    )

    known_controls: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class RegulatoryEvidence(BaseModel):
    source_type: Literal[
        "Regulatory Obligation",
        "Requirement",
        "Known Control",
    ]

    source_reference: str
    evidence_text: str
    explanation: str


class RegulatoryImpactFinding(BaseModel):
    impact_id: str

    obligation_ids: list[str] = Field(
        min_length=1,
    )

    affected_requirement_ids: list[str]

    impact_type: ImpactType

    coverage_status: CoverageStatus

    severity: ImpactSeverity

    confidence: Confidence

    title: str
    explanation: str

    current_coverage: str
    coverage_gap: str

    business_impact: str
    implementation_impact: str
    testing_impact: str
    operational_impact: str

    evidence: list[RegulatoryEvidence] = Field(
        min_length=1,
    )

    recommended_requirement_action: str

    proposed_requirement_text: str | None = None

    validation_questions: list[str]

    requires_human_validation: bool

    suggested_owner: str


class ObligationCoverageEntry(BaseModel):
    obligation_id: str

    coverage_status: CoverageStatus

    requirement_ids: list[str]

    impact_ids: list[str]

    coverage_explanation: str

    missing_coverage: list[str]

    requires_human_validation: bool


class RequirementImpactEntry(BaseModel):
    requirement_id: str

    impacted: bool

    obligation_ids: list[str]

    impact_ids: list[str]

    highest_severity: ImpactSeverity | None = None

    recommended_action: str

    notes: str


class ImpactSummaryEntry(BaseModel):
    severity: ImpactSeverity

    count: int = Field(ge=0)

    impact_ids: list[str]


class RegulatoryImpactResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    confirmed_information: list[str]

    impact_findings: list[RegulatoryImpactFinding]

    obligation_coverage: list[
        ObligationCoverageEntry
    ]

    requirement_impacts: list[
        RequirementImpactEntry
    ]

    impact_summary: list[ImpactSummaryEntry]

    impacted_requirement_ids: list[str]

    uncovered_obligation_ids: list[str]

    potential_conflicts: list[str]

    readiness_status: ReadinessStatus

    assumptions: list[str]

    missing_information: list[str]

    risks: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )