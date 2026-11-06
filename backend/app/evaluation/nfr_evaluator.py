import re
from collections import Counter

from pydantic import BaseModel

from app.schemas.nfr import (
    NfrCategory,
    NfrRecommendationRequest,
    NfrRecommendationResponse,
)


ALLOWED_CATEGORIES = set(NfrCategory.__args__)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "shall",
    "the",
    "that",
    "to",
    "with",
}
QUALITY_TERMS = {
    "accessible",
    "accessibility",
    "available",
    "availability",
    "capacity",
    "compatible",
    "compatibility",
    "confidential",
    "consistent",
    "continuity",
    "durable",
    "efficient",
    "integrity",
    "latency",
    "maintainability",
    "measurable",
    "performance",
    "privacy",
    "recoverability",
    "recoverable",
    "recovery",
    "reliable",
    "reliability",
    "resilient",
    "scalable",
    "scalability",
    "secure",
    "security",
    "traceability",
    "usable",
    "usability",
}
TARGET_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:percent|milliseconds?|ms|seconds?|secs?|"
    r"minutes?|mins?|hours?|days?|weeks?|months?|years?|"
    r"concurrent\s+users?|users?|requests?\s*/\s*(?:second|minute)|"
    r"transactions?\s*/\s*(?:second|minute)|records?|gigabytes?|"
    r"megabytes?|terabytes?|times?\s+per\s+(?:second|minute|hour|day))\b"
    r"|\b\d+(?:[.,]\d+)?\s*%(?!\w)",
    re.IGNORECASE,
)
OBJECTIVE_PATTERN = re.compile(
    r"\b(?:RTO|RPO|WCAG)\b.{0,20}\b\d+(?:[.,]\d+)?\b"
    r"|\b\d+(?:[.,]\d+)?\s*(?:nines?|retries|attempts?)\b"
    r"|\b(?:retry|retries|RTO|RPO|capacity|throughput|"
    r"accessibility\s+level)\D{0,20}\d+(?:[.,]\d+)?\b"
    r"|\b(?:level\s+)?(?:A{1,3})\b(?=.{0,20}\baccessibility\b)",
    re.IGNORECASE,
)
INVENTED_ENTITY_TERMS = {
    "aes",
    "aws",
    "azure",
    "bcrypt",
    "ccpa",
    "cassandra",
    "cloudwatch",
    "databricks",
    "datadog",
    "docker",
    "dynamodb",
    "ferpa",
    "ftp",
    "gdpr",
    "gcp",
    "glba",
    "google cloud",
    "grafana",
    "graphql",
    "grpc",
    "hipaa",
    "hippa",
    "https",
    "iso 27001",
    "jenkins",
    "kafka",
    "kubernetes",
    "mfa",
    "mongodb",
    "mysql",
    "new relic",
    "oauth",
    "okta",
    "oracle",
    "openid",
    "owasp",
    "pci dss",
    "postgres",
    "postgresql",
    "prometheus",
    "rabbitmq",
    "redis",
    "rest",
    "rest api",
    "rsa",
    "salesforce",
    "sha-256",
    "snowflake",
    "soap",
    "sox",
    "splunk",
    "sqlite",
    "soc 2",
    "sql server",
    "terraform",
    "tcp/ip",
    "tls",
    "wcag",
}
SECURITY_INVENTION_TERMS = (
    "security event",
    "security alert",
    "alerting",
    "authentication",
    "cipher suite",
    "consent",
    "cryptographic protocol",
    "data residency",
    "encryption",
    "encryption protocol",
    "log payload",
    "masking",
    "mfa",
    "monitoring integration",
    "retention",
    "security monitoring",
)
AUDIT_INVENTION_TERMS = (
    "immutable",
    "immutability",
    "retention period",
    "retention",
    "audit field",
    "audit fields",
    "audit storage",
    "stored audit",
    "audit record format",
)
COMPATIBILITY_TERMS = (
    "platform",
    "browser",
    "device",
    "protocol",
    "interface",
    "external system",
)
STOPWORDS_FOR_OVERLAP = STOP_WORDS | {
    "approved",
    "business",
    "existing",
    "nfr",
    "system",
    "target",
}


class NfrEvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class NfrEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[NfrEvaluationCheck]
    analysis: NfrRecommendationResponse


def _record_check(
    checks: list[NfrEvaluationCheck],
    name: str,
    failures: list[str],
    success_message: str,
) -> None:
    checks.append(
        NfrEvaluationCheck(
            name=name,
            passed=not failures,
            message="; ".join(failures) if failures else success_message,
        )
    )


def _request_text(request: NfrRecommendationRequest) -> str:
    return " ".join(
        (
            request.requirement_id,
            request.requirement_title,
            request.requirement_text,
            request.business_context,
            request.business_domain,
            *request.known_constraints,
            *request.existing_nfrs,
            request.additional_instructions or "",
        )
    ).lower()


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS_FOR_OVERLAP
    }


def _overlap_score(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(
        len(left_tokens),
        len(right_tokens),
    )


def _recommendation_text(recommendation: object) -> str:
    fields = (
        "title",
        "requirement",
        "rationale",
        "measurement_method",
        "missing_target",
        "validation_reason",
    )
    return " ".join(
        str(value)
        for field in fields
        if (value := getattr(recommendation, field, None))
    )


def _all_output_text(analysis: NfrRecommendationResponse) -> str:
    values = [
        analysis.requirement_summary,
        *analysis.existing_nfr_coverage,
        *analysis.duplicate_existing_nfrs,
        *analysis.assumptions,
        *analysis.ambiguities,
        *analysis.missing_information,
        *analysis.risks,
        *analysis.human_validation_required,
    ]
    for recommendation in analysis.recommendations:
        values.extend(
            (
                recommendation.title,
                recommendation.requirement,
                recommendation.rationale,
                recommendation.measurement_method,
                recommendation.missing_target or "",
                recommendation.validation_reason or "",
                *recommendation.source_references,
                *recommendation.assumptions,
            )
        )
    for assessment in analysis.relevant_categories:
        values.extend(
            (assessment.category, assessment.rationale)
        )
    return " ".join(values)


def _has_positive_evidence(
    request: NfrRecommendationRequest,
    terms: tuple[str, ...],
) -> bool:
    supplied_context = " ".join(
        (
            request.requirement_text,
            request.business_context,
            *request.known_constraints,
            *request.existing_nfrs,
            request.additional_instructions or "",
        )
    )
    negative_pattern = re.compile(
        r"\b(?:no|not|without|unknown|unspecified|unconfirmed|"
        r"has not|have not|hasn't|haven't)\b",
        re.IGNORECASE,
    )
    for sentence in re.split(r"(?<=[.!?;])\s+", supplied_context):
        lowered_sentence = sentence.lower()
        if any(term.lower() in lowered_sentence for term in terms) and not (
            negative_pattern.search(lowered_sentence)
        ):
            return True
    return False


def _contains_named_term(text: str, term: str) -> bool:
    return bool(
        re.search(
            rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])",
            text,
            re.IGNORECASE,
        )
    )


def _expected_relevant_categories(case: dict) -> set[str]:
    return set(case.get("expected_relevant_categories", ()))


def evaluate_nfr_response(
    case: dict,
    analysis: NfrRecommendationResponse,
) -> NfrEvaluationResult:
    request: NfrRecommendationRequest = case["request"]
    checks: list[NfrEvaluationCheck] = []
    recommendations = analysis.recommendations
    recommendation_ids = [item.nfr_id for item in recommendations]
    ids_set = set(recommendation_ids)
    assessments = analysis.relevant_categories
    category_names = [item.category for item in assessments]
    request_text = _request_text(request)

    _record_check(
        checks,
        "At least one recommendation exists",
        [] if recommendations else ["No NFR recommendations were generated."],
        f"Generated {len(recommendations)} recommendation(s).",
    )

    repeated_ids = [
        identifier
        for identifier, count in Counter(recommendation_ids).items()
        if count > 1
    ]
    _record_check(
        checks,
        "NFR IDs are unique",
        [f"NFR ID {identifier} appears more than once." for identifier in repeated_ids],
        "All NFR IDs are unique.",
    )

    malformed_requirements = [
        item.nfr_id
        for item in recommendations
        if not item.requirement.strip().startswith("The system shall")
    ]
    _record_check(
        checks,
        'Every recommendation begins with "The system shall"',
        [
            f"{identifier} does not begin with 'The system shall'."
            for identifier in malformed_requirements
        ],
        "Every recommendation begins with 'The system shall'.",
    )

    unreferenced = [
        item.nfr_id
        for item in recommendations
        if request.requirement_id.lower()
        not in " ".join(
            (item.requirement, *item.source_references)
        ).lower()
    ]
    _record_check(
        checks,
        "Every recommendation references the supplied requirement ID",
        [
            f"{identifier} does not reference {request.requirement_id}."
            for identifier in unreferenced
        ],
        f"Every recommendation references {request.requirement_id}.",
    )

    invalid_categories = [
        item.category
        for item in recommendations
        if item.category not in ALLOWED_CATEGORIES
    ] + [
        item.category
        for item in assessments
        if item.category not in ALLOWED_CATEGORIES
    ]
    _record_check(
        checks,
        "Every category uses an allowed schema category",
        [f"Invalid category {category!r}." for category in invalid_categories],
        "All categories use allowed schema values.",
    )

    missing_or_repeated_categories = [
        f"{category} appears {category_names.count(category)} times"
        for category in sorted(ALLOWED_CATEGORIES)
        if category_names.count(category) != 1
    ]
    extra_categories = sorted(set(category_names) - ALLOWED_CATEGORIES)
    if extra_categories:
        missing_or_repeated_categories.extend(
            f"unexpected category {category}" for category in extra_categories
        )
    _record_check(
        checks,
        "All 14 categories have exactly one category assessment",
        missing_or_repeated_categories,
        "Each of the 14 categories has exactly one assessment.",
    )

    irrelevant_with_ids = [
        item.category
        for item in assessments
        if not item.relevant and item.recommendation_ids
    ]
    _record_check(
        checks,
        "Irrelevant categories have no recommendation IDs",
        [
            f"{category} is irrelevant but lists recommendation IDs."
            for category in irrelevant_with_ids
        ],
        "Irrelevant categories have no recommendation IDs.",
    )

    id_assessment_count = Counter(
        identifier
        for assessment in assessments
        if assessment.relevant
        for identifier in assessment.recommendation_ids
    )
    incorrect_category_assignments = [
        f"{identifier} appears in {count} relevant assessments"
        for identifier, count in id_assessment_count.items()
        if count != 1
    ]
    incorrectly_unassigned = sorted(ids_set - set(id_assessment_count))
    incorrectly_assigned = sorted(set(id_assessment_count) - ids_set)
    incorrect_category_assignments.extend(
        f"{identifier} is not linked to any relevant category"
        for identifier in incorrectly_unassigned
    )
    incorrect_category_assignments.extend(
        f"unknown recommendation ID {identifier} is linked"
        for identifier in incorrectly_assigned
    )
    _record_check(
        checks,
        "Every recommendation ID appears in exactly one relevant category",
        incorrect_category_assignments,
        "Every recommendation ID appears in exactly one relevant category.",
    )

    dangling_ids = [
        f"{assessment.category}: {identifier}"
        for assessment in assessments
        for identifier in assessment.recommendation_ids
        if identifier not in ids_set
    ]
    _record_check(
        checks,
        "Category recommendation IDs refer to generated NFR IDs",
        [
            f"Unknown recommendation ID {identifier} is listed."
            for identifier in dangling_ids
        ],
        "All category recommendation IDs refer to generated NFRs.",
    )

    functional_only = []
    for item in recommendations:
        text = item.requirement.lower()
        quality_terms_found = {
            token for token in QUALITY_TERMS if token in text
        }
        source_overlap = max(
            _overlap_score(item.requirement, request.requirement_text),
            _overlap_score(item.requirement, request.business_context),
            *(
                [_overlap_score(item.requirement, rule) for rule in request.known_constraints]
                or [0.0]
            ),
        )
        if source_overlap >= 0.8 and not quality_terms_found:
            functional_only.append(item.nfr_id)
    _record_check(
        checks,
        "Recommendations do not restate functional behavior or business rules",
        [
            f"{identifier} appears to restate a supplied functional rule."
            for identifier in functional_only
        ],
        "Recommendations express quality requirements rather than functional rules.",
    )

    unsupported_targets = []
    for item in recommendations:
        text = _recommendation_text(item)
        patterns_found = [
            match.group(0)
            for pattern in (TARGET_PATTERN, OBJECTIVE_PATTERN)
            for match in pattern.finditer(text)
        ]
        unsupported_targets.extend(
            f"{item.nfr_id}: {target}"
            for target in patterns_found
            if not any(
                number in request_text
                for number in re.findall(r"\d+(?:[.,]\d+)?", target)
            )
        )
    _record_check(
        checks,
        "No unsupported numerical or policy targets are invented",
        unsupported_targets,
        "No unsupported numeric targets were found.",
    )

    invented_entities = [
        term
        for term in sorted(INVENTED_ENTITY_TERMS)
        if _contains_named_term(_all_output_text(analysis), term)
        and not _contains_named_term(request_text, term)
    ]
    _record_check(
        checks,
        "No regulation, standard, vendor, product, protocol, algorithm, architecture, database, or cloud service is invented",
        [f"Unsupported named technology or standard {term!r} appears." for term in invented_entities],
        "No unsupported named technology or standard was found.",
    )

    missing_rationale = [
        item.nfr_id for item in recommendations if not item.rationale.strip()
    ]
    missing_measurement = [
        item.nfr_id
        for item in recommendations
        if not item.measurement_method.strip()
    ]
    _record_check(
        checks,
        "Every recommendation has a rationale and measurement method",
        [
            *(
                f"{identifier} has no rationale."
                for identifier in missing_rationale
            ),
            *(
                f"{identifier} has no measurement method."
                for identifier in missing_measurement
            ),
        ],
        "Every recommendation has a rationale and measurement method.",
    )

    ready_failures = [
        f"{item.nfr_id} is Ready but not measurable."
        for item in recommendations
        if item.status == "Ready" and not item.measurable
    ] + [
        f"{item.nfr_id} is Ready but has missing_target={item.missing_target!r}."
        for item in recommendations
        if item.status == "Ready" and item.missing_target
    ]
    _record_check(
        checks,
        "Ready recommendations are measurable and have no missing target",
        ready_failures,
        "All Ready recommendations are measurable and have no missing target.",
    )

    needs_target_failures = [
        f"{item.nfr_id} has Needs Target without measurable=true."
        for item in recommendations
        if item.status == "Needs Target" and not item.measurable
    ] + [
        f"{item.nfr_id} has Needs Target without a missing target."
        for item in recommendations
        if item.status == "Needs Target"
        and not (item.missing_target and item.missing_target.strip())
    ] + [
        f"{item.nfr_id} has Needs Target without human validation."
        for item in recommendations
        if item.status == "Needs Target" and not item.requires_human_validation
    ] + [
        f"{item.nfr_id} has Needs Target without a validation reason."
        for item in recommendations
        if item.status == "Needs Target"
        and not (item.validation_reason and item.validation_reason.strip())
    ]
    _record_check(
        checks,
        "Needs Target recommendations include a measurable target, validation, and reason",
        needs_target_failures,
        "Needs Target recommendations include all required review details.",
    )

    clarification_failures = [
        f"{item.nfr_id} has Needs Clarification without human validation."
        for item in recommendations
        if item.status == "Needs Clarification"
        and not item.requires_human_validation
    ] + [
        f"{item.nfr_id} has Needs Clarification without a validation reason."
        for item in recommendations
        if item.status == "Needs Clarification"
        and not (item.validation_reason and item.validation_reason.strip())
    ]
    _record_check(
        checks,
        "Needs Clarification recommendations include human validation and a reason",
        clarification_failures,
        "Needs Clarification recommendations include validation and a reason.",
    )

    irrelevant_supported = [
        f"{category} is marked irrelevant despite a supported missing target."
        for category in _expected_relevant_categories(case)
        for assessment in assessments
        if assessment.category == category and not assessment.relevant
    ]
    _record_check(
        checks,
        "A missing target does not make an otherwise relevant category irrelevant",
        irrelevant_supported,
        "Missing targets do not suppress supported category relevance.",
    )

    high_critical_failures = []
    if case["case_id"] == "high_criticality_transaction_missing_targets":
        for category in ("Performance", "Availability", "Recoverability"):
            assessment = next(
                (item for item in assessments if item.category == category),
                None,
            )
            if assessment is None or not assessment.relevant:
                high_critical_failures.append(
                    f"{category} must be relevant for this high-criticality transaction."
                )
                continue
            linked = [
                item for item in recommendations
                if item.nfr_id in assessment.recommendation_ids
            ]
            if not linked or any(item.status != "Needs Target" for item in linked):
                high_critical_failures.append(
                    f"{category} must have Needs Target recommendations."
                )
    _record_check(
        checks,
        "High-criticality transactions identify performance, availability, and recovery targets",
        high_critical_failures,
        "Performance, availability, and recoverability are Needs Target.",
    )

    relevance_failures = []
    explicitly_supplied_compliance = _has_positive_evidence(
        request,
        ("policy", "regulation", "contractual obligation", "compliance control"),
    )
    compliance = next(
        (item for item in assessments if item.category == "Compliance"), None
    )
    if compliance and compliance.relevant and not explicitly_supplied_compliance:
        relevance_failures.append(
            "Compliance is relevant without a supplied policy, regulation, "
            "contractual obligation, or control."
        )

    explicitly_supplied_accessibility = _has_positive_evidence(
        request,
        ("accessibility", "accessible", "wcag", "screen reader"),
    )
    accessibility = next(
        (item for item in assessments if item.category == "Accessibility"), None
    )
    if (
        accessibility
        and accessibility.relevant
        and not explicitly_supplied_accessibility
    ):
        relevance_failures.append(
            "Accessibility is relevant without a supplied accessibility need or constraint."
        )

    explicitly_supplied_compatibility = _has_positive_evidence(
        request,
        COMPATIBILITY_TERMS,
    )
    compatibility = next(
        (item for item in assessments if item.category == "Compatibility"), None
    )
    if (
        compatibility
        and compatibility.relevant
        and not explicitly_supplied_compatibility
    ):
        relevance_failures.append(
            "Compatibility is relevant without a supplied platform, device, "
            "browser, protocol, interface, or external system."
        )
    _record_check(
        checks,
        "Compliance, accessibility, and compatibility relevance are grounded",
        relevance_failures,
        "Compliance, accessibility, and compatibility relevance are grounded in the request.",
    )

    existing_nfrs = request.existing_nfrs
    regenerated = []
    for recommendation in recommendations:
        for existing in existing_nfrs:
            if _overlap_score(recommendation.requirement, existing) >= 0.75:
                regenerated.append(
                    f"{recommendation.nfr_id} substantially overlaps existing NFR {existing!r}."
                )
    _record_check(
        checks,
        "Existing NFRs are not substantially regenerated",
        regenerated,
        "Recommendations do not substantially regenerate existing NFRs.",
    )

    duplicate_input = any(
        _overlap_score(existing_nfrs[left], existing_nfrs[right]) >= 0.65
        for left in range(len(existing_nfrs))
        for right in range(left + 1, len(existing_nfrs))
    )
    duplicate_failures = []
    if len(existing_nfrs) == 1 and analysis.duplicate_existing_nfrs:
        duplicate_failures.append(
            "A single existing NFR was reported as a duplicate."
        )
    if duplicate_input and not analysis.duplicate_existing_nfrs:
        duplicate_failures.append(
            "Overlapping existing NFRs were not reported as duplicates."
        )
    _record_check(
        checks,
        "Existing NFR duplicate reporting distinguishes single and overlapping entries",
        duplicate_failures,
        "Duplicate reporting matches the supplied existing NFRs.",
    )

    security_inventions = [
        term
        for term in SECURITY_INVENTION_TERMS
        if any(
            term in _recommendation_text(item).lower()
            for item in recommendations
            if item.category == "Security"
        )
        and term not in request_text
    ]
    _record_check(
        checks,
        "Security recommendations avoid invented events, alerts, protocols, integrations, and log payloads",
        [f"Security recommendation invents {term!r}." for term in security_inventions],
        "Security recommendations contain no prohibited invented details.",
    )

    audit_inventions = [
        term
        for term in AUDIT_INVENTION_TERMS
        if any(
            term in _recommendation_text(item).lower()
            for item in recommendations
            if item.category == "Auditability"
        )
        and term not in request_text
    ]
    _record_check(
        checks,
        "Auditability recommendations avoid invented fields, immutability, retention, and storage behavior",
        [f"Auditability recommendation invents {term!r}." for term in audit_inventions],
        "Auditability recommendations contain no prohibited invented details.",
    )

    _record_check(
        checks,
        "Human validation is not empty",
        [] if analysis.human_validation_required else ["No human validation items were reported."],
        "Human validation items were reported.",
    )

    needs_approved_decision = any(
        item.status in {"Needs Target", "Needs Clarification"}
        or item.missing_target
        for item in recommendations
    )
    missing_info_failures = []
    if needs_approved_decision and not analysis.missing_information:
        missing_info_failures.append(
            "No missing information was reported despite an unresolved target or policy."
        )
    _record_check(
        checks,
        "Missing information is reported when a required target or policy decision is unresolved",
        missing_info_failures,
        "Required missing targets or decisions are reported as missing information.",
    )

    unsupported_recommendations = []
    for assessment in assessments:
        if assessment.relevant:
            continue
        for identifier in assessment.recommendation_ids:
            recommendation = next(
                (item for item in recommendations if item.nfr_id == identifier),
                None,
            )
            if recommendation and not any(
                term in _request_text(request)
                for term in (
                    assessment.category.lower(),
                    *(
                        {
                            "Accessibility": ("accessibility", "accessible"),
                            "Compliance": ("policy", "regulation", "compliance"),
                            "Compatibility": COMPATIBILITY_TERMS,
                        }.get(assessment.category, ())
                    ),
                )
            ):
                unsupported_recommendations.append(
                    f"{assessment.category} has an unsupported generic recommendation."
                )
    _record_check(
        checks,
        "Unsupported categories do not receive generic recommendations",
        unsupported_recommendations,
        "Unsupported categories do not receive generic recommendations.",
    )

    expected_relevant = _expected_relevant_categories(case)
    case_relevance_failures = [
        f"{category} was not marked relevant."
        for category in sorted(expected_relevant)
        for assessment in assessments
        if assessment.category == category and not assessment.relevant
    ]
    explicitly_irrelevant = set(case.get("expected_irrelevant_categories", ()))
    case_relevance_failures.extend(
        f"{category} was marked relevant without case evidence."
        for category in sorted(explicitly_irrelevant)
        for assessment in assessments
        if assessment.category == category and assessment.relevant
    )
    if case["case_id"] == "restricted_data_security_privacy_review":
        human_text = " ".join(analysis.human_validation_required).lower()
        for category in ("Security", "Privacy"):
            if not any(item.category == category and item.relevant for item in assessments):
                case_relevance_failures.append(
                    f"{category} review is required for restricted data."
                )
        if not any(
            term in human_text
            for term in ("security", "privacy", "policy", "classification")
        ):
            case_relevance_failures.append(
                "Human validation does not call for a security or privacy review."
            )

    if case["case_id"] == "explicit_compatibility_constraint":
        if compatibility is None or not compatibility.relevant:
            case_relevance_failures.append(
                "Compatibility must be relevant when an interface constraint is supplied."
            )
    if (
        case["case_id"] == "existing_nfr_duplicate_avoidance"
        and len(existing_nfrs) == 1
    ):
        if analysis.duplicate_existing_nfrs:
            case_relevance_failures.append(
                "A single existing NFR must not be reported as a duplicate."
            )
    _record_check(
        checks,
        "Case-specific category and duplicate expectations are met",
        case_relevance_failures,
        "Case-specific category and duplicate expectations are met.",
    )

    failed_count = sum(not check.passed for check in checks)
    return NfrEvaluationResult(
        case_id=case["case_id"],
        passed=failed_count == 0,
        score=round((len(checks) - failed_count) / len(checks) * 100, 2),
        checks=checks,
        analysis=analysis,
    )
