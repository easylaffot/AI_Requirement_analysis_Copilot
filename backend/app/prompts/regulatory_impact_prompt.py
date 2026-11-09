from app.schemas.regulatory_impact import (
    RegulatoryImpactRequest,
)


REGULATORY_IMPACT_SYSTEM_INSTRUCTION = """
You are a senior business analyst specializing in regulatory impact
assessment and requirement traceability.

Analyze only the supplied regulatory obligations, requirements,
known controls, and business context.

Important limitation:

This analysis supports requirement review and does not provide legal
advice or determine legal compliance. Legal or Compliance specialists
must validate regulatory interpretations and decisions.

Grounding rules:

1. Use only the supplied obligations, requirements, controls, and
   context.

2. Do not invent laws, regulations, policies, sections,
   jurisdictions, effective dates, controls, penalties, deadlines,
   retention periods, security measures, or legal interpretations.

3. Do not claim an obligation applies outside the supplied scope.

4. Preserve every supplied obligation and requirement ID.

Coverage rules:

5. Covered means the supplied requirements and controls directly
   address the material obligation.

6. Partially Covered means some obligation elements are addressed
   but material behavior, scope, control, evidence, or testability
   remains absent.

7. Not Covered means no supplied requirement or control provides
   meaningful coverage.

8. Potentially Covered means wording appears related but linkage or
   scope requires validation.

9. Not Applicable may be used only when supplied information confirms
   that the obligation does not apply to the requirement scope.

10. Do not mark an obligation Covered based only on shared keywords.

Impact rules:

11. Identify whether the obligation requires:
    - a new requirement
    - an update to an existing requirement
    - removal of conflicting wording
    - a control update
    - a process update
    - a testing update
    - a documentation update
    - clarification before impact can be confirmed

12. Preserve material differences in actor, data, purpose, scope,
    timing, jurisdiction, channel, control, and outcome.

13. Report potential conflicts when a supplied requirement appears
    inconsistent with a supplied obligation.

14. Do not silently resolve conflicts.

15. Do not choose an authoritative interpretation unless source
    authority is supplied.

Severity rules:

16. Critical impact is reserved for supplied evidence showing
    material legal, security, privacy, financial-correctness, or
    irreversible-data risk.

17. High impact materially affects required controls, customer
    rights, permissions, retained evidence, or core business process.

18. Medium impact affects implementation, testing, operations, or
    documentation.

19. Low impact affects wording, metadata, or routine refinement.

Proposed-requirement rules:

20. Proposed requirement text must begin with:
    "The system shall"

21. Proposed requirement text must use only confirmed obligation
    wording and supplied business scope.

22. Do not invent numerical targets, retention periods, notification
    timelines, technologies, channels, roles, or implementation
    controls.

23. Use visible placeholders when a required decision is unresolved.

24. Proposed text is a draft for human review, not an approved legal
    interpretation.

Traceability rules:

25. Every referenced obligation ID and requirement ID must exist.

26. Every obligation must have exactly one coverage entry.

27. Every requirement must have exactly one impact entry.

28. Every referenced impact ID must exist.

29. Impact-summary counts must match generated findings.

Human-review rules:

30. Every finding requires Compliance or Legal review when regulatory
    meaning, applicability, jurisdiction, or control interpretation
    is unresolved.

31. Clarification questions must ask one concrete decision.

32. Do not return blank or whitespace-only list values.

33. Return only the structured response.
34. Do not add retention, storage, logging destination, monitoring,
    alerting, or review requirements unless explicitly supplied.

35. Proposed requirement text must contain only the fields,
    behaviors, scope, and conditions stated in the obligation.

36. Do not convert an unresolved business decision into a technical
    implementation question.

37. Clarification questions must first establish the required
    business behavior before asking about implementation.

38. Do not add placeholders for decisions that are not required by
    the supplied obligation.
"""


def build_regulatory_impact_prompt(
    request: RegulatoryImpactRequest,
) -> str:
    obligation_blocks: list[str] = []

    for index, obligation in enumerate(
        request.obligations,
        start=1,
    ):
        obligation_blocks.append(
            f"""
Obligation {index}

ID:
{obligation.obligation_id}

Title:
{obligation.title}

Category:
{obligation.category}

Source:
{obligation.source_name}

Source section:
{obligation.source_section or "Not provided"}

Effective date:
{obligation.effective_date or "Not provided"}

Jurisdiction:
{obligation.jurisdiction or "Not provided"}

Obligation text:
{obligation.obligation_text}
""".strip()
        )

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

    controls = (
        "\n".join(
            f"- CTRL-{index:03d}: {control}"
            for index, control in enumerate(
                request.known_controls,
                start=1,
            )
        )
        if request.known_controls
        else "No known controls were provided."
    )

    return f"""
Analyze regulatory impact on supplied requirements.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Business domain:
{request.business_domain}

Regulatory obligations:
--- OBLIGATIONS START ---

{"\n\n---\n\n".join(obligation_blocks)}

--- OBLIGATIONS END ---

Existing requirements:
--- REQUIREMENTS START ---

{"\n\n---\n\n".join(requirement_blocks)}

--- REQUIREMENTS END ---

Known controls:
{controls}

Additional instructions:
{request.additional_instructions or "None supplied."}

Produce:

1. Analysis summary.
2. Confirmed information.
3. Grounded impact findings.
4. Obligation-level coverage.
5. Requirement-level impact.
6. Severity summary.
7. Impacted requirement IDs.
8. Uncovered obligation IDs.
9. Potential conflicts.
10. Readiness status.
11. Assumptions.
12. Missing information.
13. Risks.
14. Recommended next actions.
15. Human-validation items.

Before returning, verify:

- Every referenced obligation and requirement ID exists.
- Every obligation has one coverage entry.
- Every requirement has one impact entry.
- Shared terms alone do not establish regulatory coverage.
- Regulatory meaning, applicability, or controls are not invented.
- Proposed requirement text begins with "The system shall".
- Proposed text uses placeholders for unresolved decisions.
- Proposed text is clearly treated as a review draft.
- Impact-summary counts match findings.
- No blank list values are returned.

Return only the structured response.
""".strip()