from app.schemas.requirement_priority import (
    RequirementPriorityRequest,
)


REQUIREMENT_PRIORITY_SYSTEM_INSTRUCTION = """
You are a senior product owner and business analyst specializing in
evidence-based requirement prioritization.

Recommend requirement priorities using only the supplied release
objective, requirements, context, dependencies, constraints, and
explicit priority information.

Grounding rules:

1. Do not invent deadlines, costs, stakeholder commitments,
   regulations, customer volumes, financial losses, dependencies,
   priorities, or implementation estimates.

2. Preserve every requirement ID and title.

3. Distinguish explicitly stated priority from recommended priority.

4. Do not classify a requirement as Critical solely because it is
   in banking, security, compliance, or another sensitive domain.

Priority rules:

5. Critical means the release or every usable core workflow cannot
   operate without the requirement, or explicit evidence marks it
   critical.

6. High means the requirement provides substantial release value,
   resolves a material risk, or is an important dependency.

7. Medium means the requirement provides useful value but is not a
   prerequisite for the release objective.

8. Low means the requirement provides limited immediate release
   value and can reasonably be deferred.

9. Use Unknown when evidence is insufficient.

10. MoSCoW classification must be consistent with the recommended
    priority and supplied release objective.

11. Must Have must be supported by an unavoidable release need,
    confirmed obligation, or blocking dependency.

12. Won't Have This Release may be used only when supplied evidence
    supports explicit deferral. Otherwise use Unclassified.

Factor rules:

13. Assess business value, customer impact, urgency, risk reduction,
    compliance need, security need, dependency importance,
    operational impact, and implementation readiness.

14. Use Unknown when a factor is unsupported.

15. Every non-Unknown factor must cite valid evidence IDs.

16. Evidence must be an exact phrase or faithful short extract from
    supplied information.

Dependency rules:

17. Do not invent dependencies.

18. A blocking prerequisite may be prioritized above a dependent
    requirement when supported by supplied dependencies.

19. Recommended delivery order must respect known dependencies.

Readiness rules:

20. A high-value requirement may still be not ready for
    implementation.

21. Missing rules, actors, boundaries, integration details, or
    acceptance outcomes must be identified separately from priority.

22. Priority conflicts must be reported when stated priority and
    evidence-based priority materially disagree.

Human-review rules:

23. Every inferred Critical or High priority requires Product Owner
    validation.

24. Clarification questions must ask one concrete decision.

25. Priority-summary counts must match generated recommendations.

26. Every supplied requirement must appear exactly once.

27. Do not return blank list values.

28. Return structured output only.
"""


def build_requirement_priority_prompt(
    request: RequirementPriorityRequest,
) -> str:
    requirement_blocks: list[str] = []

    for index, requirement in enumerate(
        request.requirements,
        start=1,
    ):
        requirement_blocks.append(
            f"""
Requirement {index}

ID:
{requirement.requirement_id}

Title:
{requirement.title}

Category:
{requirement.category}

Stated priority:
{requirement.stated_priority}

Source document:
{requirement.source_document or "Not provided"}

Source section:
{requirement.source_section or "Not provided"}

Requirement text:
{requirement.requirement_text}
""".strip()
        )

    requirements_text = "\n\n---\n\n".join(
        requirement_blocks
    )

    dependencies = (
        "\n".join(
            f"- DEP-{index:03d}: {item}"
            for index, item in enumerate(
                request.known_dependencies,
                start=1,
            )
        )
        if request.known_dependencies
        else "No known dependencies were provided."
    )

    constraints = (
        "\n".join(
            f"- CON-{index:03d}: {item}"
            for index, item in enumerate(
                request.known_constraints,
                start=1,
            )
        )
        if request.known_constraints
        else "No known constraints were provided."
    )

    return f"""
Prioritize the supplied requirements.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Release objective:
{request.release_objective}

Prioritization method:
{request.prioritization_method}

Known dependencies:
{dependencies}

Known constraints:
{constraints}

Requirements:
--- REQUIREMENTS START ---

{requirements_text}

--- REQUIREMENTS END ---

Additional instructions:
{request.additional_instructions or "None supplied."}

Produce:

1. Analysis summary.
2. Release-objective summary.
3. One priority recommendation for every requirement.
4. MoSCoW classification.
5. Evidence strength.
6. Factor assessment.
7. Evidence and rationale.
8. Dependency-aware delivery order.
9. Priority-conflict detection.
10. Implementation-readiness assessment.
11. Missing information and clarification questions.
12. Priority summary.
13. Blocking requirement IDs.
14. Overall readiness.
15. Assumptions, risks, next actions, and human validation.

Before returning, verify:

- Every supplied requirement appears exactly once.
- Every evidence ID exists in the same requirement result.
- Unknown is used when evidence is insufficient.
- Critical and Must Have are not inferred without blocking evidence.
- Delivery order respects supplied dependencies.
- Priority and implementation readiness remain separate.
- Every inferred Critical or High priority requires human validation.
- Counts match the generated recommendations.
- No blank list values are returned.

Return structured output only.
""".strip()