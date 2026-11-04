import re

from app.evaluation.models import (
    EvaluationCheck,
    EvaluationResult,
)
from app.schemas.analysis import IncidentAnalysisResponse


ALLOWED_PRIORITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
}

UNSUPPORTED_CAUSE_PHRASES = {
    "database failure",
    "database connection",
    "connection pool",
    "cache failure",
    "redis",
    "network failure",
    "resource exhaustion",
    "memory leak",
    "cpu exhaustion",
}

VAGUE_TERMS = {
    "quickly",
    "efficiently",
    "user-friendly",
    "acceptable performance",
    "as soon as possible",
}


def _passed(
    name: str,
    message: str,
) -> EvaluationCheck:
    return EvaluationCheck(
        name=name,
        passed=True,
        message=message,
    )


def _failed(
    name: str,
    message: str,
) -> EvaluationCheck:
    return EvaluationCheck(
        name=name,
        passed=False,
        message=message,
    )


def evaluate_analysis(
    case_id: str,
    analysis: IncidentAnalysisResponse,
    forbidden_claims: list[str] | None = None,
) -> EvaluationResult:
    checks: list[EvaluationCheck] = []
    forbidden_claims = forbidden_claims or []

    hypothesis = analysis.root_cause_hypothesis.lower()

    prohibited_phrases = (
        UNSUPPORTED_CAUSE_PHRASES
        | {claim.lower() for claim in forbidden_claims}
    )

    unsupported_phrases_found = [
        phrase
        for phrase in prohibited_phrases
        if phrase in hypothesis
    ]

    if unsupported_phrases_found:
        checks.append(
            _failed(
                "No unsupported root cause",
                "Unsupported root-cause wording found: "
                + ", ".join(unsupported_phrases_found),
            )
        )
    else:
        checks.append(
            _passed(
                "No unsupported root cause",
                "No prohibited unsupported cause was found.",
            )
        )

    invalid_requirements = [
        requirement
        for requirement in analysis.functional_requirements
        if not requirement.startswith("The system shall")
    ]

    if invalid_requirements:
        checks.append(
            _failed(
                'Requirements begin with "The system shall"',
                f"{len(invalid_requirements)} requirement(s) "
                "do not use the required format.",
            )
        )
    else:
        checks.append(
            _passed(
                'Requirements begin with "The system shall"',
                "All functional requirements use the required format.",
            )
        )

    vague_requirements = [
        requirement
        for requirement in analysis.functional_requirements
        if any(
            term in requirement.lower()
            for term in VAGUE_TERMS
        )
    ]

    if vague_requirements:
        checks.append(
            _failed(
                "Requirements avoid vague wording",
                f"{len(vague_requirements)} requirement(s) "
                "contain vague language.",
            )
        )
    else:
        checks.append(
            _passed(
                "Requirements avoid vague wording",
                "No configured vague terms were found.",
            )
        )

    invented_number_patterns = [
        r"\b\d+\s*(?:ms|milliseconds|seconds|minutes)\b",
        r"\b\d+(?:\.\d+)?%\b",
        r"\b99(?:\.\d+)?%\b",
    ]

    generated_requirement_text = " ".join(
        analysis.functional_requirements
    )

    invented_targets = [
        pattern
        for pattern in invented_number_patterns
        if re.search(
            pattern,
            generated_requirement_text,
            flags=re.IGNORECASE,
        )
    ]

    if invented_targets:
        checks.append(
            _failed(
                "No invented numerical targets",
                "A numerical target was found in the generated "
                "requirements. Human review is required.",
            )
        )
    else:
        checks.append(
            _passed(
                "No invented numerical targets",
                "No numerical targets were found in requirements.",
            )
        )

    invalid_criteria = [
        criterion
        for criterion in analysis.acceptance_criteria
        if not all(
            keyword in criterion
            for keyword in ("Given", "When", "Then")
        )
    ]

    if invalid_criteria:
        checks.append(
            _failed(
                "Acceptance criteria use Given-When-Then",
                f"{len(invalid_criteria)} acceptance criterion or "
                "criteria do not contain Given, When, and Then.",
            )
        )
    else:
        checks.append(
            _passed(
                "Acceptance criteria use Given-When-Then",
                "All acceptance criteria use the expected format.",
            )
        )

    if analysis.priority in ALLOWED_PRIORITIES:
        checks.append(
            _passed(
                "Priority uses an allowed value",
                f"Priority is {analysis.priority}.",
            )
        )
    else:
        checks.append(
            _failed(
                "Priority uses an allowed value",
                f"Unexpected priority: {analysis.priority}",
            )
        )

    if analysis.missing_information:
        checks.append(
            _passed(
                "Missing information is identified",
                "The response identifies information requiring "
                "further investigation.",
            )
        )
    else:
        checks.append(
            _failed(
                "Missing information is identified",
                "No missing information was reported.",
            )
        )

    if analysis.human_validation_required:
        checks.append(
            _passed(
                "Human validation is present",
                "Human-validation items were generated.",
            )
        )
    else:
        checks.append(
            _failed(
                "Human validation is present",
                "No human-validation items were generated.",
            )
        )

    passed_count = sum(
        check.passed
        for check in checks
    )

    score = round(
        passed_count / len(checks) * 100,
        2,
    )

    return EvaluationResult(
        case_id=case_id,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
        analysis=analysis,
    )
