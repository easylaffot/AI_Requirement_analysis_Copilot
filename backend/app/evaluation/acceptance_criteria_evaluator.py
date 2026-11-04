import re
from collections import Counter

from pydantic import BaseModel

from app.schemas.acceptance_criteria import (
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
)


ALLOWED_CRITERION_TYPES = {
    "Positive",
    "Negative",
    "Boundary",
    "Permission",
    "Business Rule",
    "Failure",
}
REQUIRED_COVERAGE_AREAS = (
    "Positive",
    "Negative",
    "Boundary",
    "Permission",
    "Business Rule",
    "Failure",
)
NUMBER_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\b")
IDENTIFIER_PATTERN = re.compile(
    r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b",
    re.IGNORECASE,
)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "when",
    "with",
}


class AcceptanceCriteriaEvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class AcceptanceCriteriaEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[AcceptanceCriteriaEvaluationCheck]
    analysis: AcceptanceCriteriaResponse


def _record_check(
    checks: list[AcceptanceCriteriaEvaluationCheck],
    name: str,
    failures: list[str],
    success_message: str,
) -> None:
    checks.append(
        AcceptanceCriteriaEvaluationCheck(
            name=name,
            passed=not failures,
            message="; ".join(failures) if failures else success_message,
        )
    )


def _request_text(request: AcceptanceCriteriaRequest) -> str:
    return " ".join(
        [
            request.story_id,
            request.story_title,
            request.user_story,
            request.business_context,
            *request.business_rules,
            *request.known_constraints,
            *request.existing_acceptance_criteria,
            request.additional_instructions or "",
        ]
    )


def _criterion_text(criterion: object) -> str:
    return " ".join(
        (
            getattr(criterion, "title"),
            getattr(criterion, "given"),
            getattr(criterion, "when"),
            getattr(criterion, "then"),
            getattr(criterion, "criterion"),
        )
    )


def _normalized_tokens(text: str) -> set[str]:
    text = IDENTIFIER_PATTERN.sub(" ", text.lower())
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text)
        if len(token) > 1 and token not in STOP_WORDS
    }


def _overlap_score(left: str, right: str) -> float:
    left_tokens = _normalized_tokens(left)
    right_tokens = _normalized_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(
        len(left_tokens),
        len(right_tokens),
    )


def _coverage_area_matches(area: str, category: str) -> bool:
    normalized_area = area.lower().replace("-", " ")
    normalized_category = category.lower()
    aliases = {
        "business rule": ("business rule", "business-rule", "rule"),
        "positive": ("positive", "successful"),
        "negative": ("negative", "invalid", "prohibited"),
        "boundary": ("boundary", "limit", "minimum", "maximum"),
        "permission": ("permission", "authorization", "access control"),
        "failure": ("failure", "error", "exception"),
    }
    return any(alias in normalized_area for alias in aliases[normalized_category])


def _boundary_scenario_present(
    criterion_text: str,
    *,
    value: str,
    direction: str,
    neighbor: str,
) -> bool:
    text = criterion_text.lower()

    value_pattern = rf"(?<!\d){re.escape(value)}(?!\d)"
    neighbor_pattern = rf"(?<!\d){re.escape(neighbor)}(?!\d)"

    has_boundary_value = bool(
        re.search(value_pattern, text)
    )

    has_neighbor_value = bool(
        re.search(neighbor_pattern, text)
    )

    if direction == "at":
        return has_boundary_value and any(
            term in text
            for term in (
                "amount",
                "value",
                "limit",
                "minimum",
                "maximum",
            )
        )

    if direction == "below":
        semantic_patterns = (
            rf"\bbelow\s+\$?{re.escape(value)}\b",
            rf"\bless\s+than\s+\$?{re.escape(value)}\b",
            rf"\bunder\s+\$?{re.escape(value)}\b",
        )

        semantic_phrases = (
            "below the minimum",
            "less than the minimum",
            "under the minimum",
        )

        return (
            has_neighbor_value
            or any(
                re.search(pattern, text)
                for pattern in semantic_patterns
            )
            or any(
                phrase in text
                for phrase in semantic_phrases
            )
        )

    if direction == "above":
        semantic_patterns = (
            rf"\babove\s+\$?{re.escape(value)}\b",
            rf"\bgreater\s+than\s+\$?{re.escape(value)}\b",
            rf"\bmore\s+than\s+\$?{re.escape(value)}\b",
            rf"\bover\s+\$?{re.escape(value)}\b",
        )

        semantic_phrases = (
            "above the maximum",
            "greater than the maximum",
            "more than the maximum",
            "over the maximum",
        )

        return (
            has_neighbor_value
            or any(
                re.search(pattern, text)
                for pattern in semantic_patterns
            )
            or any(
                phrase in text
                for phrase in semantic_phrases
            )
        )

    return False

def _has_duplicate_pair(
    existing: list[str],
) -> bool:
    return any(
        _overlap_score(
            existing[left],
            existing[right],
        )
        >= 0.65
        for left in range(len(existing))
        for right in range(left + 1, len(existing))
    )

def evaluate_acceptance_criteria(
    case_id: str,
    analysis: AcceptanceCriteriaResponse,
    request: AcceptanceCriteriaRequest,
    *,
    confirmed_boundaries: list[dict[str, str]] | None = None,
    confirmed_restrictions: bool = False,
    expected_missing_information: list[str] | None = None,
    unsupported_failure_behavior: bool = False,
    accepted_for_processing_only: bool = False,
    contradictory_precondition_phrases: list[str] | None = None,
) -> AcceptanceCriteriaEvaluationResult:
    checks: list[AcceptanceCriteriaEvaluationCheck] = []
    criteria = analysis.generated_criteria
    criterion_ids = [criterion.criterion_id for criterion in criteria]
    valid_criterion_ids = set(criterion_ids)
    existing_ids = {
        f"EXISTING-AC-{index:03d}"
        for index, _ in enumerate(
            request.existing_acceptance_criteria,
            start=1,
        )
    }
    valid_coverage_ids = valid_criterion_ids | existing_ids
    confirmed_boundaries = confirmed_boundaries or []
    expected_missing_information = expected_missing_information or []
    contradictory_precondition_phrases = (
        contradictory_precondition_phrases or []
    )

    _record_check(
        checks,
        "At least one generated criterion exists",
        [] if criteria else ["No acceptance criteria were generated."],
        f"Generated {len(criteria)} criterion/criteria.",
    )

    duplicate_ids = [
        criterion_id
        for criterion_id, count in Counter(criterion_ids).items()
        if count > 1
    ]
    _record_check(
        checks,
        "Criterion IDs are unique",
        [f"Criterion ID {criterion_id} appears more than once."
         for criterion_id in duplicate_ids],
        "All generated criterion IDs are unique.",
    )

    missing_gherkin_parts = [
        criterion.criterion_id
        for criterion in criteria
        if not all(
            re.search(rf"\b{part}\b", criterion.criterion, re.IGNORECASE)
            for part in ("Given", "When", "Then")
        )
    ]
    _record_check(
        checks,
        "Every complete criterion contains Given, When, and Then",
        [
            f"Criterion {criterion_id} omits a Given, When, or Then clause."
            for criterion_id in missing_gherkin_parts
        ],
        "Every complete criterion contains Given, When, and Then.",
    )

    empty_components = [
        f"{criterion.criterion_id}.{field}"
        for criterion in criteria
        for field in ("given", "when", "then")
        if not getattr(criterion, field).strip()
    ]
    _record_check(
        checks,
        "Separate Given, When, and Then fields are non-empty",
        [f"{field_name} is empty." for field_name in empty_components],
        "Every criterion has non-empty Given, When, and Then fields.",
    )

    source_reference_failures = [
        criterion.criterion_id
        for criterion in criteria
        if request.story_id not in criterion.source_references
    ]
    _record_check(
        checks,
        "Every criterion references the supplied story ID",
        [
            f"Criterion {criterion_id} does not reference {request.story_id}."
            for criterion_id in source_reference_failures
        ],
        f"Every criterion references {request.story_id}.",
    )

    invalid_types = [
        f"{criterion.criterion_id}: {criterion.criterion_type!r}"
        for criterion in criteria
        if criterion.criterion_type not in ALLOWED_CRITERION_TYPES
    ]
    _record_check(
        checks,
        "Criterion types use allowed schema values",
        [f"Invalid criterion type {value}." for value in invalid_types],
        "All criterion types are allowed.",
    )

    boundary_criteria = [
        criterion
        for criterion in criteria
        if criterion.criterion_type == "Boundary"
    ]
    boundary_failures: list[str] = []
    if boundary_criteria and not confirmed_boundaries:
        boundary_failures.extend(
            f"Criterion {criterion.criterion_id} is Boundary without a "
            "confirmed boundary in the request."
            for criterion in boundary_criteria
        )
    for boundary in confirmed_boundaries:
        kind = boundary["kind"].lower()
        value = boundary["value"]
        neighbor = boundary["neighbor"]
        if kind == "minimum":
            required_scenarios = (
                ("at", "at the minimum"),
                ("below", "below the minimum"),
            )
        elif kind == "maximum":
            required_scenarios = (
                ("at", "at the maximum"),
                ("above", "above the maximum"),
            )
        else:
            boundary_failures.append(
                f"Unknown boundary kind {kind!r} in evaluation case."
            )
            continue

        for direction, description in required_scenarios:
            if not any(
                _boundary_scenario_present(
                    _criterion_text(criterion),
                    value=value,
                    direction=direction,
                    neighbor=neighbor,
                )
                for criterion in criteria
            ):
                boundary_failures.append(
                    f"No boundary criterion tests {description} ({value})."
                )
    _record_check(
        checks,
        "Boundary criteria are grounded and test at and beyond each boundary",
        boundary_failures,
        (
            "Boundary criteria test the confirmed boundaries."
            if confirmed_boundaries
            else "No unconfirmed boundary criteria were generated."
        ),
    )

    confirmed_rule_behaviors = [
        criterion
        for criterion in criteria
        if criterion.criterion_type
        in {"Negative", "Permission", "Business Rule"}
    ]
    restriction_failures = []
    if confirmed_restrictions and not confirmed_rule_behaviors:
        restriction_failures.append(
            "Confirmed restriction has no Negative, Permission, or "
            "Business Rule criterion."
        )
    _record_check(
        checks,
        "Confirmed restrictions produce negative or rule behavior",
        restriction_failures,
        (
            "Confirmed restrictions have a corresponding behavior criterion."
            if confirmed_restrictions
            else "No confirmed restriction requires negative behavior."
        ),
    )

    allowed_rule_ids = {
        f"BR-{index:03d}"
        for index, _ in enumerate(request.business_rules, start=1)
    }
    invalid_rule_refs: list[str] = []
    for criterion in criteria:
        for applied_rule in criterion.business_rules_applied:
            rule_ids = re.findall(r"\bBR-\d{3}\b", applied_rule)
            if not rule_ids or any(rule_id not in allowed_rule_ids for rule_id in rule_ids):
                invalid_rule_refs.append(
                    f"{criterion.criterion_id} applies {applied_rule!r}; "
                    f"supplied rules are {sorted(allowed_rule_ids)}."
                )
    _record_check(
        checks,
        "Applied business-rule IDs exist in the request",
        invalid_rule_refs,
        "All applied business-rule IDs refer to supplied rules.",
    )

    confirmed_input_text = " ".join(
        [
            request.story_id,
            request.story_title,
            request.user_story,
            request.business_context,
            *request.business_rules,
            *request.known_constraints,
            *request.existing_acceptance_criteria,
        ]
    )
    request_text_without_ids = IDENTIFIER_PATTERN.sub(" ", confirmed_input_text)
    request_numbers = set(NUMBER_PATTERN.findall(request_text_without_ids))
    for boundary in confirmed_boundaries:
        request_numbers.add(boundary["value"])
        request_numbers.add(boundary["neighbor"])
    output_text = analysis.model_dump_json()
    output_text = IDENTIFIER_PATTERN.sub(" ", output_text)
    output_numbers = set(NUMBER_PATTERN.findall(output_text))
    unsupported_numbers = sorted(output_numbers - request_numbers)
    _record_check(
        checks,
        "No unsupported numerical limits are introduced",
        [
            "Response contains unsupported numerical value(s): "
            + ", ".join(unsupported_numbers)
            + "."
            if unsupported_numbers
            else ""
        ]
        if unsupported_numbers
        else [],
        "No numerical values were introduced beyond the request.",
    )

    missing_testability_reason = [
        criterion.criterion_id
        for criterion in criteria
        if not criterion.testability_reason.strip()
    ]
    _record_check(
        checks,
        "Every criterion has a testability reason",
        [
            f"Criterion {criterion_id} has no testability reason."
            for criterion_id in missing_testability_reason
        ],
        "Every criterion includes a testability reason.",
    )

    missing_validation_reason = [
        criterion.criterion_id
        for criterion in criteria
        if criterion.requires_human_validation
        and not (criterion.validation_reason or "").strip()
    ]
    _record_check(
        checks,
        "Criteria requiring human validation include a reason",
        [
            f"Criterion {criterion_id} requires validation without a reason."
            for criterion_id in missing_validation_reason
        ],
        "Every criterion requiring validation includes a reason.",
    )

    coverage_failures: list[str] = []
    for category in REQUIRED_COVERAGE_AREAS:
        if not any(
            _coverage_area_matches(entry.coverage_area, category)
            for entry in analysis.coverage
        ):
            coverage_failures.append(
                f"Coverage does not include {category}."
            )
    _record_check(
        checks,
        "Coverage includes all six required behavior categories",
        coverage_failures,
        "Coverage includes Positive, Negative, Boundary, Permission, "
        "Business Rule, and Failure.",
    )

    invalid_coverage_refs = [
        f"{entry.coverage_area}->{criterion_id}"
        for entry in analysis.coverage
        for criterion_id in entry.criterion_ids
        if criterion_id not in valid_coverage_ids
    ]
    _record_check(
        checks,
        "Coverage criterion IDs reference generated or supplied existing criteria",
        [
            f"Coverage references unknown criterion ID {reference}."
            for reference in invalid_coverage_refs
        ],
        "Coverage references only generated or supplied criterion IDs.",
    )

    missing_information_text = "\n".join(analysis.missing_information).lower()
    missing_topics_failures = [
        f"Missing information does not report {topic!r}."
        for topic in expected_missing_information
        if topic.lower() not in missing_information_text
    ]
    if unsupported_failure_behavior and any(
        criterion.criterion_type == "Failure" for criterion in criteria
    ):
        missing_topics_failures.append(
            "Failure behavior is unspecified but a Failure criterion was "
            "generated."
        )
    _record_check(
        checks,
        "Unsupported scenario information is reported rather than invented",
        missing_topics_failures,
        (
            "Expected missing scenario information is reported."
            if expected_missing_information or unsupported_failure_behavior
            else "No expected missing scenario information for this case."
        ),
    )

    existing_criteria = request.existing_acceptance_criteria
    duplicate_reports = analysis.duplicate_existing_criteria
    actual_duplicate_pair_exists = _has_duplicate_pair(existing_criteria)
    duplicate_failures: list[str] = []
    if len(existing_criteria) < 2 and duplicate_reports:
        duplicate_failures.append(
            "A single existing criterion must not be reported as a duplicate."
        )
    else:
        for report in duplicate_reports:
            if not actual_duplicate_pair_exists:
                duplicate_failures.append(
                    f"Reported duplicate is unsupported: {report!r}."
                )
                continue
            matching_pairs = [
                (left, right)
                for left in range(len(existing_criteria))
                for right in range(left + 1, len(existing_criteria))
                if _overlap_score(
                    existing_criteria[left],
                    existing_criteria[right],
                )
                >= 0.65
            ]
            report_matches_pair = any(
                (
                    f"EXISTING-AC-{left + 1:03d}".lower() in report.lower()
                    and f"EXISTING-AC-{right + 1:03d}".lower()
                    in report.lower()
                )
                or (
                    _overlap_score(report, existing_criteria[left]) >= 0.45
                    and _overlap_score(report, existing_criteria[right]) >= 0.45
                )
                for left, right in matching_pairs
            )
            if not report_matches_pair and len(matching_pairs) == 1:
                left, right = matching_pairs[0]
                cited_ids = {
                    int(number) - 1
                    for number in re.findall(
                        r"EXISTING-AC-(\d{3})",
                        report,
                        flags=re.IGNORECASE,
                    )
                }
                report_matches_pair = cited_ids in ({left}, {right})
            if not report_matches_pair:
                duplicate_failures.append(
                    f"Duplicate report does not identify an overlapping "
                    f"existing pair: {report!r}."
                )
    if actual_duplicate_pair_exists and not duplicate_reports:
        duplicate_failures.append(
            "Substantially overlapping existing criteria were not identified."
        )
    _record_check(
        checks,
        "Existing duplicates are reported only for substantially overlapping pairs",
        duplicate_failures,
        (
            "Existing-criterion duplicate reporting matches the supplied list."
        ),
    )

    _record_check(
        checks,
        "Human validation is not empty",
        []
        if analysis.human_validation_required
        else ["No human-validation items were returned."],
        "Human-validation items were returned.",
    )

    processing_failures: list[str] = []
    if accepted_for_processing_only:
        completion_claims = re.compile(
            r"\b(?:successfully completed|transaction completed|"
            r"transfer completed|payment completed|fully processed)\b",
            re.IGNORECASE,
        )
        for criterion in criteria:
            if completion_claims.search(
                " ".join((criterion.then, criterion.criterion))
            ):
                processing_failures.append(
                    f"{criterion.criterion_id} claims completion beyond "
                    "acceptance for processing."
                )
        if not any(
            re.search(
                r"\b(?:accept(?:ed|s)? for processing|"
                r"accepted for further processing|queued for processing)\b",
                " ".join((criterion.then, criterion.criterion)),
                re.IGNORECASE,
            )
            for criterion in criteria
        ):
            processing_failures.append(
                "No criterion confirms acceptance for processing."
            )
    _record_check(
        checks,
        "Processing acceptance is not misrepresented as completion",
        processing_failures,
        (
            "Processing acceptance is accurately distinguished from completion."
            if accepted_for_processing_only
            else "No processing-only completion constraint applies."
        ),
    )

    contradictory_preconditions = [
        phrase
        for phrase in contradictory_precondition_phrases
        if any(phrase.lower() in item.lower() for item in analysis.preconditions)
    ]
    if any(
        re.search(r"\b(?:unauthorized|not authorized|not permitted)\b", text, re.I)
        for criterion in criteria
        for text in (criterion.given, criterion.when, criterion.then, criterion.criterion)
    ) and any(
        re.search(r"\b(?:all users|customer) (?:is|are) authorized\b", item, re.I)
        for item in analysis.preconditions
    ):
        contradictory_preconditions.append(
            "Global precondition authorizes actors whose scenario-specific "
            "criteria test unauthorized access."
        )
    _record_check(
        checks,
        "Global preconditions do not contradict scenario-specific criteria",
        [
            f"Contradictory global precondition: {phrase}."
            for phrase in contradictory_preconditions
        ],
        "Global preconditions do not exclude the tested scenarios.",
    )

    passed_count = sum(check.passed for check in checks)
    score = round(passed_count / len(checks) * 100, 2)
    return AcceptanceCriteriaEvaluationResult(
        case_id=case_id,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
        analysis=analysis,
    )
