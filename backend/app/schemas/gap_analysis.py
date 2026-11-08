from typing import Literal

from pydantic import BaseModel, Field


GapCategory = Literal[
    "Missing Actor",
    "Missing Business Rule",
    "Missing Data Definition",
    "Missing Condition",
    "Missing Boundary",
    "Missing Permission",
    "Missing Exception Handling",
    "Missing Failure Behavior",
    "Missing Dependency",
    "Missing Integration Detail",
    "Missing Security Requirement",
    "Missing Privacy Requirement",
    "Missing Audit Requirement",
    "Missing Performance Target",
    "Missing Availability Target",
    "Missing Recovery Target",
    "Missing Acceptance Information",
    "Missing Scope Decision",
    "Missing Priority",
    "Missing Ownership",
]

GapSeverity = Literal["High", "Medium", "Low"]

GapStatus = Literal[
    "Confirmed Gap",
    "Potential Gap",
    "Not Applicable",
]

ReadinessStatus = Literal[
    "Ready",
    "Needs Clarification",
    "Not Ready",
]


class GapAnalysisRequest(BaseModel):
    requirement_id: str = Field(min_length=2, max_length=100)
    requirement_title: str = Field(min_length=3, max_length=200)
    requirement_text: str = Field(min_length=20, max_length=15000)
    business_context: str = Field(min_length=10, max_length=5000)
    known_actors: list[str] = Field(default_factory=list)
    known_business_rules: list[str] = Field(default_factory=list)
    known_constraints: list[str] = Field(default_factory=list)
    existing_acceptance_criteria: list[str] = Field(default_factory=list)
    additional_instructions: str | None = Field(default=None, max_length=1000)


class GapFinding(BaseModel):
    gap_id: str
    category: GapCategory
    title: str
    description: str
    severity: GapSeverity
    status: GapStatus
    evidence_from_input: list[str]
    missing_information: str
    impact: str
    clarification_questions: list[str] = Field(min_length=1)
    suggested_owner: str
    blocks_implementation: bool
    blocks_testing: bool
    requires_human_validation: bool


class CoverageArea(BaseModel):
    area: str
    covered: bool
    evidence: list[str]
    gap_ids: list[str]
    notes: str


class GapAnalysisResponse(BaseModel):
    requirement_summary: str = Field(min_length=10)
    confirmed_information: list[str]
    gap_findings: list[GapFinding]
    coverage_assessment: list[CoverageArea] = Field(min_length=1)
    readiness_status: ReadinessStatus
    readiness_score: int = Field(ge=0, le=100)
    score_explanation: str
    assumptions: list[str]
    risks: list[str]
    recommended_next_actions: list[str]
    human_validation_required: list[str] = Field(min_length=1)
