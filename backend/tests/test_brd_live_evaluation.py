import pytest

from app.evaluation.brd_evaluator import evaluate_brd_analysis
from app.schemas.brd import BrdAnalysisRequest
from app.services.brd_service import BrdService
from tests.brd_evaluation_cases import EVALUATION_CASES, BrdEvaluationCase


def test_brd_evaluation_cases_are_synthetic_and_complete() -> None:
    expected_case_ids = {
        "complete_clear_functional_brd",
        "missing_and_undecided_information",
        "multiple_actors_with_distinct_permissions",
        "integration_with_unspecified_details",
        "oversized_workflow_requires_story_splitting",
    }

    assert {case["case_id"] for case in EVALUATION_CASES} == expected_case_ids
    assert all(len(case["brd_content"]) >= 100 for case in EVALUATION_CASES)


@pytest.mark.asyncio
@pytest.mark.live_ai
@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[case["case_id"] for case in EVALUATION_CASES],
)
async def test_brd_analysis_quality(
    evaluation_case: BrdEvaluationCase,
) -> None:
    request = BrdAnalysisRequest(
        brd_title=evaluation_case["brd_title"],
        project_name=evaluation_case["project_name"],
        business_domain=evaluation_case["business_domain"],
        brd_content=evaluation_case["brd_content"],
        additional_instructions=evaluation_case.get("additional_instructions"),
    )
    service = BrdService()

    try:
        analysis = await service.analyze(request)
    finally:
        await service.close()

    result = evaluate_brd_analysis(
        case_id=evaluation_case["case_id"],
        analysis=analysis,
        brd_content=evaluation_case["brd_content"],
        expected_missing_information=evaluation_case[
            "expected_missing_information"
        ],
        minimum_story_count=evaluation_case["minimum_story_count"],
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
