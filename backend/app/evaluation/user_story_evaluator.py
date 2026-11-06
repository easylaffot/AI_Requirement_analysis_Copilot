import re
from collections import Counter

from pydantic import BaseModel

from app.schemas.user_story import (
    UserStoryGenerationRequest,
    UserStoryGenerationResponse,
)


ALLOWED_PRIORITIES = {"Critical", "High", "Medium", "Low"}
VAGUE_ACTORS = {
    "user",
    "users",
    "system user",
    "system users",
    "stakeholder",
    "stakeholders",
    "application",
}
ACTION_VERBS = (
    "add",
    "create",
    "view",
    "modify",
    "update",
    "edit",
    "delete",
    "remove",
    "submit",
    "validate",
    "approve",
    "reject",
    "notify",
    "download",
    "export",
    "activate",
    "deactivate",
    "enforce",
    "restrict",
    "authorize",
    "calculate",
    "record",
)
RESTRICTION_TERMS = (
    "only",
    "must not",
    "may not",
    "cannot",
    "can not",
    "prohibited",
    "restricted",
    "not allowed",
    "not permitted",
)
ENFORCEMENT_TERMS = (
    "enforce",
    "enforcing",
    "enforcement",
    "authorization",
    "authorize",
    "security",
    "compliance",
    "restrict access",
    "prevent access",
    "block access",
)
UNSUPPORTED_DETAIL_PATTERNS = {
    "OTP rules": re.compile(r"\botp\b", re.IGNORECASE),
    "waiting periods": re.compile(
        r"\b(?:wait(?:ing)? period|wait for|within \d+|after \d+)\b",
        re.IGNORECASE,
    ),
    "screens or interface details": re.compile(
        r"\b(?:screen|page|form|button|user interface|ui)\b",
        re.IGNORECASE,
    ),
    "APIs": re.compile(r"\bapi(?:s)?\b", re.IGNORECASE),
    "database details": re.compile(
        r"\b(?:database|db table|table schema|sql|query)\b",
        re.IGNORECASE,
    ),
}
NUMBER_WITH_UNIT = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:%|"
    r"ms|milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)
SPELLED_DURATION = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"several|a few|a couple of)\s+"
    r"(?:milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)


class UserStoryEvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class UserStoryEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[UserStoryEvaluationCheck]
    analysis: UserStoryGenerationResponse


def _record_check(
    checks: list[UserStoryEvaluationCheck],
    name: str,
    failures: list[str],
    success_message: str,
) -> None:
    checks.append(
        UserStoryEvaluationCheck(
            name=name,
            passed=not failures,
            message="; ".join(failures) if failures else success_message,
        )
    )


def _request_text(request: UserStoryGenerationRequest) -> str:
    return " ".join(
        [
            request.requirement_title,
            request.requirement_text,
            request.business_context,
            *request.known_actors,
            *request.business_rules,
            request.additional_instructions or "",
        ]
    )


def _story_prose(story: object) -> str:
    acceptance_criteria = getattr(story, "acceptance_criteria")
    invest_assessment = getattr(story, "invest_assessment")
    text_fields = [
        getattr(story, "title"),
        getattr(story, "actor"),
        getattr(story, "goal"),
        getattr(story, "business_value"),
        getattr(story, "story"),
        getattr(story, "priority_justification"),
        getattr(story, "splitting_reason") or "",
        *getattr(story, "business_rules_applied"),
        *getattr(story, "dependencies"),
        *[
            getattr(criterion, "criterion")
            for criterion in acceptance_criteria
        ],
        *[
            getattr(invest_assessment, f"{name}_reason")
            for name in (
                "independent",
                "negotiable",
                "valuable",
                "estimable",
                "small",
                "testable",
            )
        ],
    ]
    return " ".join(text_fields)


def _goal_has_multiple_independent_actions(goal: str) -> bool:
    normalized_goal = re.sub(
        r"\bapprove(?:s|d)?\s+or\s+reject(?:s|ed)?\b",
        "decide",
        goal.lower(),
    )
    matches = [
        match
        for verb in ACTION_VERBS
        for match in re.finditer(
            rf"\b{re.escape(verb)}(?:s|es|ed|ing)?\b",
            normalized_goal,
        )
    ]
    return len(matches) > 1


def _is_clear_external_dependency(
    dependency: str,
    supplied_context: str,
) -> bool:
    text = dependency.strip().lower()
    if len(text.split()) < 3:
        return False
    condition_markers = (
        "external",
        "existing",
        "business condition",
        "must be",
        "must exist",
        "must already exist",
        "must be available",
        "requires",
        "provided",
        "once ",
        "after ",
        "when ",
        "before ",
        "subject to",
        "is available",
        "are available",
        "available data",
        "existing records",
        "existing payees",
        " exists",
    )
    if not any(marker in text for marker in condition_markers):
        return False

    ignored_terms = {
        "after",
        "already",
        "available",
        "before",
        "business",
        "condition",
        "data",
        "exist",
        "exists",
        "external",
        "existing",
        "for",
        "in",
        "is",
        "must",
        "of",
        "provided",
        "requires",
        "subject",
        "system",
        "the",
        "to",
        "when",
        "with",
    }

    def meaningful_terms(value: str) -> set[str]:
        terms = set(re.findall(r"[a-z0-9]+", value))
        normalized = {
            term[:-1] if len(term) > 4 and term.endswith("s") else term
            for term in terms
        }
        return normalized - ignored_terms

    supplied_terms = meaningful_terms(supplied_context.lower())
    return bool(meaningful_terms(text) & supplied_terms)


def _matches_missing_topic(
    topic: str,
    missing_information: list[str],
) -> bool:
    content = " ".join(missing_information).lower()
    topic = topic.lower()
    equivalents = {
        "actor": ("actor", "user role", "user type", "who will", "who should"),
        "business value": ("business value", "benefit", "intended value", "purpose"),
        "validation": ("validation", "validation rule", "acceptance rule", "criteria"),
    }
    terms = equivalents.get(topic, (topic,))
    return any(term in content for term in terms)


def evaluate_user_story_generation(
    case_id: str,
    analysis: UserStoryGenerationResponse,
    request: UserStoryGenerationRequest,
    *,
    confirmed_restrictions: list[str] | None = None,
    confirmed_boundaries: list[str] | None = None,
    expected_missing_topics: list[str] | None = None,
    minimum_story_count: int = 1,
    estimable_should_be_false: bool = False,
    priority_is_explicit: bool = False,
) -> UserStoryEvaluationResult:
    checks: list[UserStoryEvaluationCheck] = []
    stories = analysis.generated_stories
    input_text = _request_text(request).lower()
    confirmed_restrictions = confirmed_restrictions or [
        restriction
        for restriction in RESTRICTION_TERMS
        if restriction in input_text
    ]
    confirmed_boundaries = confirmed_boundaries or []
    expected_missing_topics = expected_missing_topics or []
    story_ids = [story.story_id for story in stories]
    valid_story_ids = set(story_ids)

    _record_check(
        checks,
        "At least one story is generated",
        [] if stories else ["No user stories were generated."],
        f"Generated {len(stories)} user story/stories.",
    )

    duplicate_ids = [
        story_id
        for story_id, count in Counter(story_ids).items()
        if count > 1
    ]
    _record_check(
        checks,
        "Story IDs are unique",
        [f"Story ID {story_id} appears more than once." for story_id in duplicate_ids],
        "All generated story IDs are unique.",
    )

    invalid_source_refs = [
        story.story_id
        for story in stories
        if "SOURCE-REQ-001" not in story.source_requirement_references
    ]
    _record_check(
        checks,
        "Every story references SOURCE-REQ-001",
        [
            f"Story {story_id} does not reference SOURCE-REQ-001."
            for story_id in invalid_source_refs
        ],
        "Every story references SOURCE-REQ-001.",
    )

    malformed_stories = [
        story
        for story in stories
        if not (
            re.search(r"\bAs an?\b", story.story, re.IGNORECASE)
            and re.search(r"\bI want to\b", story.story, re.IGNORECASE)
            and re.search(r"\bso that I can\b", story.story, re.IGNORECASE)
        )
    ]
    _record_check(
        checks,
        'Every story contains "As a/an", "I want to", and "so that I can"',
        [
            f"Story {story.story_id} does not use all required story phrases: "
            f"{story.story!r}"
            for story in malformed_stories
        ],
        "Every story uses the required user-story phrases.",
    )

    incomplete_fields = [
        f"{story.story_id}: {field_name}"
        for story in stories
        for field_name, value in (
            ("actor", story.actor),
            ("goal", story.goal),
            ("business value", story.business_value),
        )
        if not value.strip()
    ]
    _record_check(
        checks,
        "Every story has an actor, goal, and business value",
        [f"Missing non-empty story field: {item}." for item in incomplete_fields],
        "Every story has a non-empty actor, goal, and business value.",
    )

    vague_actors = [
        f"{story.story_id}: {story.actor!r}"
        for story in stories
        if story.actor.strip().lower() in VAGUE_ACTORS
        or re.search(r"\b(?:end )?user\b", story.actor, re.IGNORECASE)
        or re.search(r"\bstakeholder\b", story.actor, re.IGNORECASE)
    ]
    _record_check(
        checks,
        "Vague actors are rejected",
        [f"Story uses a vague actor: {actor}." for actor in vague_actors],
        "All story actors are specific.",
    )

    customer_enforcement = [
        story.story_id
        for story in stories
        if re.search(r"\bcustomer\b", story.actor, re.IGNORECASE)
        and any(
            term in f"{story.goal} {story.story}".lower()
            for term in ENFORCEMENT_TERMS
        )
    ]
    _record_check(
        checks,
        "Customers are not responsible for enforcing restrictions",
        [
            f"Customer actor in story {story_id} is assigned enforcement, "
            "authorization, security, or compliance responsibility."
            for story_id in customer_enforcement
        ],
        "No customer story assigns restriction enforcement responsibility.",
    )

    malformed_criteria = [
        f"{story.story_id}/{criterion.criterion_id}"
        for story in stories
        for criterion in story.acceptance_criteria
        if not all(
            re.search(rf"\b{word}\b", criterion.criterion, re.IGNORECASE)
            for word in ("Given", "When", "Then")
        )
    ]
    _record_check(
        checks,
        "Acceptance criteria contain Given, When, and Then",
        [
            f"Criterion {criterion_id} omits Given, When, or Then."
            for criterion_id in malformed_criteria
        ],
        "Every acceptance criterion contains Given, When, and Then.",
    )

    negative_criteria = [
        criterion
        for story in stories
        for criterion in story.acceptance_criteria
        if criterion.criterion_type == "Negative"
    ]
    if confirmed_restrictions and not negative_criteria:
        negative_failures = [
            "Confirmed restrictions were supplied but no Negative "
            "acceptance criterion was generated."
        ]
    else:
        negative_failures = []
    _record_check(
        checks,
        "Confirmed restrictions have negative acceptance criteria",
        negative_failures,
        (
            "Negative criteria are present for confirmed restrictions."
            if confirmed_restrictions
            else "No confirmed restriction requires a negative criterion."
        ),
    )

    boundary_criteria = [
        f"{story.story_id}/{criterion.criterion_id}"
        for story in stories
        for criterion in story.acceptance_criteria
        if criterion.criterion_type == "Boundary"
    ]
    unsupported_boundaries = (
        boundary_criteria if boundary_criteria and not confirmed_boundaries else []
    )
    _record_check(
        checks,
        "Boundary criteria are grounded in confirmed boundaries",
        [
            f"Boundary criterion {criterion_id} has no supplied boundary."
            for criterion_id in unsupported_boundaries
        ],
        (
            "Boundary criteria are supported by supplied boundaries."
            if boundary_criteria and confirmed_boundaries
            else "No unsupported boundary criteria were generated."
        ),
    )

    invented_details: list[str] = []
    numeric_input = set(re.findall(r"\d+(?:[.,]\d+)?", input_text))
    for story in stories:
        prose = re.sub(
            r"\b(?:SOURCE-REQ|BR|US)-\d{3}\b",
            "",
            _story_prose(story),
            flags=re.IGNORECASE,
        )
        for detail_name, pattern in UNSUPPORTED_DETAIL_PATTERNS.items():
            if pattern.search(prose) and not pattern.search(input_text):
                invented_details.append(f"{story.story_id} invents {detail_name}.")
        for match in NUMBER_WITH_UNIT.finditer(prose):
            number = re.match(r"\d+(?:[.,]\d+)?", match.group())
            if number and number.group() not in numeric_input:
                invented_details.append(
                    f"{story.story_id} invents numeric/duration detail "
                    f"{match.group()!r}."
                )
        for match in SPELLED_DURATION.finditer(prose):
            if not SPELLED_DURATION.search(input_text):
                invented_details.append(
                    f"{story.story_id} invents duration {match.group()!r}."
                )
        numeric_output = set(re.findall(r"\d+(?:[.,]\d+)?", prose))
        unsupported_numbers = numeric_output - numeric_input
        if unsupported_numbers:
            invented_details.append(
                f"{story.story_id} includes unsupported number(s): "
                + ", ".join(sorted(unsupported_numbers))
                + "."
            )
    _record_check(
        checks,
        "No unsupported numbers or implementation details are invented",
        invented_details,
        "No unsupported numbers, durations, OTP rules, or technical details found.",
    )

    invalid_priorities = [
        f"{story.story_id}: {story.priority!r}"
        for story in stories
        if story.priority not in ALLOWED_PRIORITIES
    ]
    empty_justifications = [
        story.story_id
        for story in stories
        if not story.priority_justification.strip()
    ]
    _record_check(
        checks,
        "Every story has a valid priority and justification",
        [
            *[
                f"Story {story_id} has invalid priority {priority}."
                for story_id, priority in (
                    (entry.split(": ", 1)[0], entry.split(": ", 1)[1])
                    for entry in invalid_priorities
                )
            ],
            *[
                f"Story {story_id} has no priority justification."
                for story_id in empty_justifications
            ],
        ],
        "Every story has an allowed priority and non-empty justification.",
    )

    priority_validation_failures = []
    if not priority_is_explicit:
        has_priority_validation = any(
            "product owner" in item.lower()
            and re.search(r"\bpriorit(?:y|ies)\b", item, re.IGNORECASE)
            for item in analysis.human_validation_required
        )
        if not has_priority_validation:
            priority_validation_failures.append(
                "Inferred priorities require Product Owner priority validation."
            )
    _record_check(
        checks,
        "Inferred priorities require Product Owner validation",
        priority_validation_failures,
        (
            "Product Owner priority validation is present."
            if not priority_is_explicit
            else "Priority was explicitly supplied."
        ),
    )

    invest_failures = [
        f"Story {story.story_id} has no reason for {criterion}."
        for story in stories
        for criterion in (
            "independent",
            "negotiable",
            "valuable",
            "estimable",
            "small",
            "testable",
        )
        if not getattr(story.invest_assessment, f"{criterion}_reason").strip()
    ]
    _record_check(
        checks,
        "Every INVEST field has a non-empty reason",
        invest_failures,
        "All six INVEST characteristics have explanations.",
    )

    if estimable_should_be_false:
        estimability_failures = (
            []
            if any(
                not story.invest_assessment.estimable
                for story in stories
            )
            else [
                "Important requirement details are missing, but every story "
                "is marked Estimable."
            ]
        )
    else:
        estimability_failures = []
    _record_check(
        checks,
        "Missing important details are reflected in Estimable assessment",
        estimability_failures,
        (
            "At least one affected story is marked not Estimable."
            if estimable_should_be_false and not estimability_failures
            else "No incomplete requirement requires a false Estimable result."
        ),
    )

    complex_goals = [
        story.story_id
        for story in stories
        if _goal_has_multiple_independent_actions(story.goal)
        and not (
            story.may_require_further_splitting
            and story.splitting_reason
            and story.splitting_reason.strip()
        )
    ]
    splitting_failures = [
        f"Story {story_id} has multiple independent goal actions without "
        "a splitting flag and reason."
        for story_id in complex_goals
    ]
    if len(stories) < minimum_story_count:
        splitting_failures.append(
            f"Generated {len(stories)} stories; expected at least "
            f"{minimum_story_count} for the independently testable actions."
        )
    missing_split_reasons = [
        story.story_id
        for story in stories
        if story.may_require_further_splitting
        and not (story.splitting_reason and story.splitting_reason.strip())
    ]
    splitting_failures.extend(
        f"Story {story_id} is marked for further splitting without a reason."
        for story_id in missing_split_reasons
    )
    _record_check(
        checks,
        "Independent goals are split or flagged with a reason",
        splitting_failures,
        "Independent goals are split or include a splitting reason.",
    )

    allowed_rule_ids = {
        f"BR-{index:03d}"
        for index, _ in enumerate(request.business_rules, start=1)
    }
    invalid_rule_references: list[str] = []
    for story in stories:
        for applied_rule in story.business_rules_applied:
            referenced_ids = re.findall(r"\bBR-\d{3}\b", applied_rule)
            if (
                not referenced_ids
                or any(rule_id not in allowed_rule_ids for rule_id in referenced_ids)
            ):
                invalid_rule_references.append(
                    f"{story.story_id} applies {applied_rule!r}; supplied IDs are "
                    f"{sorted(allowed_rule_ids)}."
                )
    _record_check(
        checks,
        "Applied business rules reference only supplied BR IDs",
        invalid_rule_references,
        "All applied business-rule references use supplied IDs.",
    )

    invalid_dependencies = [
        f"{story.story_id} has unclear dependency {dependency!r}."
        for story in stories
        for dependency in story.dependencies
        if dependency not in valid_story_ids
        and not _is_clear_external_dependency(
            dependency,
            _request_text(request),
        )
    ]
    _record_check(
        checks,
        "Dependencies reference stories or clear external conditions",
        invalid_dependencies,
        "All dependencies identify a generated story or clear external condition.",
    )

    missing_information_failures = [
        f"Missing information does not identify {topic!r}."
        for topic in expected_missing_topics
        if not _matches_missing_topic(topic, analysis.missing_information)
    ]
    _record_check(
        checks,
        "Incomplete requirements report expected missing information",
        missing_information_failures,
        (
            "Expected missing-information topics were reported."
            if expected_missing_topics
            else "No missing-information topics were required for this case."
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

    passed_count = sum(check.passed for check in checks)
    score = round(passed_count / len(checks) * 100, 2)
    return UserStoryEvaluationResult(
        case_id=case_id,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
        analysis=analysis,
    )
