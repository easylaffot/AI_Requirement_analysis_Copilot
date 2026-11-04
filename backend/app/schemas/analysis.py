from typing import Literal

from pydantic import BaseModel, Field


class IncidentAnalysisResponse(BaseModel):
    incident_summary: str = Field(
        min_length=10,
        description="Concise factual summary of the incident",
    )

    confirmed_evidence: list[str] = Field(
        min_length=1,
        description=(
            "Facts explicitly supported by the supplied incident data"
        ),
    )

    business_impact: str = Field(
        min_length=10,
        description=(
            "Customer, operational, financial, or service impact"
        ),
    )

    root_cause_hypothesis: str = Field(
        min_length=10,
        description=(
            "Possible cause based only on available evidence, "
            "clearly identified as unconfirmed"
        ),
    )

    assumptions: list[str] = Field(
        description=(
            "Necessary assumptions that require human validation"
        ),
    )

    missing_information: list[str] = Field(
        description=(
            "Information required for further analysis or validation"
        ),
    )

    functional_requirements: list[str] = Field(
        min_length=1,
        description="Atomic and testable functional requirements",
    )

    user_story: str = Field(
        min_length=10,
        description="User story in As-I want-so that format",
    )

    acceptance_criteria: list[str] = Field(
        min_length=1,
        description="Testable Given-When-Then criteria",
    )

    risks: list[str] = Field(
        min_length=1,
        description="Risks supported by the incident information",
    )

    priority: Literal[
        "Critical",
        "High",
        "Medium",
        "Low",
    ]

    priority_justification: str = Field(
        min_length=10,
        description=(
            "Evidence-based explanation for the recommended priority"
        ),
    )

    human_validation_required: list[str] = Field(
        min_length=1,
        description=(
            "Items that a business analyst or technical team must verify"
        ),
    )