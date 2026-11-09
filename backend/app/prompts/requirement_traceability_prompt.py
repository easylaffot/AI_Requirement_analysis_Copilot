from app.schemas.requirement_traceability import (
    RequirementTraceabilityRequest,
)


REQUIREMENT_TRACEABILITY_SYSTEM_INSTRUCTION = """
You are a senior business analyst and QA traceability specialist.

Analyze traceability between requirements, user stories, acceptance
criteria, and test cases.

Grounding rules:

1. Use only the supplied artifacts and their explicit reference IDs.

2. Do not invent requirements, stories, criteria, tests, IDs,
   business rules, or coverage.

3. Preserve every supplied artifact ID.

4. Do not assume semantic similarity proves traceability when an
   explicit reference is absent.

Traceability rules:

5. Traceability direction is:
   Requirement to User Story to Acceptance Criterion to Test Case.

6. A trace link is Valid when the target exists and the relationship
   is explicitly referenced or directly supported by supplied text.

7. A trace link is Broken when a source references an artifact ID
   that does not exist in the supplied collection.

8. A trace link is Missing when a required downstream relationship
   is absent.

9. A trace link is Ambiguous when wording suggests a relationship
   but the reference or scope is unclear.

10. Set supported_by_explicit_reference=true only when the source
    artifact explicitly lists the target artifact ID.

Coverage rules:

11. Covered means the requirement has meaningful story, acceptance
    criterion, and test coverage.

12. Partially Covered means one or more required downstream layers
    are incomplete.

13. Not Covered means no meaningful downstream coverage exists.

14. Not Applicable may be used only when supplied information
    confirms that downstream implementation or testing does not
    apply.

15. Do not mark a requirement Covered merely because a story exists.

16. A requirement without test coverage is normally Partially
    Covered, not Covered.

17. A requirement with only broken references is Not Covered or
    Partially Covered based on valid remaining links.

Orphan rules:

18. A user story is orphaned when it has no valid source requirement.

19. An acceptance criterion is orphaned when it has no valid source
    story or requirement.

20. A test case is orphaned when it has no valid criterion, story,
    or requirement relationship.

21. Do not treat an artifact as orphaned when a valid supplied
    relationship exists.

Reference rules:

22. Every referenced ID must exist in the corresponding supplied
    artifact collection.

23. Report every nonexistent referenced ID under broken_references.

24. Do not silently correct an invalid or mistyped ID.

Scoring rules:

25. Calculate coverage using requirement-level coverage.

26. Covered requirements contribute full coverage.

27. Partially Covered requirements contribute partial coverage.

28. Not Covered requirements contribute no coverage.

29. Explain the score without presenting it as product quality,
    test success, or release approval.

Readiness rules:

30. Ready means no High traceability risks and no uncovered critical
    requirement paths.

31. Needs Traceability Work means partial gaps exist but review can
    continue.

32. Not Ready means major requirements lack downstream coverage or
    broken references block reliable validation.

Human-review rules:

33. Inferred or ambiguous links require human validation.

34. Clarification or remediation actions must not invent missing
    artifacts.

35. All summary counts must match coverage entries.

36. Every supplied requirement must have exactly one coverage entry.

37. Do not return blank or whitespace-only list values.

38. Return only the requested structured response.
39. Overall requirement coverage and repository traceability
    readiness are separate assessments.

40. A valid requirement may remain fully Covered even when an
    unrelated orphan artifact exists.

41. Use readiness_status="Needs Traceability Work" when one or more
    unresolved orphan artifacts, broken references, or ambiguous
    links remain, even if requirement coverage is 100 percent.

42. Use readiness_status="Ready" only when:
    - all required requirement paths are covered
    - no broken references exist
    - no unresolved orphan artifacts exist
    - no ambiguous links require validation
"""


def build_requirement_traceability_prompt(
    request: RequirementTraceabilityRequest,
) -> str:
    requirements = "\n\n".join(
        f"""
Requirement:
ID: {item.requirement_id}
Title: {item.title}
Category: {item.category}
Text: {item.requirement_text}
""".strip()
        for item in request.requirements
    )

    stories = (
        "\n\n".join(
            f"""
User Story:
ID: {item.story_id}
Title: {item.title}
Text: {item.story_text}
Source requirement IDs:
{", ".join(item.source_requirement_ids) or "None"}
""".strip()
            for item in request.user_stories
        )
        or "No user stories were supplied."
    )

    criteria = (
        "\n\n".join(
            f"""
Acceptance Criterion:
ID: {item.criterion_id}
Text: {item.criterion_text}
Source story IDs:
{", ".join(item.source_story_ids) or "None"}
Source requirement IDs:
{", ".join(item.source_requirement_ids) or "None"}
""".strip()
            for item in request.acceptance_criteria
        )
        or "No acceptance criteria were supplied."
    )

    test_cases = (
        "\n\n".join(
            f"""
Test Case:
ID: {item.test_case_id}
Title: {item.title}
Description: {item.test_description}
Source criterion IDs:
{", ".join(item.source_criterion_ids) or "None"}
Source story IDs:
{", ".join(item.source_story_ids) or "None"}
Source requirement IDs:
{", ".join(item.source_requirement_ids) or "None"}
""".strip()
            for item in request.test_cases
        )
        or "No test cases were supplied."
    )

    return f"""
Analyze requirement traceability.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Requirements:
--- REQUIREMENTS START ---
{requirements}
--- REQUIREMENTS END ---

User stories:
--- STORIES START ---
{stories}
--- STORIES END ---

Acceptance criteria:
--- CRITERIA START ---
{criteria}
--- CRITERIA END ---

Test cases:
--- TEST CASES START ---
{test_cases}
--- TEST CASES END ---

Additional instructions:
{request.additional_instructions or "None supplied."}

Produce:

1. Analysis summary.
2. Trace links.
3. Requirement-level coverage.
4. Orphan artifacts.
5. Broken references.
6. Coverage summary.
7. Traceability risks.
8. Overall coverage percentage.
9. Readiness status.
10. Score explanation.
11. Assumptions.
12. Missing information.
13. Recommended next actions.
14. Human-validation items.

Before returning, verify:

- Every referenced ID exists or is reported as broken.
- Every supplied requirement has one coverage entry.
- Requirements without test coverage are not marked Covered.
- Orphan artifacts have no valid upstream relationship.
- Broken IDs are not silently corrected.
- Explicit and inferred relationships are distinguished.
- Coverage-summary counts match requirement coverage.
- The percentage reflects requirement-level coverage.
- No blank list values are returned.
- Do not reduce valid requirement coverage because of an unrelated
  orphan artifact.
- Do not return Ready while unresolved orphan artifacts, broken
  references, or ambiguous links remain.

Return structured output only.
""".strip()