import pytest

from app.evaluation.acceptance_criteria_evaluator import (
    evaluate_acceptance_criteria,
)
from app.services.acceptance_criteria_service import (
    AcceptanceCriteriaService,
)
from tests.acceptance_criteria_evaluation_cases import (
    EVALUATION_CASES,
    AcceptanceCriteriaEvaluationCase,
)


def test_acceptance_criteria_cases_are_synthetic_and_complete() -> None:
    expected_case_ids = {
        "simple_positive_processing_behavior",
        "restriction_requires_negative_behavior",
        "minimum_and_maximum_boundaries",
        "actor_based_permission_rule",
        "incomplete_story_missing_failure_behavior",
    }

    assert {case["case_id"] for case in EVALUATION_CASES} == expected_case_ids


@pytest.mark.asyncio
@pytest.mark.live_ai
@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[case["case_id"] for case in EVALUATION_CASES],
)
async def test_acceptance_criteria_quality(
    evaluation_case: AcceptanceCriteriaEvaluationCase,
) -> None:
    service = AcceptanceCriteriaService()

    try:
        analysis = await service.generate(evaluation_case["request"])
    finally:
        await service.close()

    result = evaluate_acceptance_criteria(
        case_id=evaluation_case["case_id"],
        analysis=analysis,
        request=evaluation_case["request"],
        confirmed_boundaries=evaluation_case["confirmed_boundaries"],
        confirmed_restrictions=evaluation_case["confirmed_restrictions"],
        expected_missing_information=evaluation_case[
            "expected_missing_information"
        ],
        unsupported_failure_behavior=evaluation_case[
            "unsupported_failure_behavior"
        ],
        accepted_for_processing_only=evaluation_case[
            "accepted_for_processing_only"
        ],
        contradictory_precondition_phrases=evaluation_case[
            "contradictory_precondition_phrases"
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
