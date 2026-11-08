from typing import get_args

import pytest

from app.evaluation.ambiguity_evaluator import evaluate_ambiguity_response
from app.schemas.ambiguity import AmbiguityCategory, Severity
from app.services.ambiguity_service import AmbiguityService
from tests.ambiguity_evaluation_cases import (
    EVALUATION_CASES,
    AmbiguityEvaluationCase,
)


def test_ambiguity_evaluation_cases_are_synthetic_and_complete() -> None:
    expected_case_ids = {
        "clear_measurable_payment_limit",
        "vague_and_subjective_claim_processing",
        "undefined_actor_and_object",
        "missing_timing_amount_boundary_and_channel",
        "compound_optional_order_update_and_notification",
    }

    assert {case["case_id"] for case in EVALUATION_CASES} == expected_case_ids
    assert all(
        case["request"].requirement_id
        and case["request"].requirement_title
        and case["request"].requirement_text
        and case["request"].business_context
        for case in EVALUATION_CASES
    )
    assert all(
        len(case["request"].requirement_text) >= 10
        and len(case["request"].requirement_text) <= 10000
        and len(case["request"].business_context) >= 10
        and len(case["request"].business_context) <= 5000
        for case in EVALUATION_CASES
    )
    assert set(get_args(AmbiguityCategory))
    assert set(get_args(Severity)) == {"High", "Medium", "Low"}


@pytest.mark.asyncio
@pytest.mark.live_ai
@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[case["case_id"] for case in EVALUATION_CASES],
)
async def test_ambiguity_analysis_quality(
    evaluation_case: AmbiguityEvaluationCase,
) -> None:
    service = AmbiguityService()

    try:
        analysis = await service.analyze(evaluation_case["request"])
    finally:
        await service.close()

    result = evaluate_ambiguity_response(
        case_id=evaluation_case["case_id"],
        request=evaluation_case["request"],
        analysis=analysis,
        expected_missing_information=evaluation_case[
            "expected_missing_information"
        ],
        expected_defined_terms=evaluation_case["expected_defined_terms"],
        expected_status=evaluation_case["expected_status"],
        minimum_score=evaluation_case["minimum_score"],
        expected_optional_modality=evaluation_case[
            "expected_optional_modality"
        ],
        expect_notification_channel=evaluation_case[
            "expect_notification_channel"
        ],
        unresolved_rewrite_concepts=evaluation_case[
            "unresolved_rewrite_concepts"
        ],
        requires_cannot_rewrite_safely=evaluation_case[
            "requires_cannot_rewrite_safely"
        ],
    )
    failures = [
        f"{check.name}: {check.message}"
        for check in result.checks
        if not check.passed
    ]

    assert result.passed, (
        f"Evaluation score: {result.score}%\n"
        + "\n".join(failures)
    )
