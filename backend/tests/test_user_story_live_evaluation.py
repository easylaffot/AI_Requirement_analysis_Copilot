import pytest

from app.evaluation.user_story_evaluator import (
    evaluate_user_story_generation,
)
from app.services.user_story_service import UserStoryService
from tests.user_story_evaluation_cases import (
    EVALUATION_CASES,
    UserStoryEvaluationCase,
)


def test_user_story_evaluation_cases_are_synthetic_and_complete() -> None:
    expected_case_ids = {
        "simple_atomic_requirement",
        "independent_crud_actions",
        "actors_with_distinct_permissions",
        "confirmed_restriction_requires_negative_criteria",
        "incomplete_requirement",
    }

    assert {
        case["case_id"]
        for case in EVALUATION_CASES
    } == expected_case_ids

    assert all(
        len(case["request"].requirement_text) >= 20
        for case in EVALUATION_CASES
    )


@pytest.mark.asyncio
@pytest.mark.live_ai
@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[
        case["case_id"]
        for case in EVALUATION_CASES
    ],
)
async def test_user_story_generation_quality(
    evaluation_case: UserStoryEvaluationCase,
) -> None:
    service = UserStoryService()

    try:
        analysis = await service.generate(
            evaluation_case["request"]
        )
    finally:
        await service.close()

    result = evaluate_user_story_generation(
        case_id=evaluation_case["case_id"],
        analysis=analysis,
        request=evaluation_case["request"],
        confirmed_restrictions=evaluation_case[
            "confirmed_restrictions"
        ],
        confirmed_boundaries=evaluation_case[
            "confirmed_boundaries"
        ],
        expected_missing_topics=evaluation_case[
            "expected_missing_topics"
        ],
        minimum_story_count=evaluation_case[
            "minimum_story_count"
        ],
        estimable_should_be_false=evaluation_case[
            "estimable_should_be_false"
        ],
        priority_is_explicit=evaluation_case[
            "priority_is_explicit"
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