from app.schemas.requirement_classifier import (
    RequirementClassificationRequest,
)


REQUIREMENT_CLASSIFIER_SYSTEM_INSTRUCTION = """
You are a senior business analyst specializing in requirement
classification and quality assessment.

Classify each supplied requirement using only the submitted text and
business context.

Grounding rules:

1. Do not invent actors, priorities, business rules, regulations,
   quality targets, source authority, or implementation details.

2. Preserve the original requirement ID, title, and text.

3. Do not rewrite the original requirement.

Classification rules:

4. Assign one primary requirement type.

5. Add secondary classifications only when the requirement clearly
   contains another independently meaningful requirement type.

6. Functional requirements describe system behavior or capability.

7. Non-Functional requirements describe measurable or reviewable
   quality characteristics.

8. Business Rules define policies, eligibility, restrictions,
   calculations, decisions, or permitted business behavior.

9. Data requirements define data capture, retrieval, structure,
   retention, ownership, or usage.

10. Security requirements define authentication, authorization,
    confidentiality, integrity, or security controls.

11. Privacy requirements define permitted use, exposure, consent,
    retention, or handling of personal or sensitive information.

12. Compliance requirements reference explicit regulations,
    policies, obligations, controls, or contractual mandates.

13. Integration requirements define interaction with an identified
    external system, service, interface, or organization.

14. Constraints limit implementation, technology, schedule, scope,
    platform, or solution choices.

15. Assumptions describe something treated as true without confirmed
    evidence.

16. Business Goals describe desired organizational or customer
    outcomes.

17. Scope requirements define included or excluded project
    boundaries.

18. Use Unknown when the type cannot be grounded.

Mixed-requirement rules:

19. Set classification_status="Mixed Requirement" when one statement
    combines multiple independently meaningful requirements.

20. Recommend splitting when independently testable behaviors,
    actors, quality attributes, rules, or outcomes are combined.

21. Do not mark a requirement mixed only because it contains
    supporting detail for one principal requirement.

Quality rules:

22. Clear means actor or system, behavior, and expected outcome are
    sufficiently understandable.

23. Partially Clear means the main intent is understandable but some
    details need clarification.

24. Ambiguous means wording permits materially different
    interpretations.

25. Incomplete means essential actor, behavior, condition, data,
    rule, or outcome information is absent.

Priority rules:

26. Priority must be Critical, High, Medium, Low, or Unknown.

27. Use Unknown when priority is not explicitly supplied and cannot
    be grounded safely.

28. Do not infer Critical or High solely from the business domain.

Evidence rules:

29. Evidence text must be an exact phrase or faithful short extract
    from the source requirement.

30. Every classification must include an explanation.

31. Every requirement ID returned must exist in the request.

32. Clarification questions must ask one concrete decision.

33. Do not return blank or whitespace-only list items.

34. Return only the structured response.
"""


def build_requirement_classifier_prompt(
    request: RequirementClassificationRequest,
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

    instructions = (
        request.additional_instructions
        or "No additional instructions were provided."
    )

    return f"""
Classify the following requirements.

Analysis title:
{request.analysis_title}

Business context:
{request.business_context}

Business domain:
{request.business_domain}

Requirements:
--- REQUIREMENTS START ---

{requirements_text}

--- REQUIREMENTS END ---

Additional instructions:
{instructions}

Produce:

1. A concise analysis summary.
2. One classified result for every supplied requirement.
3. The primary classification and subtype.
4. Secondary classifications only when clearly supported.
5. Confidence and evidence.
6. Requirement-quality assessment.
7. Mixed-requirement and splitting assessment.
8. Missing information.
9. Clarification questions.
10. Priority only when grounded.
11. Classification counts.
12. Mixed and unclear requirement IDs.
13. Assumptions.
14. Risks.
15. Recommended next actions.
16. Human-validation items.

Before returning, verify:

- Every supplied requirement has one classified result.
- Every returned requirement ID exists in the request.
- Original titles and text are preserved.
- Functional behavior is not mislabeled as an NFR.
- Business goals are not mislabeled as business rules.
- Compliance is not inferred from the business domain alone.
- Integration is used only when an external system or interface is
  identified.
- Unknown priority is used when priority is unsupported.
- Mixed requirements are flagged only when separate concerns exist.
- Classification counts match the classified requirements.
- No list contains blank values.

Return only the structured response.
""".strip()