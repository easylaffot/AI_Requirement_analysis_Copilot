import re
from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.ambiguity import (
    AmbiguityAnalysisRequest,
    AmbiguityAnalysisResponse,
    AmbiguityCategory,
)


ALLOWED_CATEGORIES = set(AmbiguityCategory.__args__)
ALLOWED_SEVERITIES = {"High", "Medium", "Low"}
ALLOWED_STATUSES = {"Clear", "Needs Clarification", "Not Ready"}

MISSING_INFORMATION_PATTERNS: dict[str, tuple[str, ...]] = {
    "actor": (
        r"\bactor\b",
        r"\bwho (?:will|should|must|can) perform\b",
        r"\bresponsible (?:person|party|role)\b",
    ),
    "object": (
        r"\bobject\b",
        r"\btarget (?:object|item|entity)\b",
        r"\bwhat (?:to|should|must) be updated\b",
    ),
    "expected outcome": (
        r"\bexpected (?:outcomes?|results?|behaviors?)\b",
        r"\bexpected results?\b",
        r"\bintended (?:outcomes?|results?|behaviors?)\b",
        r"\b(?:outcomes?|results?|behaviors?)\b",
        r"\bgoal\b",
    ),
    "eligibility criteria": (
        r"\beligibility criteria\b",
        r"\bcriteria for eligibility\b",
        r"\bconditions? for (?:being )?eligible\b",
    ),
    "processing time": (
        r"\btime(?:frame| limit| target| requirement)?\b",
        r"\btiming\b",
        r"\bduration\b",
        r"\bdeadline\b",
        r"\bhow quickly\b",
        r"\bprocessing speed\b",
    ),
    "amount threshold": (
        r"\bamount\b",
        r"\bthreshold\b",
        r"\bquantity\b",
        r"\bmaximum\b",
        r"\bminimum\b",
        r"\bboundary\b",
        r"\blimit\b",
    ),
    "notification channel": (
        r"\bnotification channel\b",
        r"\bdelivery channel\b",
        r"\bchannels?\b",
        r"\bhow (?:the )?(?:customer|requester|user) (?:is|will be) notified\b",
    ),
    "notification condition": (
        r"\bnotification condition\b",
        r"\bnotification\w*.{0,50}\b(?:conditions?|triggers?|criteria)\b",
        r"\bwhen to notify\b",
        r"\bcondition(?:s)? for (?:sending )?(?:a )?notification\b",
        r"\bcondition(?:s)? for (?:a )?(?:customer )?notification\b",
        r"\bcondition(?:s)? determining\b.{0,60}\bnotification\b",
    ),
}

CONCRETE_CHANNELS = (
    "email",
    "e-mail",
    "sms",
    "text message",
    "push notification",
    "in-app notification",
    "phone call",
    "postal mail",
    "instant message",
)

UNSUPPORTED_DETAIL_PATTERNS: dict[str, re.Pattern[str]] = {
    "technical implementation detail": re.compile(
        r"\b(?:api|database|sql|oauth|endpoint|server|encryption|"
        r"microservice|browser|cloud platform)\b",
        re.IGNORECASE,
    ),
    "regulation or standard": re.compile(
        r"\b(?:gdpr|hipaa|pci(?:\s+dss)?|sox|iso\s*27001)\b",
        re.IGNORECASE,
    ),
    "permission or access-control detail": re.compile(
        r"\b(?:role-based access|access permission|authorization role|"
        r"administrator access|"
        r"(?:admin|manager|staff) permissions?)\b",
        re.IGNORECASE,
    ),
    "specific workflow": re.compile(
        r"\b(?:approval workflow|escalation workflow|four-eyes approval|"
        r"dual approval)\b",
        re.IGNORECASE,
    ),
}

SUMMARY_STRENGTHENING_PAIRS = (
    ("important users", "critical users"),
    ("quickly", "rapid"),
    ("handle appropriately", "process properly"),
)
CONCRETE_ACTORS = (
    "customer",
    "requester",
    "claimant",
    "employee",
    "staff",
    "manager",
    "administrator",
    "supervisor",
    "operator",
    "agent",
    "applicant",
    "reviewer",
    "approver",
    "merchant",
)

CERTAINTY_PHRASES = re.compile(
    r"\b(?:the requirement (?:states|specifies|confirms)|"
    r"(?:is|are) confirmed|explicitly (?:states|specifies|requires))\b",
    re.IGNORECASE,
)
TENTATIVE_INTERPRETATION = re.compile(
    r"\b(?:could|might|may|possibly|potentially|one possible "
    r"interpretation|another possible interpretation)\b",
    re.IGNORECASE,
)

NUMERIC_DETAIL = re.compile(
    r"(?<![A-Za-z0-9])(?P<symbol>[$€£])?\s*"
    r"(?P<number>\d+(?:[.,]\d+)?)\s*"
    r"(?P<unit>%|percent|ms|milliseconds?|seconds?|minutes?|hours?|days?|"
    r"weeks?|months?|years?|dollars?|USD|EUR)?(?![A-Za-z0-9])",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(r"\[([^\]]+)\]")


class AmbiguityEvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class AmbiguityEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[AmbiguityEvaluationCheck]
    analysis: AmbiguityAnalysisResponse


def _record_check(
    checks: list[AmbiguityEvaluationCheck],
    name: str,
    failures: Iterable[str],
    success_message: str,
) -> None:
    failure_list = list(failures)
    checks.append(
        AmbiguityEvaluationCheck(
            name=name,
            passed=not failure_list,
            message="; ".join(failure_list) if failure_list else success_message,
        )
    )


def _source_text(request: AmbiguityAnalysisRequest) -> str:
    return " ".join(
        [
            request.requirement_text,
            request.business_context,
            *request.known_actors,
            *request.known_business_rules,
        ]
    )


def _response_prose(analysis: AmbiguityAnalysisResponse) -> list[str]:
    prose = [
        analysis.requirement_summary,
        analysis.score_explanation,
        *analysis.confirmed_information,
        *analysis.assumptions,
        *analysis.missing_information,
        *analysis.risks,
        *analysis.human_validation_required,
    ]

    for finding in analysis.ambiguity_findings:
        prose.extend(
            [
                finding.ambiguous_text,
                finding.explanation,
                finding.interpretation_risk,
                *finding.clarification_questions,
            ]
        )
        prose.extend(
            interpretation.interpretation
            for interpretation in finding.possible_interpretations
        )
        prose.extend(
            interpretation.notes
            for interpretation in finding.possible_interpretations
        )

    prose.extend(
        rewrite.rewritten_requirement for rewrite in analysis.suggested_rewrites
    )
    for rewrite in analysis.suggested_rewrites:
        prose.extend(rewrite.unresolved_placeholders)
        prose.extend(rewrite.assumptions_used)

    return prose


def _defined_term_in_finding(
    finding_text: str,
    defined_terms: Iterable[str],
) -> list[str]:
    folded_finding = finding_text.casefold()
    return [
        term
        for term in defined_terms
        if term.casefold() in folded_finding
    ]


def _matches_missing_information(concept: str, text: str) -> bool:
    patterns = MISSING_INFORMATION_PATTERNS.get(
        concept,
        (re.escape(concept),),
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _unsupported_numeric_details(
    request: AmbiguityAnalysisRequest,
    prose: Iterable[str],
) -> list[str]:
    def normalized_number(value: str) -> str:
        return str(Decimal(value.replace(",", "")).normalize())

    source_matches = list(NUMERIC_DETAIL.finditer(_source_text(request)))
    source_numbers = {
        normalized_number(match.group("number"))
        for match in source_matches
    }

    def normalized_unit(match: re.Match[str]) -> str | None:
        symbol = match.group("symbol")
        unit = match.group("unit")
        if symbol:
            return {"$": "usd", "€": "eur", "£": "gbp"}[symbol]
        if unit is None:
            return None
        normalized = unit.casefold()
        if normalized == "percent":
            return "%"
        if normalized == "dollars":
            return "usd"
        return normalized[:-1] if normalized.endswith("s") else normalized

    source_facts = {
        (
            normalized_number(match.group("number")),
            normalized_unit(match),
        )
        for match in source_matches
    }
    invented: set[str] = set()
    for text in prose:
        prose_without_ids = re.sub(
            r"\b[A-Z][A-Z0-9]*(?:[-_][A-Z0-9]+)*\b|"
            r"\b(?:finding|interpretation|rewrite|case|item)"
            r"\s*[-#:]?\s*\d+\b",
            " ",
            text,
        )
        for match in NUMERIC_DETAIL.finditer(prose_without_ids):
            number = normalized_number(match.group("number"))
            unit = normalized_unit(match)
            if number not in source_numbers or (
                unit is not None
                and (number, unit) not in source_facts
                and not (
                    unit == "usd"
                    and (number, None) in source_facts
                    and re.search(r"\bUSD\b", _source_text(request), re.I)
                )
            ):
                invented.add(match.group(0).strip())
    return sorted(invented)


def _unsupported_named_details(
    request: AmbiguityAnalysisRequest,
    prose: Iterable[str],
) -> list[str]:
    source = _source_text(request).casefold()
    unsupported: set[str] = set()

    for text in prose:
        folded_text = text.casefold()
        for actor in CONCRETE_ACTORS:
            if (
                re.search(rf"\b{re.escape(actor)}\b", folded_text)
                and not re.search(
                    rf"\b{re.escape(actor)}\b",
                    source,
                )
            ):
                unsupported.add(f"unsupported actor: {actor}")
        for channel in CONCRETE_CHANNELS:
            channel_pattern = rf"(?<!\w){re.escape(channel)}(?!\w)"
            if (
                re.search(channel_pattern, folded_text)
                and not re.search(channel_pattern, source)
            ):
                unsupported.add(
                    f"notification channel: {channel} in {text!r}"
                )
        for label, pattern in UNSUPPORTED_DETAIL_PATTERNS.items():
            for match in pattern.finditer(text):
                detail = match.group(0)
                if detail.casefold() not in source:
                    unsupported.add(f"{label}: {detail}")

    return sorted(unsupported)


def _question_is_one_concrete_decision(question: str) -> bool:
    if question.count("?") != 1 or ";" in question:
        return False
    coordination = re.search(
        r"\b(?:and|or)\b",
        question,
        flags=re.IGNORECASE,
    )
    if coordination and not re.search(
        r"\b(?:object|target)\s+(?:or|and)\s+"
        r"(?:entity|item|data record)\b|"
        r"\b(?:expected )?(?:result|outcome)\s+(?:or|and)\s+"
        r"(?:behavior|result|outcome|state)\b|"
        r"\b(?:system )?state\s+(?:or|and)\s+(?:result|outcome)\b|"
        r"\b(?:actor|person)\s+(?:or|and)\s+(?:role|person)\b",
        question,
        flags=re.IGNORECASE,
    ):
        return False
    if re.search(
        r"\b(?:and|or)\s+(?:what|which|who|when|where|whether|how)\b",
        question,
        flags=re.IGNORECASE,
    ):
        return False
    return bool(
        re.search(
            r"^\s*(?:please clarify whether\b|"
            r"(?:within what|under what|under which|at what|for what|what|which|who|when|where|how|whether|"
            r"is|are|does|do|can|should|will|must)\b)",
            question,
            flags=re.IGNORECASE,
        )
    )


def _normalized_phrase(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def _duplicate_finding_pairs(
    analysis: AmbiguityAnalysisResponse,
) -> list[str]:
    duplicates: list[str] = []
    findings = analysis.ambiguity_findings
    for index, first in enumerate(findings):
        first_tokens = _normalized_phrase(first.ambiguous_text)
        for second in findings[index + 1 :]:
            second_tokens = _normalized_phrase(second.ambiguous_text)
            union = first_tokens | second_tokens
            similarity = (
                len(first_tokens & second_tokens) / len(union)
                if union
                else 0.0
            )
            first_reason = _normalized_phrase(
                f"{first.explanation} {first.interpretation_risk}"
            )
            second_reason = _normalized_phrase(
                f"{second.explanation} {second.interpretation_risk}"
            )
            reason_union = first_reason | second_reason
            reason_similarity = (
                len(first_reason & second_reason) / len(reason_union)
                if reason_union
                else 0.0
            )
            if (
                first.category == second.category
                and (
                    first.ambiguous_text.casefold()
                    == second.ambiguous_text.casefold()
                    or (len(first_tokens) >= 3 and similarity >= 0.85)
                )
            ) or (
                first.ambiguous_text.casefold()
                == second.ambiguous_text.casefold()
                and reason_similarity >= 0.65
            ):
                duplicates.append(
                    f"{first.finding_id} and {second.finding_id} "
                    f"both cite {first.ambiguous_text!r}"
                )
    return duplicates


def _rewrite_concept_placeholder(
    concept: str,
    rewrite_text: str,
) -> bool:
    placeholder_names = {
        "actor": r"\[(?:ACTOR|PERSON|ROLE|RESPONSIBLE PARTY)[^\]]*\]",
        "object": r"\[(?:OBJECT|TARGET|ITEM|ENTITY)[^\]]*\]",
        "expected outcome": r"\[[^\]]*(?:OUTCOME|RESULT|GOAL|BEHAVIOR)[^\]]*\]",
    }
    pattern = placeholder_names.get(concept)
    return bool(pattern and re.search(pattern, rewrite_text, re.IGNORECASE))


def _normalized_placeholder(value: str) -> str:
    return value.strip().strip("[]").casefold()


def evaluate_ambiguity_response(
    *,
    case_id: str,
    request: AmbiguityAnalysisRequest,
    analysis: AmbiguityAnalysisResponse,
    expected_missing_information: tuple[str, ...] = (),
    expected_defined_terms: tuple[str, ...] = (),
    expected_status: Literal[
        "Clear", "Not Ready", "Not Clear"
    ] | None = None,
    minimum_score: int | None = None,
    expected_optional_modality: bool = False,
    expect_notification_channel: bool = False,
    unresolved_rewrite_concepts: tuple[str, ...] = (),
    requires_cannot_rewrite_safely: bool = False,
) -> AmbiguityEvaluationResult:
    checks: list[AmbiguityEvaluationCheck] = []
    findings = analysis.ambiguity_findings

    ids = [finding.finding_id for finding in findings]
    _record_check(
        checks,
        "Finding IDs are unique",
        [
            f"Duplicate finding ID: {finding_id}"
            for finding_id in set(ids)
            if ids.count(finding_id) > 1
        ],
        "All finding IDs are unique.",
    )

    _record_check(
        checks,
        "Finding categories use schema values",
        [
            f"{finding.finding_id} has invalid category {finding.category!r}"
            for finding in findings
            if finding.category not in ALLOWED_CATEGORIES
        ],
        "All finding categories are allowed.",
    )
    _record_check(
        checks,
        "Finding severities use schema values",
        [
            f"{finding.finding_id} has invalid severity {finding.severity!r}"
            for finding in findings
            if finding.severity not in ALLOWED_SEVERITIES
        ],
        "All finding severities are allowed.",
    )
    _record_check(
        checks,
        "Ambiguous text is grounded in requirement",
        [
            f"{finding.finding_id} quotes {finding.ambiguous_text!r}, "
            "which is not an exact case-insensitive substring."
            for finding in findings
            if finding.ambiguous_text.casefold()
            not in request.requirement_text.casefold()
        ],
        "Every ambiguous phrase exactly appears in the requirement.",
    )

    defined_in_input = [
        term
        for term in expected_defined_terms
        if term.casefold()
        in " ".join(
            [request.business_context, *request.known_business_rules]
        ).casefold()
    ]
    _record_check(
        checks,
        "Explicitly defined terms are not marked ambiguous",
        [
            f"{finding.finding_id} marks explicitly defined term "
            f"{term!r} as ambiguous."
            for finding in findings
            for term in _defined_term_in_finding(
                finding.ambiguous_text,
                defined_in_input,
            )
        ],
        "No explicitly defined term is marked ambiguous.",
    )

    _record_check(
        checks,
        "Findings explain the ambiguity",
        [
            f"{finding.finding_id} has an empty explanation."
            for finding in findings
            if not finding.explanation.strip()
        ],
        "Every finding has a non-empty explanation.",
    )
    _record_check(
        checks,
        "Findings explain interpretation risk",
        [
            f"{finding.finding_id} has an empty interpretation risk."
            for finding in findings
            if not finding.interpretation_risk.strip()
        ],
        "Every finding has a non-empty interpretation risk.",
    )
    _record_check(
        checks,
        "Clarification questions request one concrete decision",
        [
            f"{finding.finding_id}: {question!r}"
            for finding in findings
            for question in finding.clarification_questions
            if not _question_is_one_concrete_decision(question)
        ],
        "Every clarification question asks one concrete decision.",
    )
    _record_check(
        checks,
        "Findings identify human validation owners",
        [
            f"{finding.finding_id} has no validation owner."
            for finding in findings
            if not finding.validation_owner.strip()
        ],
        "Every finding identifies a human validation owner.",
    )

    duplicate_interpretation_ids = [
        f"{finding.finding_id}: {interpretation_id}"
        for finding in findings
        for interpretation_id in {
            interpretation.interpretation_id
            for interpretation in finding.possible_interpretations
            if sum(
                candidate.interpretation_id == interpretation.interpretation_id
                for candidate in finding.possible_interpretations
            )
            > 1
        }
    ]
    _record_check(
        checks,
        "Possible interpretation IDs are unique",
        duplicate_interpretation_ids,
        "Possible interpretation IDs are unique within each finding.",
    )

    unsupported_confirmed = [
        f"{finding.finding_id}/{interpretation.interpretation_id}: "
        f"{interpretation.interpretation!r}"
        for finding in findings
        for interpretation in finding.possible_interpretations
        if not interpretation.supported_by_input
        and (
            CERTAINTY_PHRASES.search(interpretation.interpretation)
            or not TENTATIVE_INTERPRETATION.search(
                interpretation.interpretation
            )
        )
    ]
    _record_check(
        checks,
        "Possible interpretations are not presented as confirmed facts",
        unsupported_confirmed,
        "Unsupported interpretations are not phrased as confirmed facts.",
    )

    prose = _response_prose(analysis)
    invented_numbers = _unsupported_numeric_details(request, prose)
    invented_details = _unsupported_named_details(request, prose)
    _record_check(
        checks,
        "Output does not invent unsupported concrete details",
        [
            *[f"Unsupported value or timing: {item}" for item in invented_numbers],
            *invented_details,
        ],
        "No unsupported values, channels, technical details, regulations, "
        "permissions, or specific workflows were found.",
    )

    interpretation_support_failures: list[str] = []
    for finding in findings:
        for interpretation in finding.possible_interpretations:
            if (
                interpretation.supported_by_input
                and (
                    _unsupported_numeric_details(
                        request,
                        [interpretation.interpretation, interpretation.notes],
                    )
                    or _unsupported_named_details(
                        request,
                        [
                            interpretation.interpretation,
                            interpretation.notes,
                        ],
                    )
                )
            ):
                interpretation_support_failures.append(
                    f"{finding.finding_id}/{interpretation.interpretation_id} "
                    "marks an unsupported concrete detail as supported."
                )
    _record_check(
        checks,
        "Interpretation support flags match supplied information",
        interpretation_support_failures,
        "Interpretation support flags do not contradict input facts.",
    )

    _record_check(
        checks,
        "Requirement summary preserves source meaning",
        [
            f"Summary changes {source_term!r} to stronger wording "
            f"{strengthened_term!r}."
            for source_term, strengthened_term in SUMMARY_STRENGTHENING_PAIRS
            if source_term.casefold() in request.requirement_text.casefold()
            and strengthened_term.casefold()
            in analysis.requirement_summary.casefold()
        ],
        "The summary does not strengthen known source wording.",
    )

    if expected_status == "Clear":
        _record_check(
            checks,
            "Clear case has no findings",
            [] if not findings else [f"Found {len(findings)} finding(s)."],
            "No ambiguity findings were returned.",
        )
        _record_check(
            checks,
            "Clear case returns Clear status",
            [] if analysis.overall_status == "Clear" else [
                f"Expected Clear, got {analysis.overall_status}."
            ],
            "Overall status is Clear.",
        )
    elif expected_status == "Not Ready":
        _record_check(
            checks,
            "Severely incomplete case is Not Ready",
            [] if analysis.overall_status == "Not Ready" else [
                f"Expected Not Ready, got {analysis.overall_status}."
            ],
            "Overall status is Not Ready.",
        )
    elif expected_status == "Not Clear":
        _record_check(
            checks,
            "Ambiguous case is not Clear",
            [] if analysis.overall_status != "Clear" else [
                "Ambiguous requirement was classified as Clear."
            ],
            "Ambiguous requirement is not classified as Clear.",
        )

    _record_check(
        checks,
        "Overall status uses a schema value",
        [] if analysis.overall_status in ALLOWED_STATUSES else [
            f"Invalid overall status: {analysis.overall_status!r}."
        ],
        "Overall status is allowed.",
    )
    _record_check(
        checks,
        "Overall score is within 0 to 100",
        [] if 0 <= analysis.overall_score <= 100 else [
            f"Score is {analysis.overall_score}."
        ],
        f"Score is {analysis.overall_score}.",
    )

    if minimum_score is not None:
        _record_check(
            checks,
            "Clear case has a suitably high score",
            [] if analysis.overall_score >= minimum_score else [
                f"Expected at least {minimum_score}, "
                f"got {analysis.overall_score}."
            ],
            f"Score meets the {minimum_score}-point clear-case threshold.",
        )

    if any(finding.severity == "High" for finding in findings):
        _record_check(
            checks,
            "High-severity ambiguity scores below clear cases",
            [] if analysis.overall_score < 85 else [
                "A high-severity finding has a score of "
                f"{analysis.overall_score}; expected below the clear-case "
                "minimum of 85."
            ],
            "High-severity ambiguity has a score below the clear-case minimum.",
        )

    rewrite_failures: list[str] = []
    finding_ids = {finding.finding_id for finding in findings}
    for rewrite in analysis.suggested_rewrites:
        if not rewrite.rewritten_requirement.startswith("The system shall"):
            rewrite_failures.append(
                f"{rewrite.rewrite_id} does not begin with "
                "'The system shall'."
            )
        placeholders = {
            placeholder.strip()
            for placeholder in PLACEHOLDER.findall(
                rewrite.rewritten_requirement
            )
        }
        unresolved = {
            _normalized_placeholder(placeholder)
            for placeholder in rewrite.unresolved_placeholders
        }
        visible_placeholders = {
            _normalized_placeholder(placeholder)
            for placeholder in placeholders
        }
        if not visible_placeholders.issubset(unresolved):
            rewrite_failures.append(
                f"{rewrite.rewrite_id} omits visible placeholders from "
                "unresolved_placeholders."
            )
        if rewrite.status == "Conditional" and not placeholders:
            rewrite_failures.append(
                f"{rewrite.rewrite_id} is Conditional without a visible "
                "bracketed placeholder."
            )
        if rewrite.status == "Ready" and rewrite.unresolved_placeholders:
            rewrite_failures.append(
                f"{rewrite.rewrite_id} is Ready but has unresolved "
                "placeholders."
            )
        if rewrite.status == "Ready" and placeholders:
            rewrite_failures.append(
                f"{rewrite.rewrite_id} is Ready but contains visible "
                "placeholders."
            )
        unknown_sources = set(rewrite.source_finding_ids) - finding_ids
        if unknown_sources:
            rewrite_failures.append(
                f"{rewrite.rewrite_id} references unknown findings "
                f"{sorted(unknown_sources)}."
            )
        if rewrite.status == "Cannot Rewrite Safely":
            missing_concepts = [
                concept
                for concept in unresolved_rewrite_concepts
                if not _rewrite_concept_placeholder(
                    concept,
                    rewrite.rewritten_requirement,
                )
            ]
            if missing_concepts:
                rewrite_failures.append(
                    f"{rewrite.rewrite_id} claims it cannot rewrite safely "
                    "but resolves or omits placeholders for "
                    f"{', '.join(missing_concepts)}."
                )
    _record_check(
        checks,
        "Suggested rewrites are safe and traceable",
        rewrite_failures,
        "Rewrites use the required format, placeholders, and source IDs.",
    )
    if requires_cannot_rewrite_safely:
        _record_check(
            checks,
            "Unresolvable requirement is not rewritten as settled",
            [] if any(
                rewrite.status == "Cannot Rewrite Safely"
                for rewrite in analysis.suggested_rewrites
            ) else [
                "No rewrite is marked Cannot Rewrite Safely despite missing "
                "actor, goal, or expected outcome."
            ],
            "At least one rewrite is marked Cannot Rewrite Safely.",
        )

    missing_information = " ".join(analysis.missing_information)
    missing_failures = [
        concept
        for concept in expected_missing_information
        if not _matches_missing_information(concept, missing_information)
    ]
    _record_check(
        checks,
        "Expected missing information is reported",
        [f"Missing information does not identify {concept!r}." for concept in missing_failures],
        "Expected missing information is present.",
    )

    requirement_mentions_notification = bool(
        re.search(r"\b(?:notify|notification|notified|alert)\b", request.requirement_text, re.I)
    )
    supplied_channel = any(
        re.search(
            rf"(?<!\w){re.escape(channel)}(?!\w)",
            " ".join(
                [request.business_context, *request.known_business_rules]
            ).casefold(),
        )
        for channel in CONCRETE_CHANNELS
    )
    missing_mentions_channel = _matches_missing_information(
        "notification channel",
        missing_information,
    )
    channel_failures: list[str] = []
    if expect_notification_channel and not missing_mentions_channel:
        channel_failures.append(
            "Expected the undefined notification channel in missing_information."
        )
    if (
        not requirement_mentions_notification or supplied_channel
    ) and missing_mentions_channel:
        channel_failures.append(
            "Notification channel was reported although notification behavior "
            "is absent or its channel is defined."
        )
    _record_check(
        checks,
        "Notification channel is detected only when undefined",
        channel_failures,
        "Notification-channel reporting matches requirement and supplied context.",
    )

    modal_words = re.findall(
        r"\b(?:should|may|could|normally)\b",
        request.requirement_text,
        flags=re.IGNORECASE,
    )
    optionality_failures: list[str] = []
    if expected_optional_modality and not modal_words:
        optionality_failures.append(
            "Case expects unclear modal wording but the requirement has none."
        )
    if expected_optional_modality and not any(
        finding.category == "Optionality"
        and re.search(
            r"\b(?:should|may|could|normally)\b",
            finding.ambiguous_text,
            flags=re.IGNORECASE,
        )
        for finding in findings
    ):
        optionality_failures.append(
            "No Optionality finding quotes the unclear modal wording."
        )
    _record_check(
        checks,
        "Unclear modal wording is checked for optionality",
        optionality_failures,
        "Unclear modal wording has an Optionality finding.",
    )

    _record_check(
        checks,
        "Ambiguous cases require human validation",
        [] if not findings or analysis.human_validation_required else [
            "Ambiguous findings were returned without human validation items."
        ],
        "Human validation is present when findings exist.",
    )
    _record_check(
        checks,
        "Findings do not substantially duplicate",
        _duplicate_finding_pairs(analysis),
        "No substantially duplicate findings were found.",
    )

    passed_count = sum(check.passed for check in checks)
    score = round(passed_count / len(checks) * 100, 2) if checks else 0.0
    return AmbiguityEvaluationResult(
        case_id=case_id,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
        analysis=analysis,
    )
