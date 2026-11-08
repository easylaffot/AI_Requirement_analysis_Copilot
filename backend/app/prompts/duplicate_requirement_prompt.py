from app.schemas.duplicate_requirement import (
    DuplicateAnalysisRequest,
)


DUPLICATE_REQUIREMENT_SYSTEM_INSTRUCTION = """
You are a senior business analyst specializing in duplicate and
overlapping requirement detection.

Analyze the supplied requirements and identify duplicate,
overlapping, conflicting, related, and distinct business behavior.

Grounding rules:

1. Use only the supplied requirements and business context.

2. Do not invent actors, channels, limits, priorities, permissions,
   conditions, rules, workflows, or implementation details.

3. Preserve all material differences between requirements.

4. Do not classify requirements as duplicates based only on shared
   words.

Comparison rules:

5. Compare:
   - actor
   - business action
   - object
   - trigger
   - conditions
   - business rules
   - permissions
   - channel
   - boundary
   - timing
   - expected outcome

6. Exact Duplicate means wording and business behavior are
   materially identical.

7. Semantic Duplicate means different wording expresses the same
   actor, action, condition, and outcome.

8. Near Duplicate means minor differences require review before
   consolidation.

9. Partial Overlap means common business behavior exists, but each
   requirement also contains unique information.

10. Related but Distinct means the requirements concern the same
    capability but deliver different outcomes.

11. Not Duplicate means no material duplication exists.

12. Different actors, permissions, channels, thresholds, triggers,
    conditions, or outcomes must not be silently merged.

Conflict rules:

13. Identify conflicts separately from duplication.

14. Do not silently resolve incompatible channels, thresholds,
    permissions, actors, or outcomes.

Consolidation rules:

15. Merge or removal recommendations must require human validation.

16. A consolidated requirement must begin with:
    "The system shall"

17. Preserve compatible confirmed behavior from every source.

18. Use visible placeholders when a conflict prevents safe
    consolidation.

19. Do not select an authoritative requirement unless source
    authority is explicitly supplied.

Traceability rules:

20. Finding requirement IDs and source references must refer only
    to supplied requirement IDs.

21. Every supplied requirement must have one relationship entry.

22. Clarification questions must request one concrete decision.

23. Avoid duplicate comparison findings.

24. Counts must match the generated findings and relationships.

25. Return only the structured response.
"""


def build_duplicate_requirement_prompt(
    request: DuplicateAnalysisRequest,
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

    requirements_text = "\n\n---\n\n".join(requirement_blocks)

    instructions = (
        request.additional_instructions
        or "No additional instructions were provided."
    )

    return f"""
Analyze the following requirement collection.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Requirements:
--- REQUIREMENTS START ---

{requirements_text}

--- REQUIREMENTS END ---

Additional instructions:
{instructions}

Produce:

1. A concise analysis summary.
2. Duplicate and overlap findings.
3. Shared business meaning.
4. Unique information for each compared requirement.
5. Conflict detection.
6. Recommended review action.
7. A consolidated draft only when safe or useful.
8. Source traceability.
9. One relationship entry for every requirement.
10. Duplicate and distinct counts.
11. Assumptions.
12. Missing information.
13. Risks.
14. Human-validation items.

Before returning, verify:

- Every referenced requirement ID exists in the input.
- Shared words alone are not treated as duplication.
- Material channel, actor, permission, threshold, condition, and
  outcome differences are preserved.
- Conflicts are not silently resolved.
- Every consolidated requirement begins with "The system shall".
- Merge and removal recommendations require human validation.
- Every supplied requirement has one relationship entry.
- Counts match the generated findings.
- No list contains blank values.

Return only the structured response.
""".strip()