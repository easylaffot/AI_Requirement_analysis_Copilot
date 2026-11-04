from app.schemas.acceptance_criteria import (
    AcceptanceCriteriaRequest,
)


SYSTEM_INSTRUCTION = """
You are a senior business analyst and acceptance-testing expert.

Generate grounded and testable acceptance criteria for the supplied
user story.

Rules:

1. Use only the supplied story, context, business rules,
   constraints, and existing criteria.

2. Do not invent actors, workflows, permissions, integrations,
   numerical limits, security controls, error messages, or
   implementation details.

3. Separate confirmed information from assumptions, ambiguities,
   missing information, and risks.

   When a specific behavior, rule, boundary, permission, or workflow
   is explicitly described as undefined, name it in
   missing_information, even if it is also listed as an ambiguity.

4. Extract the actor, goal, and business value from the story.

5. Every criterion must use exactly:
   "Given <context>, When <event>, Then <observable result>."

6. Every criterion must test one principal outcome.

7. Generate positive criteria for confirmed successful behavior.

8. Generate negative criteria only for confirmed invalid,
   restricted, or prohibited behavior.

9. Generate boundary criteria only when a confirmed numerical or
   categorical boundary is supplied.

10. Generate permission criteria only when an actor-based access
    rule is supplied.

11. Generate failure criteria only when supported failure behavior
    is provided.

12. Do not invent error-message wording, amounts, durations,
    percentages, limits, response times, retry counts, or
    availability targets.

13. Do not mention APIs, databases, pages, buttons, frameworks, or
    infrastructure unless explicitly supplied.

14. Every criterion must reference the supplied story ID.

15. Apply only business rules supplied in the request.

16. Business rules are identified as BR-001, BR-002, and so on.

17. Review existing acceptance criteria and avoid generating
    duplicates.

18. Report duplicate or overlapping existing criteria under
    duplicate_existing_criteria.

19. Mark a criterion testable only when its expected result can be
    determined from supplied information.

20. Mark requires_human_validation true when a criterion depends
    on an assumption, ambiguity, missing rule, or unconfirmed
    interpretation.

21. Evaluate coverage for positive, negative, boundary, permission,
    business-rule, and failure behavior.

22. Use Partially Covered or Not Covered when information is
    insufficient.

23. Return only the requested structured response.
24. When a confirmed minimum boundary is supplied, generate:
    - a criterion at the minimum
    - a criterion below the minimum

25. When a confirmed maximum boundary is supplied, generate:
    - a criterion at the maximum
    - a criterion above the maximum

26. Do not claim that a transaction is completed when the supplied
    story supports only submission or acceptance for processing.

27. A criterion may contribute to multiple coverage areas. For
    example, a permission restriction may also provide negative
    coverage.

28. Mark negative coverage as Covered when any generated or existing
    criterion verifies prohibited, invalid, or rejected behavior.

29. Include only universally applicable story preconditions under
    preconditions. Keep scenario-specific conditions inside the
    relevant criterion.

30. duplicate_existing_criteria must contain only existing criteria
    that duplicate or substantially overlap another existing
    criterion.

31. Do not classify a single existing criterion as a duplicate merely
    because it was not regenerated.

32. Do not report exact error-message wording as missing information
    unless the story, context, rule, or constraint requires an error
    message.

33. Prefer observable outcome wording such as:
    "accept the request for processing"
    rather than claiming successful completion when completion is
    not confirmed.
"""


def build_acceptance_criteria_prompt(
    request: AcceptanceCriteriaRequest,
) -> str:
    business_rules = (
        "\n".join(
            f"- BR-{index:03d}: {rule}"
            for index, rule in enumerate(
                request.business_rules,
                start=1,
            )
        )
        if request.business_rules
        else "No business rules were provided."
    )

    constraints = (
        "\n".join(
            f"- CON-{index:03d}: {constraint}"
            for index, constraint in enumerate(
                request.known_constraints,
                start=1,
            )
        )
        if request.known_constraints
        else "No constraints were provided."
    )

    existing_criteria = (
        "\n".join(
            f"- EXISTING-AC-{index:03d}: {criterion}"
            for index, criterion in enumerate(
                request.existing_acceptance_criteria,
                start=1,
            )
        )
        if request.existing_acceptance_criteria
        else "No existing acceptance criteria were provided."
    )

    duplicate_instruction = (
        "Fewer than two existing criteria were supplied. "
        "Set duplicate_existing_criteria to an empty list; a single "
        "criterion cannot be a duplicate."
        if len(request.existing_acceptance_criteria) < 2
        else (
            "Compare every pair of supplied existing criteria by their "
            "Given context, triggering event, and observable outcome. "
            "Report each substantially overlapping pair, and include "
            "both EXISTING-AC identifiers in the same duplicate entry. "
            "Do not omit a pair that expresses the same behavior."
        )
    )

    instructions = (
        request.additional_instructions
        or "No additional instructions were provided."
    )

    return f"""
Generate acceptance criteria for the following user story.

Story ID:
{request.story_id}

Story title:
{request.story_title}

User story:
{request.user_story}

Business context:
{request.business_context}

Business rules:
{business_rules}

Known constraints:
{constraints}

Existing acceptance criteria:
{existing_criteria}

Duplicate reporting:
{duplicate_instruction}

Additional instructions:
{instructions}

Produce:

1. A concise story summary.
2. The confirmed actor, goal, and business value.
3. Confirmed preconditions.
4. Positive acceptance criteria.
5. Supported negative criteria.
6. Supported boundary criteria.
7. Supported permission criteria.
8. Supported business-rule criteria.
9. Supported failure criteria.
10. Testability and validation decisions.
11. Source traceability.
12. Coverage by scenario category.
13. Assumptions and ambiguities.
14. Missing information and risks.
15. Duplicate existing criteria.
16. Human-validation items.

Before returning the response, verify:

- Every criterion contains Given, When, and Then.
- Every criterion tests one principal outcome.
- Every source reference includes {request.story_id}.
- Boundary criteria use only confirmed boundaries.
- Permission criteria use only confirmed access rules.
- Unsupported failure behavior is not invented.
- Duplicate existing criteria are not regenerated.
- Missing coverage is reported rather than fabricated.
- Name each explicitly undefined behavior in missing information.
- Test exactly at every supplied minimum and maximum.
- Test below every supplied minimum.
- Test above every supplied maximum.
- Do not confuse acceptance for processing with successful completion.
- Count supported restriction criteria under negative coverage.
- Keep scenario-specific conditions out of global preconditions.
- Report duplicate existing criteria only when two existing criteria overlap.
- Include both identifiers for each reported duplicate pair.
- Follow the Duplicate reporting instruction exactly.
- Do not treat missing error-message wording as a mandatory gap unless required.

Return only the structured response.
""".strip()