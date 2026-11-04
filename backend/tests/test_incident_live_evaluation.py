import pytest

from app.evaluation.incident_evaluator import (
    evaluate_analysis,
)
from app.services.incident_service import IncidentService
from tests.evaluation_cases import EVALUATION_CASES


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.live_ai,
]


@pytest.mark.parametrize(
    "evaluation_case",
    EVALUATION_CASES,
    ids=[
        case["case_id"]
        for case in EVALUATION_CASES
    ],
)
async def test_incident_analysis_quality(
    evaluation_case: dict,
) -> None:
    service = IncidentService()

    try:
        analysis = await service.analyze(
            evaluation_case["incident"]
        )
    finally:
        await service.close()

    result = evaluate_analysis(
        case_id=evaluation_case["case_id"],
        analysis=analysis,
        forbidden_claims=evaluation_case[
            "forbidden_claims"
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