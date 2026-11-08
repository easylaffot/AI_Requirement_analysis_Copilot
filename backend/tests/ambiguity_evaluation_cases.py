from typing import Literal, TypedDict

from app.schemas.ambiguity import AmbiguityAnalysisRequest


class AmbiguityEvaluationCase(TypedDict):
    case_id: str
    request: AmbiguityAnalysisRequest
    expected_missing_information: tuple[str, ...]
    expected_defined_terms: tuple[str, ...]
    expected_status: Literal["Clear", "Not Ready", "Not Clear"]
    minimum_score: int
    expected_optional_modality: bool
    expect_notification_channel: bool
    unresolved_rewrite_concepts: tuple[str, ...]
    requires_cannot_rewrite_safely: bool


EVALUATION_CASES: list[AmbiguityEvaluationCase] = [
    {
        "case_id": "clear_measurable_payment_limit",
        "request": AmbiguityAnalysisRequest(
            requirement_id="AMB-UC6-001",
            requirement_title="Reject payments above the confirmed limit",
            requirement_text=(
                "The system shall reject any outgoing payment request with "
                "an amount greater than 500 USD and record the reason "
                "'amount limit exceeded' on that request."
            ),
            business_context=(
                "The requirement applies to outgoing payment requests. "
                "All outgoing payment amounts are denominated in USD. "
                "The amount limit is evaluated before a request is "
                "submitted for processing."
            ),
            known_business_rules=[
                "A rejected payment request is not submitted for processing."
            ],
        ),
        "expected_missing_information": (),
        "expected_defined_terms": (),
        "expected_status": "Clear",
        "minimum_score": 85,
        "expected_optional_modality": False,
        "expect_notification_channel": False,
        "unresolved_rewrite_concepts": (),
        "requires_cannot_rewrite_safely": False,
    },
    {
        "case_id": "vague_and_subjective_claim_processing",
        "request": AmbiguityAnalysisRequest(
            requirement_id="AMB-UC6-002",
            requirement_title="Process eligible claims and show status",
            requirement_text=(
                "The system should process eligible claims quickly and "
                "provide a user-friendly status."
            ),
            business_context=(
                "Claims are handled by the claims service. The requirement "
                "does not define a processing-time target or criteria for "
                "a user-friendly status. The requirement does not request "
                "sending a notification or message."
            ),
            known_business_rules=[
                "A claim is eligible only when the claimant's identity has "
                "been verified and the claim is active."
            ],
            additional_instructions=(
                "Do not propose any actor, notification channel, value, "
                "duration, or implementation detail that is absent from "
                "the supplied requirement and context."
            ),
        ),
        "expected_missing_information": (
            "processing time",
        ),
        "expected_defined_terms": ("eligible",),
        "expected_status": "Not Clear",
        "minimum_score": 0,
        "expected_optional_modality": True,
        "expect_notification_channel": False,
        "unresolved_rewrite_concepts": (),
        "requires_cannot_rewrite_safely": False,
    },
    {
        "case_id": "undefined_actor_and_object",
        "request": AmbiguityAnalysisRequest(
            requirement_id="AMB-UC6-003",
            requirement_title="Update an unspecified item",
            requirement_text="They should update it when needed.",
            business_context=(
                "No actor, target object, or expected update outcome has "
                "been supplied."
            ),
            additional_instructions=(
                "Do not infer a specific actor, target object, trigger, "
                "expected outcome, permission, or technical implementation "
                "detail that is absent from the supplied information. Do not "
                "add unrelated security or implementation risks. Do not "
                "introduce databases, APIs, servers, or access-control "
                "policies."
            ),
        ),
        "expected_missing_information": ("actor", "object", "expected outcome"),
        "expected_defined_terms": (),
        "expected_status": "Not Ready",
        "minimum_score": 0,
        "expected_optional_modality": True,
        "expect_notification_channel": False,
        "unresolved_rewrite_concepts": ("actor", "object", "expected outcome"),
        "requires_cannot_rewrite_safely": True,
    },
    {
        "case_id": "missing_timing_amount_boundary_and_channel",
        "request": AmbiguityAnalysisRequest(
            requirement_id="AMB-UC6-004",
            requirement_title="Process and notify about a transfer",
            requirement_text=(
                "The system shall process each transfer within an "
                "acceptable time and notify the requester when the amount "
                "is high."
            ),
            business_context=(
                "Transfer processing is required. No approved timing target, "
                "amount threshold, or notification channel has been supplied."
            ),
            additional_instructions=(
                "Do not propose any actor, notification channel, value, "
                "duration, or implementation detail that is absent from "
                "the supplied requirement and context. Ask generically which "
                "channel is intended; do not name or list channel options. "
                "Do not mention storage or database implementation; focus "
                "only on requirement behavior."
            ),
        ),
        "expected_missing_information": (
            "processing time",
            "amount threshold",
            "notification channel",
        ),
        "expected_defined_terms": (),
        "expected_status": "Not Clear",
        "minimum_score": 0,
        "expected_optional_modality": False,
        "expect_notification_channel": True,
        "unresolved_rewrite_concepts": (),
        "requires_cannot_rewrite_safely": False,
    },
    {
        "case_id": "compound_optional_order_update_and_notification",
        "request": AmbiguityAnalysisRequest(
            requirement_id="AMB-UC6-005",
            requirement_title="Validate and update an order",
            requirement_text=(
                "The system may validate the order and update the account, "
                "and notify the customer as appropriate."
            ),
            business_context=(
                "No mandatory behavior, validation criteria, account-update "
                "result, notification condition, or notification channel "
                "has been defined."
            ),
            additional_instructions=(
                "Do not propose any actor, notification channel, value, "
                "duration, or implementation detail that is absent from "
                "the supplied requirement and context. Ask generically which "
                "channel is intended; do not name or list channel options. "
                "Do not add unrelated security or implementation risks. "
                "Do not invent account fields; use an expected-outcome "
                "placeholder for the unresolved account update. Ask "
                "separately whether order validation and account updating "
                "are mandatory; do not combine those decisions. In the "
                "analysis, refer to an undefined channel only as "
                "'notification channel'; never name a specific channel. "
                "The word 'email' must not appear in the response."
            ),
        ),
        "expected_missing_information": (
            "expected outcome",
            "notification channel",
            "notification condition",
        ),
        "expected_defined_terms": (),
        "expected_status": "Not Clear",
        "minimum_score": 0,
        "expected_optional_modality": True,
        "expect_notification_channel": True,
        "unresolved_rewrite_concepts": ("expected outcome",),
        "requires_cannot_rewrite_safely": False,
    },
]
