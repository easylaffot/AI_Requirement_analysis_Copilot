from typing import get_args

import pytest

from app.evaluation.nfr_evaluator import evaluate_nfr_response
from app.schemas.nfr import NfrCategory
from app.services.nfr_service import NfrService
from tests.nfr_evaluation_cases import (
    EVALUATION_CASES,
    NfrEvaluationCase,
)


def test_nfr_evaluation_cases_are_synthetic_and_complete() -> None:
    expected_case_ids = {
        "high_criticality_transaction_missing_targets",
        "restricted_data_security_privacy_review",
        "existing_nfr_duplicate_avoidance",
        "explicit_compatibility_constraint",
        "minimal_requirement_irrelevant_categories",
    }

    assert {case["case_id"] for case in EVALUATION_CASES} == expected_case_ids
    assert all(
        case["request"].requirement_id
        and case["request"].requirement_title
        and case["request"].requirement_text
        and case["request"].business_context
        and case["request"].business_domain
        for case in EVALUATION_CASES
    )
    allowed_categories = set(get_args(NfrCategory))
    for case in EVALUATION_CASES:
        relevant = set(case["expected_relevant_categories"])
        irrelevant = set(case["expected_irrelevant_categories"])
        assert relevant.isdisjoint(irrelevant)
        assert relevant | irrelevant == allowed_categories


@pytest.mark.asyncio
@pytest.mark.live_ai
@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[case["case_id"] for case in EVALUATION_CASES],
)
async def test_nfr_recommendation_quality(
    evaluation_case: NfrEvaluationCase,
) -> None:
    service = NfrService()

    try:
        analysis = await service.recommend(evaluation_case["request"])
    finally:
        await service.close()

    result = evaluate_nfr_response(evaluation_case, analysis)
    failures = [
        f"{check.name}: {check.message}"
        for check in result.checks
        if not check.passed
    ]

    assert result.passed, (
        f"Evaluation score: {result.score}%\n"
        + "\n".join(failures)
    )
