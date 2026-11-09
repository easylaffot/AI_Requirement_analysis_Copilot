from typing import Literal

from pydantic import BaseModel, Field


AmbiguityCategory = Literal[
    "Vague Term",
    "Undefined Actor",
    "Undefined Object",
    "Missing Condition",
    "Missing Boundary",
    "Missing Quantity",
    "Missing Timing",
    "Optionality",
    "Subjective Language",
    "Unclear Reference",
    "Compound Requirement",
    "Conflicting Interpretation",
    "Undefined Outcome",
    "Undefined Error Behavior",
]

Severity = Literal[
    "High",
    "Medium",
    "Low",
]

RequirementQualityStatus = Literal[
    "Clear",
    "Needs Clarification",
    "Not Ready",
]


class AmbiguityAnalysisRequest(BaseModel):
    requirement_id: str = Field(
        min_length=2,
        max_length=100,
    )

    requirement_title: str = Field(
        min_length=3,
        max_length=200,
    )

    requirement_text: str = Field(
        min_length=10,
        max_length=10000,
    )

    business_context: str = Field(
        min_length=10,
        max_length=5000,
    )

    known_actors: list[str] = Field(
        default_factory=list,
    )

    known_business_rules: list[str] = Field(
        default_factory=list,
    )

    additional_instructions: str | None = Field(
        default=None,
        max_length=1000,
    )


class PossibleInterpretation(BaseModel):
    interpretation_id: str
    interpretation: str
    supported_by_input: bool
    notes: str


class AmbiguityFinding(BaseModel):
    finding_id: str

    category: AmbiguityCategory

    ambiguous_text: str

    explanation: str

    severity: Severity

    interpretation_risk: str

    possible_interpretations: list[
        PossibleInterpretation
    ] = Field(
        min_length=1,
    )

    clarification_questions: list[str] = Field(
        min_length=1,
    )

    source_reference: str

    requires_human_validation: bool

    validation_owner: str


class SuggestedRewrite(BaseModel):
    rewrite_id: str

    rewritten_requirement: str

    status: Literal[
        "Ready",
        "Conditional",
        "Cannot Rewrite Safely",
    ]

    unresolved_placeholders: list[str]

    assumptions_used: list[str]

    source_finding_ids: list[str]


class AmbiguityAnalysisResponse(BaseModel):
    requirement_summary: str = Field(
        min_length=10,
    )

    confirmed_information: list[str]

    ambiguity_findings: list[AmbiguityFinding]

    overall_status: RequirementQualityStatus

    overall_score: int = Field(
        ge=0,
        le=100,
    )

    score_explanation: str

    suggested_rewrites: list[SuggestedRewrite]

    assumptions: list[str]

    missing_information: list[str]

    risks: list[str]    
    human_validation_required: list[str] = Field(
    default_factory=list,
)
