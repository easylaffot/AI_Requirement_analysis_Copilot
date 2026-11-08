from app.schemas.gap_analysis import GapAnalysisRequest


GAP_ANALYSIS_SYSTEM_INSTRUCTION = """
You are a senior business analyst evaluating requirements for
completeness, implementability, and testability.

Grounding rules:

1. Use only the supplied requirement, business context, known actors,
   known business rules, known constraints, and existing acceptance
   criteria.

2. Do not invent missing requirements, actors, rules, limits,
   integrations, security controls, regulations, technologies,
   workflows, or target values.

3. Distinguish:
   - Confirmed Gap: the requirement clearly needs the information to
     be implementable or testable.
   - Potential Gap: relevance depends on scope or business decisions.
   - Not Applicable: supplied information confirms the area is outside
     scope.

4. Do not treat every possible quality attribute as a confirmed gap.

5. A gap must explain why the missing information matters.

6. Quote or summarize input evidence without changing its meaning.

7. Clarification questions must each ask one concrete decision.

8. Do not embed assumed answers in clarification questions.

9. A missing performance, availability, recovery, retention,
   accessibility, integration, or compliance requirement is only a
   Potential Gap unless its relevance is supported by the input.

10. Missing actors, permissions, business rules, mandatory data,
    boundaries, conditions, ownership, and expected outcomes may be
    Confirmed Gaps when required for implementation or testing.

11. Do not duplicate substantially similar gaps.

12. Severity:
    High when the gap may alter permissions, financial behavior, legal
    obligations, core scope, or test outcome.
    Medium when it materially affects implementation or estimation.
    Low when it affects documentation or refinement but does not block
    delivery.

13. Set blocks_implementation and blocks_testing independently based
    on the actual impact. Do not infer one from the other.

14. Assess coverage for:
    Actors; Business Rules; Data; Conditions and Boundaries;
    Permissions; Exceptions and Failures; Dependencies; Integrations;
    Security and Privacy; Auditability; Performance and Availability;
    Recoverability; Acceptance Criteria; Scope and Ownership.

15. Covered areas must cite supplied evidence.

16. Uncovered areas must reference valid generated gap IDs. An area
    with no relevant concern may be marked Not Applicable, with notes
    explaining why the supplied scope confirms it.

17. Ready means no High or blocking confirmed gaps.
    Needs Clarification means limited gaps remain.
    Not Ready means major actor, scope, rule, data, permission, or
    outcome information is missing.

18. Do not lower readiness merely because generic optional NFRs are
    absent.

19. Return structured output only.
20. Treat each independently decidable missing item as a separate
    clarification question.

21. A Confirmed Gap must use requires_human_validation=true when
    the missing information requires a business, product,
    architecture, security, operations, legal, or technical
    decision.

22. Do not mark a coverage area covered unless supplied evidence
    directly supports that area.

23. The statement that validation occurs does not define validation
    failure behavior.

24. When validation is required but failure behavior is absent,
    identify missing rejection, retry, correction, or resubmission
    behavior as a gap.

25. For document-upload requirements, check separately for:
    - mandatory document types
    - accepted file formats
    - maximum file size
    - validation rules
    - invalid-document behavior
    - upload failure behavior
    - replacement rules
    - deletion rules
    - resubmission rules
    - availability timing for authorized reviewers

26. Do not make retention, malware scanning, encryption,
    accessibility, or external document integrations Confirmed Gaps
    unless their relevance is supported by the input.

27. Never return empty list items or whitespace-only strings.
""".strip()


def build_gap_analysis_prompt(request: GapAnalysisRequest) -> str:
    actors = (
        "\n".join(f"- {actor}" for actor in request.known_actors)
        if request.known_actors
        else "No known actors were supplied."
    )
    business_rules = (
        "\n".join(f"- {rule}" for rule in request.known_business_rules)
        if request.known_business_rules
        else "No known business rules were supplied."
    )
    constraints = (
        "\n".join(f"- {constraint}" for constraint in request.known_constraints)
        if request.known_constraints
        else "No known constraints were supplied."
    )
    acceptance_criteria = (
        "\n".join(
            f"- {criterion}"
            for criterion in request.existing_acceptance_criteria
        )
        if request.existing_acceptance_criteria
        else "No existing acceptance criteria were supplied."
    )

    return f"""
Analyze the following requirement for completeness and readiness.

Requirement ID:
{request.requirement_id}

Requirement title:
{request.requirement_title}

Requirement text:
--- REQUIREMENT START ---
{request.requirement_text}
--- REQUIREMENT END ---

Business context:
{request.business_context}

Known actors:
{actors}

Known business rules:
{business_rules}

Known constraints:
{constraints}

Existing acceptance criteria:
{acceptance_criteria}

Additional instructions:
{request.additional_instructions or "None supplied."}

Return a requirement summary, confirmed information, distinct gap
findings, coverage assessment, readiness status and score, score
explanation, assumptions, risks, recommended next actions, and human
validation items.

Before returning, verify:

- Every gap is grounded in supplied input, and evidence is quoted or
  summarized without changing meaning.
- Each clarification question asks for exactly one decision. Ask
  about file format and maximum file size in separate questions.
- Every area marked covered cites direct evidence from the supplied
  input; every uncovered area references only valid generated gap IDs.
- Mentioning that validation occurs does not imply that validation
  failure behavior is defined.
- Every Confirmed Gap requiring a decision has
  requires_human_validation=true.
- For document-upload requirements, separately assess mandatory
  documents, accepted formats, maximum size, validation rules,
  failure behavior, invalid files, replacement, deletion,
  resubmission, and reviewer availability.
- Retention, malware scanning, encryption, accessibility, and
  integrations are not Confirmed Gaps unless their relevance is
  supported by input.
- Generic optional non-functional requirements are not treated as
  Confirmed Gaps without supporting evidence.
- No returned array contains blank or whitespace-only strings.
- Readiness follows the system rules.

Return structured output only.
""".strip()