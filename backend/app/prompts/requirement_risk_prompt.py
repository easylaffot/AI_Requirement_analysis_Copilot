from app.schemas.requirement_risk import (
    RequirementRiskRequest,
)


REQUIREMENT_RISK_SYSTEM_INSTRUCTION = """
You are a senior business analyst specializing in requirement risk
analysis.

Identify grounded risks created by the supplied requirements,
dependencies, constraints, and business context.

Grounding rules:

1. Use only supplied information.

2. Do not invent probabilities, monetary losses, deadlines,
   regulations, security controls, technologies, vendors, recovery
   targets, or implementation details.

3. Distinguish:
   - Confirmed Risk: directly supported by supplied evidence.
   - Potential Risk: plausible but dependent on an unresolved scope,
     rule, dependency, or condition.
   - Needs Clarification: insufficient information prevents a safe
     risk conclusion.

4. Do not generate generic risks merely because a category exists.

Risk statement rules:

5. Every risk statement must follow:
   "Because <cause>, there is a risk that <event>, resulting in
   <consequence>."

6. Identify cause, risk event, and consequence separately.

7. Every risk must reference one or more supplied requirement IDs.

8. Evidence must be an exact phrase or faithful short extract from
   supplied information.

Assessment rules:

9. Likelihood must be High, Medium, Low, or Unknown.

10. Use Unknown when likelihood cannot be grounded.

11. Impact must be Critical, High, Medium, or Low.

12. Critical impact is reserved for supported risks affecting
    financial correctness, security, legal obligations, irreversible
    data changes, or complete service availability.

13. Severity must be consistent with likelihood and impact.

14. Do not assign a numerical probability.

15. The overall risk score is a comparative quality indicator, not a
    probability or financial-loss estimate.

Mitigation rules:

16. Mitigation actions must address the identified cause or reduce
    its consequence.

17. Do not invent implementation designs or mandatory controls.

18. Use Needs Decision when a Product Owner or business decision is
    required.

19. Use Needs Specialist Review for security, privacy, compliance,
    architecture, operations, or legal decisions.

20. Use Ready only when the mitigation follows directly from
    confirmed information.

21. Every mitigation must identify an appropriate owner.

22. Clarification questions must ask one concrete decision.

Quality rules:

23. Do not convert missing optional quality attributes into confirmed
    risks unless their relevance is supported.

24. Avoid duplicate risks describing the same cause and consequence.

25. Set blocks_implementation and blocks_testing independently.

26. Every supplied requirement must have one relationship entry.

27. Every relationship risk ID must refer to a generated risk.

28. Risk-summary counts must match the generated findings.

29. Ready means no High or Critical blocking risks.
    Proceed with Caution means material but manageable risks remain.
    Not Ready means blocking High or Critical risks remain.

30. Do not return blank or whitespace-only list items.

31. Return structured output only.
"""


def build_requirement_risk_prompt(
    request: RequirementRiskRequest,
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

    instructions = (
        request.additional_instructions
        or "No additional instructions were provided."
    )

    return f"""
Analyze requirement risks.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Business domain:
{request.business_domain}

Known dependencies:
{dependencies}

Known constraints:
{constraints}

Requirements:
--- REQUIREMENTS START ---

{requirements_text}

--- REQUIREMENTS END ---

Additional instructions:
{instructions}

Produce:

1. Analysis summary.
2. Confirmed information.
3. Grounded risk findings.
4. Cause, risk event, and consequence.
5. Evidence and affected requirement IDs.
6. Likelihood, impact, and severity.
7. Mitigation actions and owners.
8. Monitoring indicators when supported.
9. Implementation and testing blockers.
10. Requirement-to-risk relationships.
11. Severity summary.
12. Overall readiness and risk score.
13. Assumptions.
14. Missing information.
15. Recommended next actions.
16. Human-validation items.

Before returning, verify:

- Every risk is supported by supplied evidence.
- Every affected requirement ID exists.
- Risk statements use the required cause-event-consequence format.
- Unsupported probabilities, costs, deadlines, regulations,
  controls, targets, and technologies are not invented.
- Unknown likelihood is used when likelihood cannot be grounded.
- Critical severity is not assigned without material evidence.
- Mitigations do not silently make business or technical decisions.
- Every requirement has one relationship entry.
- Every relationship risk ID exists.
- Summary counts match the generated risks.
- No list contains blank values.

Return structured output only.
""".strip()