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

CoverageStatus = Literal[
    "Covered",
    "Partially Covered",
    "Not Covered",
    "Not Applicable",
]

TraceabilityStatus = Literal[
    "Valid",
    "Broken",
    "Missing",
    "Ambiguous",
]

ArtifactType = Literal[
    "Requirement",
    "User Story",
    "Acceptance Criterion",
    "Test Case",
]

RiskLevel = Literal[
    "High",
    "Medium",
    "Low",
]

ReadinessStatus = Literal[
    "Ready",
    "Needs Traceability Work",
    "Not Ready",
]


class TraceRequirementItem(BaseModel):
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


class TraceUserStoryItem(BaseModel):
    story_id: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    story_text: str = Field(
        min_length=10,
        max_length=5000,
    )

    source_requirement_ids: list[str] = Field(
        default_factory=list,
    )


class TraceAcceptanceCriterionItem(BaseModel):
    criterion_id: str = Field(
        min_length=2,
        max_length=100,
    )

    criterion_text: str = Field(
        min_length=10,
        max_length=5000,
    )

    source_story_ids: list[str] = Field(
        default_factory=list,
    )

    source_requirement_ids: list[str] = Field(
        default_factory=list,
    )


class TraceTestCaseItem(BaseModel):
    test_case_id: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    test_description: str = Field(
        min_length=10,
        max_length=5000,
    )

    source_criterion_ids: list[str] = Field(
        default_factory=list,
    )

    source_story_ids: list[str] = Field(
        default_factory=list,
    )

    source_requirement_ids: list[str] = Field(
        default_factory=list,
    )


class RequirementTraceabilityRequest(BaseModel):
    analysis_title: str = Field(
        min_length=3,
        max_length=200,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    requirements: list[TraceRequirementItem] = Field(
        min_length=1,
        max_length=100,
    )

    user_stories: list[TraceUserStoryItem] = Field(
        default_factory=list,
        max_length=300,
    )

    acceptance_criteria: list[
        TraceAcceptanceCriterionItem
    ] = Field(
        default_factory=list,
        max_length=500,
    )

    test_cases: list[TraceTestCaseItem] = Field(
        default_factory=list,
        max_length=500,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class TraceLink(BaseModel):
    link_id: str

    source_artifact_type: ArtifactType
    source_artifact_id: str

    target_artifact_type: ArtifactType
    target_artifact_id: str

    status: TraceabilityStatus

    explanation: str

    supported_by_explicit_reference: bool

    requires_human_validation: bool


class RequirementCoverageEntry(BaseModel):
    requirement_id: str

    coverage_status: CoverageStatus

    story_ids: list[str]

    criterion_ids: list[str]

    test_case_ids: list[str]

    coverage_explanation: str

    missing_coverage: list[str]

    requires_human_validation: bool


class OrphanArtifact(BaseModel):
    artifact_type: ArtifactType
    artifact_id: str

    reason: str

    suggested_action: str

    requires_human_validation: bool


class BrokenReference(BaseModel):
    source_artifact_type: ArtifactType
    source_artifact_id: str

    missing_target_type: ArtifactType
    missing_target_id: str

    impact: str

    suggested_action: str


class TraceabilityRisk(BaseModel):
    risk_id: str
    level: RiskLevel

    title: str
    description: str

    affected_artifact_ids: list[str]

    mitigation: str

    suggested_owner: str


class CoverageSummaryEntry(BaseModel):
    coverage_status: CoverageStatus

    count: int = Field(ge=0)

    requirement_ids: list[str]


class RequirementTraceabilityResponse(BaseModel):
    analysis_summary: str = Field(
        min_length=10,
    )

    trace_links: list[TraceLink]

    requirement_coverage: list[
        RequirementCoverageEntry
    ]

    orphan_artifacts: list[OrphanArtifact]

    broken_references: list[BrokenReference]

    coverage_summary: list[
        CoverageSummaryEntry
    ]

    traceability_risks: list[TraceabilityRisk]

    overall_coverage_percentage: int = Field(
        ge=0,
        le=100,
    )

    readiness_status: ReadinessStatus

    score_explanation: str

    assumptions: list[str]

    missing_information: list[str]

    recommended_next_actions: list[str]

    human_validation_required: list[str] = Field(
        min_length=1,
    )
