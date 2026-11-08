from typing import get_args

import pytest
from pydantic import ValidationError

from app.main import app
from app.schemas.gap_analysis import (
    CoverageArea,
    GapAnalysisRequest,
    GapAnalysisResponse,
    GapCategory,
    GapFinding,
    GapSeverity,
    GapStatus,
    ReadinessStatus,
)


def valid_request_data() -> dict[str, object]:
    return {
        "requirement_id": "REQ-GAP-101",
        "requirement_title": "Record an approved service request",
        "requirement_text": (
            "The service records an approved request and makes its current "
            "processing status available to the requester."
        ),
        "business_context": (
            "Approved service requests are tracked by the operations team."
        ),
    }


def test_valid_gap_analysis_request_is_accepted() -> None:
    request = GapAnalysisRequest(**valid_request_data())

    assert request.requirement_id == "REQ-GAP-101"
    assert request.known_actors == []
    assert request.known_business_rules == []
    assert request.known_constraints == []
    assert request.existing_acceptance_criteria == []
    assert request.additional_instructions is None


def test_request_shorter_than_minimum_is_rejected() -> None:
    data = valid_request_data()
    data["requirement_text"] = "Too short"

    with pytest.raises(ValidationError):
        GapAnalysisRequest(**data)


@pytest.mark.parametrize("score", [-1, 101])
def test_readiness_score_outside_range_is_rejected(score: int) -> None:
    response_data: dict[str, object] = {
        "requirement_summary": "A sufficiently long requirement summary.",
        "confirmed_information": [],
        "gap_findings": [],
        "coverage_assessment": [
            {
                "area": "Actors",
                "covered": True,
                "evidence": ["The requester submits the request."],
                "gap_ids": [],
                "notes": "Actor is identified.",
            }
        ],
        "readiness_status": "Ready",
        "readiness_score": score,
        "score_explanation": "The requirement is specific and testable.",
        "assumptions": [],
        "risks": [],
        "recommended_next_actions": [],
        "human_validation_required": ["Confirm the requirement owner."],
    }

    with pytest.raises(ValidationError):
        GapAnalysisResponse(**response_data)


def test_allowed_literal_values_validate() -> None:
    for category in get_args(GapCategory):
        GapFinding(
            gap_id="GAP-1",
            category=category,
            title="A gap",
            description="A grounded gap description.",
            severity="Medium",
            status="Potential Gap",
            evidence_from_input=[],
            missing_information="The missing decision.",
            impact="This affects implementation planning.",
            clarification_questions=["Which decision is required?"],
            suggested_owner="Product Owner",
            blocks_implementation=False,
            blocks_testing=False,
            requires_human_validation=True,
        )

    for severity in get_args(GapSeverity):
        GapFinding(
            gap_id="GAP-1",
            category="Missing Actor",
            title="A gap",
            description="A grounded gap description.",
            severity=severity,
            status="Confirmed Gap",
            evidence_from_input=[],
            missing_information="The missing decision.",
            impact="This affects implementation planning.",
            clarification_questions=["Which actor is responsible?"],
            suggested_owner="Product Owner",
            blocks_implementation=False,
            blocks_testing=False,
            requires_human_validation=True,
        )

    for gap_status in get_args(GapStatus):
        GapFinding(
            gap_id="GAP-1",
            category="Missing Actor",
            title="A gap",
            description="A grounded gap description.",
            severity="Low",
            status=gap_status,
            evidence_from_input=[],
            missing_information="The missing decision.",
            impact="This affects implementation planning.",
            clarification_questions=["Which actor is responsible?"],
            suggested_owner="Product Owner",
            blocks_implementation=False,
            blocks_testing=False,
            requires_human_validation=True,
        )

    for readiness in get_args(ReadinessStatus):
        GapAnalysisResponse(
            requirement_summary="A sufficiently long requirement summary.",
            confirmed_information=[],
            gap_findings=[],
            coverage_assessment=[
                CoverageArea(
                    area="Actors",
                    covered=False,
                    evidence=[],
                    gap_ids=["GAP-1"],
                    notes="Actor needs clarification.",
                )
            ],
            readiness_status=readiness,
            readiness_score=50,
            score_explanation="The requirement needs further review.",
            assumptions=[],
            risks=[],
            recommended_next_actions=[],
            human_validation_required=["Review the requirement."],
        )


def test_gap_analysis_router_path_is_registered() -> None:
    assert "/api/gap-analysis/analyze" in app.openapi()["paths"]
