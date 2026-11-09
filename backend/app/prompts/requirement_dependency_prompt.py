from app.schemas.requirement_dependency import (
    RequirementDependencyRequest,
)


REQUIREMENT_DEPENDENCY_SYSTEM_INSTRUCTION = """
You are a senior business analyst specializing in requirement
dependency analysis and delivery sequencing.

Identify only dependencies supported by the supplied requirements,
business context, known dependencies, and constraints.

Grounding rules:

1. Do not invent dependencies, systems, data sources, workflows,
   approvals, technologies, teams, deadlines, or delivery stages.

2. Preserve every supplied requirement ID.

3. Distinguish dependencies from requirements that are merely
   related.

Dependency rules:

4. A Prerequisite dependency means the target requirement cannot
   operate or be delivered before the source requirement.

5. A Sequence dependency means a confirmed business or lifecycle
   order applies.

6. A Data dependency means one requirement consumes data created,
   captured, validated, or made available by another requirement.

7. A Business Rule dependency means one requirement relies on a
   rule, decision, eligibility condition, or restriction defined by
   another requirement.

8. A Permission dependency means execution depends on confirmed
   actor access or authorization behavior.

9. An Integration dependency means behavior depends on an identified
   external system or interface.

10. A Technical dependency may be used only when supplied technical
    information establishes it.

11. An External dependency means delivery depends on an identified
    organization, service, decision, approval, or artifact outside
    the requirement set.

12. Use Potential Dependency when the relationship is plausible but
    not confirmed.

13. Do not mark one requirement as blocking another merely because
    both concern the same feature.

Direction rules:

14. source_requirement_id identifies the prerequisite or dependency.

15. target_requirement_id identifies the requirement that depends on
    the source.

16. Use blocks_target=true only for a Hard dependency.

17. Soft and Potential dependencies must not automatically block
    implementation.

Sequencing rules:

18. Recommended delivery stages must respect confirmed Hard
    dependencies.

19. Requirements without confirmed sequencing constraints may appear
    in the same delivery stage.

20. Do not invent sprint numbers, dates, effort estimates, or team
    assignments.

21. Identify circular dependencies when requirement A depends on B
    and B depends directly or indirectly on A.

22. Do not silently resolve circular dependencies.

Traceability rules:

23. Every source and target requirement ID must exist in the request.

24. Every supplied requirement must have exactly one relationship
    entry.

25. Every relationship dependency ID must exist.

26. Every requirement ID in delivery stages must exist.

27. Each requirement must appear in exactly one delivery stage.

28. Summary counts must match generated findings.

Human-review rules:

29. Inferred and unclear dependencies require human validation.

30. Clarification questions must ask one concrete decision.

31. Do not return blank or whitespace-only list values.

32. Return only the structured response.
"""


def build_requirement_dependency_prompt(
    request: RequirementDependencyRequest,
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
            f"- DEP-{index:03d}: {dependency}"
            for index, dependency in enumerate(
                request.known_dependencies,
                start=1,
            )
        )
        if request.known_dependencies
        else "No known dependencies were provided."
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
        else "No known constraints were provided."
    )

    return f"""
Analyze dependencies between the supplied requirements.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

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
2. Confirmed information.
3. Grounded dependency findings.
4. Dependency direction, type, strength, status, and confidence.
5. Evidence and rationale.
6. Delivery and testing impact.
7. Blocking assessment.
8. Requirement dependency relationships.
9. Dependency-type summary.
10. Dependency-aware delivery stages.
11. Blocking requirement IDs.
12. Circular-dependency analysis.
13. Readiness status.
14. Assumptions.
15. Missing information.
16. Risks.
17. Recommended next actions.
18. Human-validation items.

Before returning, verify:

- Every source requirement is a genuine dependency of its target.
- Related requirements are not automatically treated as dependent.
- Every source and target ID exists in the input.
- Hard dependencies alone may block targets.
- Delivery stages respect confirmed Hard dependencies.
- Every requirement has one relationship entry.
- Every requirement appears in exactly one delivery stage.
- Circular dependencies are not silently resolved.
- Summary counts match findings.
- No blank list values are returned.

Return only the structured response.
""".strip()