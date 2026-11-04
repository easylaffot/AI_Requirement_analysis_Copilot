from typing import TypedDict

from app.schemas.user_story import UserStoryGenerationRequest


PRIORITY_VALIDATION_INSTRUCTION = (
    "For every inferred priority, include a human-validation item that "
    "explicitly requires Product Owner priority confirmation."
)


class UserStoryEvaluationCase(TypedDict):
    case_id: str
    request: UserStoryGenerationRequest
    confirmed_restrictions: list[str]
    confirmed_boundaries: list[str]
    expected_missing_topics: list[str]
    minimum_story_count: int
    estimable_should_be_false: bool
    priority_is_explicit: bool


EVALUATION_CASES: list[UserStoryEvaluationCase] = [
    {
        "case_id": "simple_atomic_requirement",
        "request": UserStoryGenerationRequest(
            requirement_title="View Rewards Balance",
            requirement_text=(
                "A loyalty program member can view their current rewards "
                "points balance."
            ),
            business_context=(
                "Members use the balance to understand their available "
                "rewards."
            ),
            known_actors=["Loyalty program member"],
            additional_instructions=PRIORITY_VALIDATION_INSTRUCTION,
        ),
        "confirmed_restrictions": [],
        "confirmed_boundaries": [],
        "expected_missing_topics": [],
        "minimum_story_count": 1,
        "estimable_should_be_false": False,
        "priority_is_explicit": False,
    },
    {
        "case_id": "independent_crud_actions",
        "request": UserStoryGenerationRequest(
            requirement_title="Manage Saved Payees",
            requirement_text=(
                "A banking customer can add a saved payee, view saved "
                "payees, modify a saved payee, and delete a saved payee."
            ),
            business_context=(
                "Customers use saved payees to manage recipients for "
                "their banking transfers."
            ),
            known_actors=["Banking customer"],
            additional_instructions=PRIORITY_VALIDATION_INSTRUCTION,
        ),
        "confirmed_restrictions": [],
        "confirmed_boundaries": [],
        "expected_missing_topics": [],
        "minimum_story_count": 4,
        "estimable_should_be_false": False,
        "priority_is_explicit": False,
    },
    {
        "case_id": "actors_with_distinct_permissions",
        "request": UserStoryGenerationRequest(
            requirement_title="Review and Approve Applications",
            requirement_text=(
                "Applicants can submit and view only their own loan "
                "applications. Loan officers can review submitted "
                "applications and recommend a decision. Supervisors can "
                "approve or reject a loan officer recommendation."
            ),
            business_context=(
                "The lending workflow separates applicant, loan officer, "
                "and supervisor responsibilities."
            ),
            known_actors=[
                "Loan applicant",
                "Loan officer",
                "Loan supervisor",
            ],
            additional_instructions=PRIORITY_VALIDATION_INSTRUCTION,
        ),
        "confirmed_restrictions": [
            "Applicants can view only their own loan applications."
        ],
        "confirmed_boundaries": [],
        "expected_missing_topics": [],
        "minimum_story_count": 3,
        "estimable_should_be_false": False,
        "priority_is_explicit": False,
    },
    {
        "case_id": "confirmed_restriction_requires_negative_criteria",
        "request": UserStoryGenerationRequest(
            requirement_title="View Own Account Details",
            requirement_text=(
                "A banking customer can view their account details. A "
                "customer must not view another customer's account details."
            ),
            business_context=(
                "Customers need access to their own account information."
            ),
            known_actors=["Banking customer"],
            business_rules=[
                "A customer may view only accounts belonging to that customer."
            ],
            additional_instructions=PRIORITY_VALIDATION_INSTRUCTION,
        ),
        "confirmed_restrictions": [
            "A customer must not view another customer's account details."
        ],
        "confirmed_boundaries": [],
        "expected_missing_topics": [],
        "minimum_story_count": 1,
        "estimable_should_be_false": False,
        "priority_is_explicit": False,
    },
    {
        "case_id": "incomplete_requirement",
        "request": UserStoryGenerationRequest(
            requirement_title="Process Application Information",
            requirement_text=(
                "The service should collect application information and "
                "make it available for processing. The business value of "
                "this capability has not been determined."
            ),
            business_context=(
                "This requirement is being discussed for a future "
                "business process."
            ),
            known_actors=[],
            business_rules=[],
            additional_instructions=PRIORITY_VALIDATION_INSTRUCTION,
        ),
        "confirmed_restrictions": [],
        "confirmed_boundaries": [],
        "expected_missing_topics": [
            "actor",
            "business value",
            "validation",
        ],
        "minimum_story_count": 1,
        "estimable_should_be_false": True,
        "priority_is_explicit": False,
    },
]
