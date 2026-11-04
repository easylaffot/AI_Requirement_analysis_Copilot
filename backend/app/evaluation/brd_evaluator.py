import re
from collections import Counter

from pydantic import BaseModel

from app.schemas.brd import BrdAnalysisResponse, Priority


ALLOWED_PRIORITIES: set[str] = {
    "Critical",
    "High",
    "Medium",
    "Low",
}

UNRESOLVED_PHRASES = (
    "not confirmed",
    "not specified",
    "unknown",
    "undecided",
    "pending decision",
)

UNRESOLVED_DETAIL_TERMS = (
    "not confirmed",
    "not specified",
    "unknown",
    "undecided",
    "pending",
    "not provided",
    "missing",
    "unresolved",
    "tbd",
    "to be determined",
)

INTEGRATION_DETAIL_TERMS = (
    "api",
    "endpoint",
    "authentication",
    "protocol",
    "field mapping",
    "error handling",
    "interface",
    "integration detail",
    "integration method",
)

LIMITATION_NOTE_TERMS = (
    "limitation",
    "not specified",
    "unknown",
    "unresolved",
    "pending",
    "not provided",
    "confirmed behavior",
    "only confirmed",
    "endpoint",
    "authentication",
    "protocol",
    "field mapping",
    "error handling",
    "integration detail",
)

INDEPENDENT_OUTCOME_TERMS = (
    "create",
    "start",
    "enter",
    "submit",
    "validate",
    "approve",
    "reject",
    "upload",
    "download",
    "generate",
    "notify",
    "send",
    "view",
    "edit",
    "cancel",
    "calculate",
    "reconcile",
    "trigger",
    "review",
    "recommend",
    "record",
)


class BrdEvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class BrdEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[BrdEvaluationCheck]
    analysis: BrdAnalysisResponse


def _contains_all_phrases(
    text: str,
    phrases: tuple[str, ...],
) -> bool:
    lowered_text = text.lower()
    return all(phrase in lowered_text for phrase in phrases)


def _story_has_multiple_outcomes(story_text: str) -> bool:
    story_goal = re.search(
        r"\bi want\s+(.+?),\s*so that\b",
        story_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if story_goal is None:
        return False

    lowered_goal = story_goal.group(1).lower()

    outcome_count = sum(
        bool(
            re.search(
                rf"\b{re.escape(term)}(?:s|es|ed|ing)?\b",
                lowered_goal,
            )
        )
        for term in INDEPENDENT_OUTCOME_TERMS
    )
    return outcome_count >= 3


def _tokens(text: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in stop_words
    }


def _check(
    checks: list[BrdEvaluationCheck],
    name: str,
    failures: list[str],
    success_message: str,
) -> None:
    checks.append(
        BrdEvaluationCheck(
            name=name,
            passed=not failures,
            message="; ".join(failures) if failures else success_message,
        )
    )


def evaluate_brd_analysis(
    case_id: str,
    analysis: BrdAnalysisResponse,
    brd_content: str,
    expected_missing_information: list[str] | None = None,
    minimum_story_count: int = 1,
) -> BrdEvaluationResult:
    checks: list[BrdEvaluationCheck] = []
    requirements = analysis.extracted_requirements
    epics = analysis.epics
    stories = [
        story
        for epic in epics
        for feature in epic.features
        for story in feature.user_stories
    ]
    requirement_ids = [requirement.requirement_id for requirement in requirements]
    valid_requirement_ids = set(requirement_ids)
    story_ids = [story.story_id for story in stories]
    valid_story_ids = set(story_ids)

    _check(
        checks,
        "At least one extracted requirement exists",
        [] if requirements else ["No extracted requirements were returned."],
        f"Found {len(requirements)} extracted requirement(s).",
    )
    _check(
        checks,
        "At least one epic exists",
        [] if epics else ["No epics were returned."],
        f"Found {len(epics)} epic(s).",
    )

    empty_epics = [epic.epic_id for epic in epics if not epic.features]
    _check(
        checks,
        "Every epic contains at least one feature",
        [f"Epic {epic_id} has no features." for epic_id in empty_epics],
        "Every epic contains at least one feature.",
    )

    empty_features = [
        feature.feature_id
        for epic in epics
        for feature in epic.features
        if not feature.user_stories
    ]
    _check(
        checks,
        "Every feature contains at least one user story",
        [
            f"Feature {feature_id} has no user stories."
            for feature_id in empty_features
        ],
        "Every feature contains at least one user story.",
    )

    malformed_stories = [
        story
        for story in stories
        if not re.match(
            r"^\s*As an? .+?, I want .+?, so that .+\s*$",
            story.story,
            flags=re.IGNORECASE | re.DOTALL,
        )
    ]
    _check(
        checks,
        "Every story uses the required user-story format",
        [
            f"Story {story.story_id} does not use "
            f'"As a/an..., I want..., so that..." format: {story.story!r}'
            for story in malformed_stories
        ],
        "Every story uses the required user-story format.",
    )

    invalid_criteria = [
        f"{story.story_id}/{criterion.criterion_id}"
        for story in stories
        for criterion in story.acceptance_criteria
        if not _contains_all_phrases(
            criterion.criterion,
            ("given", "when", "then"),
        )
    ]
    stories_without_criteria = [
        story.story_id for story in stories if not story.acceptance_criteria
    ]
    criteria_failures = [
        f"Acceptance criterion {criterion_id} omits Given, When, or Then."
        for criterion_id in invalid_criteria
    ] + [
        f"Story {story_id} has no acceptance criteria."
        for story_id in stories_without_criteria
    ]
    _check(
        checks,
        "Every acceptance criterion contains Given, When, and Then",
        criteria_failures,
        "Every story has acceptance criteria containing Given, When, and Then.",
    )

    stories_without_valid_requirement = [
        story.story_id
        for story in stories
        if not any(
            requirement_id in valid_requirement_ids
            for requirement_id in story.source_requirement_ids
        )
    ]
    invalid_story_requirement_refs = [
        f"{story.story_id}->{requirement_id}"
        for story in stories
        for requirement_id in story.source_requirement_ids
        if requirement_id not in valid_requirement_ids
    ]
    _check(
        checks,
        "Every story references at least one valid extracted requirement ID",
        [
            *[
                f"Story {story_id} has no valid requirement reference."
                for story_id in stories_without_valid_requirement
            ],
            *[
                f"Story reference {reference} does not exist."
                for reference in invalid_story_requirement_refs
            ],
        ],
        "Every story references valid extracted requirement IDs.",
    )

    invalid_epic_refs = [
        f"{epic.epic_id}->{requirement_id}"
        for epic in epics
        for requirement_id in epic.source_requirement_ids
        if requirement_id not in valid_requirement_ids
    ]
    invalid_feature_refs = [
        f"{feature.feature_id}->{requirement_id}"
        for epic in epics
        for feature in epic.features
        for requirement_id in feature.source_requirement_ids
        if requirement_id not in valid_requirement_ids
    ]
    _check(
        checks,
        "Every epic and feature references only valid extracted requirement IDs",
        [
            *[
                f"Invalid epic reference {reference}."
                for reference in invalid_epic_refs
            ],
            *[
                f"Invalid feature reference {reference}."
                for reference in invalid_feature_refs
            ],
        ],
        "All epic and feature requirement references exist.",
    )

    trace_counts = Counter(
        entry.requirement_id for entry in analysis.traceability
    )
    traceability_failures = [
        f"Requirement {requirement_id} has {trace_counts[requirement_id]} "
        "traceability entries (expected exactly one)."
        for requirement_id in requirement_ids
        if trace_counts[requirement_id] != 1
    ] + [
        f"Traceability entry {requirement_id} has no extracted requirement."
        for requirement_id in trace_counts
        if requirement_id not in valid_requirement_ids
    ]
    _check(
        checks,
        "Every extracted requirement has exactly one traceability entry",
        traceability_failures,
        "Every extracted requirement has exactly one traceability entry.",
    )

    invalid_trace_story_refs = [
        f"{entry.requirement_id}->{story_id}"
        for entry in analysis.traceability
        for story_id in entry.backlog_item_ids
        if story_id not in valid_story_ids
    ]
    _check(
        checks,
        "Every traceability backlog item ID refers to a generated story ID",
        [
            f"Invalid traceability backlog item reference {reference}."
            for reference in invalid_trace_story_refs
        ],
        "All traceability backlog item IDs refer to generated stories.",
    )

    invalid_priorities = [
        f"{story.story_id} has priority {story.priority!r}."
        for story in stories
        if story.priority not in ALLOWED_PRIORITIES
        or story.priority not in Priority.__args__
    ]
    _check(
        checks,
        "Priority is one of Critical, High, Medium, or Low",
        invalid_priorities,
        "Every story uses an allowed priority.",
    )

    empty_justifications = [
        story.story_id
        for story in stories
        if not story.priority_justification.strip()
    ]
    _check(
        checks,
        "Every story has a non-empty priority justification",
        [
            f"Story {story_id} has no priority justification."
            for story_id in empty_justifications
        ],
        "Every story has a priority justification.",
    )

    prohibited_requirements = [
        f"{requirement.requirement_id} contains "
        f"{phrase!r}: {requirement.requirement_text}"
        for requirement in requirements
        for phrase in UNRESOLVED_PHRASES
        if phrase in requirement.requirement_text.lower()
    ]
    _check(
        checks,
        "Unconfirmed information is not extracted as a requirement",
        prohibited_requirements,
        "No prohibited unresolved-information phrases appear in requirements.",
    )

    missing_information_text = "\n".join(analysis.missing_information).lower()
    expected_missing = expected_missing_information or []
    missing_expectation_failures = [
        f"Expected missing-information topic {topic!r} was not reported."
        for topic in expected_missing
        if topic.lower() not in missing_information_text
    ]
    unresolved_input_claims = [
        phrase
        for phrase in UNRESOLVED_PHRASES
        if phrase in brd_content.lower()
    ]
    unresolved_information_failures = [
        f"BRD contains {phrase!r}, but missing_information does not "
        "report the configured missing-information topics."
        for phrase in unresolved_input_claims
        if not expected_missing
    ]
    _check(
        checks,
        "Missing or undecided information appears in missing_information",
        [
            *missing_expectation_failures,
            *unresolved_information_failures,
        ],
        "Expected missing-information topics were reported.",
    )

    _check(
        checks,
        "human_validation_required is not empty",
        []
        if analysis.human_validation_required
        else ["No human-validation items were returned."],
        "Human-validation items were returned.",
    )

    duplicate_story_ids = [
        story_id for story_id, count in Counter(story_ids).items() if count > 1
    ]
    _check(
        checks,
        "There are no duplicate story IDs",
        [
            f"Story ID {story_id} appears more than once."
            for story_id in duplicate_story_ids
        ],
        "All story IDs are unique.",
    )

    duplicate_requirement_ids = [
        requirement_id
        for requirement_id, count in Counter(requirement_ids).items()
        if count > 1
    ]
    _check(
        checks,
        "There are no duplicate requirement IDs",
        [
            f"Requirement ID {requirement_id} appears more than once."
            for requirement_id in duplicate_requirement_ids
        ],
        "All extracted requirement IDs are unique.",
    )

    oversized_stories = [
        story.story_id
        for story in stories
        if _story_has_multiple_outcomes(story.story)
        and not (
            story.may_require_splitting
            and story.splitting_reason
            and story.splitting_reason.strip()
        )
    ]
    flagged_without_reason = [
        story.story_id
        for story in stories
        if story.may_require_splitting
        and not (story.splitting_reason and story.splitting_reason.strip())
    ]
    splitting_failures = [
        f"Story {story_id} has multiple outcome cues and is not split or "
        "flagged with a splitting reason."
        for story_id in oversized_stories
    ] + [
        f"Story {story_id} is flagged for splitting without a reason."
        for story_id in flagged_without_reason
        if story_id not in oversized_stories
    ]
    if len(stories) < minimum_story_count:
        splitting_failures.append(
            f"Found {len(stories)} user story/stories; expected at least "
            f"{minimum_story_count} for this workflow."
        )
    _check(
        checks,
        "Stories with multiple outcomes are split or flagged for splitting",
        splitting_failures,
        "Stories with multiple outcome cues are split or have a reasoned flag.",
    )

    trace_by_requirement = {
        entry.requirement_id: entry for entry in analysis.traceability
    }
    unresolved_integration_details = [
        item
        for item in analysis.missing_information
        if any(term in item.lower() for term in UNRESOLVED_DETAIL_TERMS)
        and any(term in item.lower() for term in INTEGRATION_DETAIL_TERMS)
    ]
    coverage_failures: list[str] = []
    for missing_item in unresolved_integration_details:
        missing_tokens = _tokens(missing_item)
        related_requirements = [
            requirement
            for requirement in requirements
            if requirement.category == "Integration"
            or len(
                missing_tokens & _tokens(requirement.requirement_text)
            )
            >= 2
        ]
        for requirement in related_requirements:
            entry = trace_by_requirement.get(requirement.requirement_id)
            if entry is None or entry.coverage_status != "Covered":
                continue

            linked_story_ids = set(entry.backlog_item_ids) & valid_story_ids
            requirement_stories = [
                story
                for story in stories
                if story.story_id in linked_story_ids
                and requirement.requirement_id in story.source_requirement_ids
            ]
            notes_explain_limitation = any(
                term in entry.notes.lower()
                for term in LIMITATION_NOTE_TERMS
            )
            if not requirement_stories or not notes_explain_limitation:
                coverage_failures.append(
                    f"Requirement {requirement.requirement_id} is Covered "
                    f"despite unresolved implementation details in "
                    f"{missing_item!r}, without linked confirmed behavior "
                    "and a limitation in traceability notes."
                )
    _check(
        checks,
        "Covered requirements explain unresolved implementation limitations",
        coverage_failures,
        "No Covered integration requirement hides unresolved details.",
    )

    passed_count = sum(check.passed for check in checks)
    score = round(passed_count / len(checks) * 100, 2)
    return BrdEvaluationResult(
        case_id=case_id,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
        analysis=analysis,
    )
