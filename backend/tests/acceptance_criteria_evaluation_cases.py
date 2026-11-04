from typing import TypedDict

from app.schemas.acceptance_criteria import AcceptanceCriteriaRequest


class BoundaryExpectation(TypedDict):
    kind: str
    value: str
    neighbor: str


class AcceptanceCriteriaEvaluationCase(TypedDict):
    case_id: str
    request: AcceptanceCriteriaRequest
    confirmed_boundaries: list[BoundaryExpectation]
    confirmed_restrictions: bool
    expected_missing_information: list[str]
    unsupported_failure_behavior: bool
    accepted_for_processing_only: bool
    contradictory_precondition_phrases: list[str]


EVALUATION_CASES: list[AcceptanceCriteriaEvaluationCase] = [
    {
        "case_id": "simple_positive_processing_behavior",
        "request": AcceptanceCriteriaRequest(
            story_id="PAY-AC-101",
            story_title="Submit a transfer request",
            user_story=(
                "As a customer, I want to submit a transfer request so "
                "that it can be accepted for processing."
            ),
            business_context=(
                "Submitting a transfer starts the bank's processing "
                "workflow; submission does not confirm completion."
            ),
            existing_acceptance_criteria=[
                "Given a valid transfer request, when it is submitted, "
                "then the request is accepted for processing."
            ],
        ),
        "confirmed_boundaries": [],
        "confirmed_restrictions": False,
        "expected_missing_information": [],
        "unsupported_failure_behavior": False,
        "accepted_for_processing_only": True,
        "contradictory_precondition_phrases": [],
    },
    {
        "case_id": "restriction_requires_negative_behavior",
        "request": AcceptanceCriteriaRequest(
            story_id="ACCT-AC-202",
            story_title="View account details",
            user_story=(
                "As a customer, I want to view my account details so that "
                "I can understand my account activity."
            ),
            business_context=(
                "Customers may view their own accounts but must not view "
                "another customer's account details."
            ),
            business_rules=[
                "A customer may view only accounts belonging to that customer."
            ],
        ),
        "confirmed_boundaries": [],
        "confirmed_restrictions": True,
        "expected_missing_information": [],
        "unsupported_failure_behavior": False,
        "accepted_for_processing_only": False,
        "contradictory_precondition_phrases": [
            "customer is authorized to view another customer's account",
            "all customers are authorized",
        ],
    },
    {
        "case_id": "minimum_and_maximum_boundaries",
        "request": AcceptanceCriteriaRequest(
            story_id="TRF-AC-303",
            story_title="Enter a transfer amount",
            user_story=(
                "As a customer, I want to enter a transfer amount so that "
                "I can request a transfer within the permitted limits."
            ),
            business_context=(
                "A transfer amount is valid only when it is within the "
                "confirmed minimum and maximum."
            ),
            known_constraints=[
                "The minimum transfer amount is $10.",
                "The confirmed transfer amount immediately below the minimum is $9.",
                "The maximum transfer amount is $500.",
                "The confirmed transfer amount immediately above the maximum is $501.",
            ],
            additional_instructions=(
                "Use only the explicitly supplied transfer amount values "
                "9, 10, 500, and 501. Do not use decimal alternatives such "
                "as 9.99 or 500.01 or any other amount."
            ),
        ),
        "confirmed_boundaries": [
            {"kind": "minimum", "value": "10", "neighbor": "9"},
            {"kind": "maximum", "value": "500", "neighbor": "501"},
        ],
        "confirmed_restrictions": False,
        "expected_missing_information": [],
        "unsupported_failure_behavior": False,
        "accepted_for_processing_only": False,
        "contradictory_precondition_phrases": [],
    },
    {
        "case_id": "actor_based_permission_rule",
        "request": AcceptanceCriteriaRequest(
            story_id="LOAN-AC-404",
            story_title="Approve a loan application",
            user_story=(
                "As a loan supervisor, I want to approve a reviewed loan "
                "application so that I can authorize its next workflow step."
            ),
            business_context=(
                "Only a loan supervisor may approve an application. "
                "Applicants and loan officers may not approve applications."
            ),
            business_rules=[
                "Only loan supervisors may approve reviewed applications."
            ],
        ),
        "confirmed_boundaries": [],
        "confirmed_restrictions": True,
        "expected_missing_information": [],
        "unsupported_failure_behavior": False,
        "accepted_for_processing_only": False,
        "contradictory_precondition_phrases": [
            "all users are authorized",
            "loan officer is authorized to approve",
            "applicant is authorized to approve",
        ],
    },
    {
        "case_id": "incomplete_story_missing_failure_behavior",
        "request": AcceptanceCriteriaRequest(
            story_id="CLAIM-AC-505",
            story_title="Submit a claim",
            user_story=(
                "As a member, I want to submit a claim so that I can "
                "request reimbursement."
            ),
            business_context=(
                "The member submits a claim for review. Failure behavior "
                "and retry behavior have not been defined."
            ),
            existing_acceptance_criteria=[
                "Given a complete claim, when a member submits it, then the claim is received for review.",
                "Given claim details are complete, when the member submits the claim, then the claim is received for review.",
            ],
        ),
        "confirmed_boundaries": [],
        "confirmed_restrictions": False,
        "expected_missing_information": [
            "failure behavior",
            "retry behavior",
        ],
        "unsupported_failure_behavior": True,
        "accepted_for_processing_only": False,
        "contradictory_precondition_phrases": [],
    },
]
