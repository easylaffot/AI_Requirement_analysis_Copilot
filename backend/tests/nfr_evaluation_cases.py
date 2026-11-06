from typing import TypedDict

from app.schemas.nfr import NfrRecommendationRequest


class NfrEvaluationCase(TypedDict, total=False):
    case_id: str
    request: NfrRecommendationRequest
    expected_relevant_categories: list[str]
    expected_irrelevant_categories: list[str]


EVALUATION_CASES: list[NfrEvaluationCase] = [
    {
        "case_id": "high_criticality_transaction_missing_targets",
        "request": NfrRecommendationRequest(
            requirement_id="PAY-NFR-101",
            requirement_title="Submit a payment transaction",
            requirement_text=(
                "The payment service accepts a customer transaction for "
                "processing and records its processing state."
            ),
            business_context=(
                "Payment processing is a high-criticality business "
                "capability. Transactions affect account balances, and an "
                "interruption may leave processing state uncertain. No "
                "approved performance, availability, RTO, or RPO target "
                "has been supplied."
            ),
            business_domain="Payments",
            data_sensitivity="Unknown",
            criticality="High",
        ),
        "expected_relevant_categories": [
            "Performance",
            "Availability",
            "Recoverability",
        ],
        "expected_irrelevant_categories": [
            "Accessibility",
            "Auditability",
            "Compatibility",
            "Compliance",
            "Maintainability",
            "Observability",
            "Privacy",
            "Reliability",
            "Scalability",
            "Security",
            "Usability",
        ],
    },
    {
        "case_id": "restricted_data_security_privacy_review",
        "request": NfrRecommendationRequest(
            requirement_id="CLAIM-NFR-202",
            requirement_title="Review restricted claim details",
            requirement_text=(
                "The claims service presents restricted claimant and claim "
                "details to staff for claim review."
            ),
            business_context=(
                "Claim details are classified as Restricted. The applicable "
                "security and privacy controls and handling policy have not "
                "yet been supplied."
            ),
            business_domain="Insurance",
            data_sensitivity="Restricted",
            criticality="Unknown",
        ),
        "expected_relevant_categories": ["Security", "Privacy"],
        "expected_irrelevant_categories": [
            "Accessibility",
            "Availability",
            "Auditability",
            "Compatibility",
            "Compliance",
            "Maintainability",
            "Observability",
            "Performance",
            "Recoverability",
            "Reliability",
            "Scalability",
            "Usability",
        ],
    },
    {
        "case_id": "existing_nfr_duplicate_avoidance",
        "request": NfrRecommendationRequest(
            requirement_id="FIN-NFR-303",
            requirement_title="Prepare invoice reconciliation",
            requirement_text=(
                "The finance service prepares an invoice reconciliation "
                "statement from confirmed invoice approvals."
            ),
            business_context=(
                "Finance staff use the statement to reconcile invoice "
                "approvals during the daily close. Its performance and "
                "availability matter to that process, and an interrupted "
                "statement must be reproducible from confirmed approvals. "
                "Existing audit requirements already define the traceability "
                "needed for that review. No approved performance, availability, "
                "or recovery target has been supplied."
            ),
            business_domain="Finance",
            data_sensitivity="Internal",
            criticality="Medium",
            existing_nfrs=[
                "The system shall provide a traceable audit record for each confirmed invoice approval.",
            ],
        ),
        "expected_relevant_categories": [
            "Auditability",
            "Performance",
            "Availability",
            "Recoverability",
        ],
        "expected_irrelevant_categories": [
            "Accessibility",
            "Compatibility",
            "Compliance",
            "Maintainability",
            "Observability",
            "Privacy",
            "Reliability",
            "Scalability",
            "Security",
            "Usability",
        ],
    },
    {
        "case_id": "explicit_compatibility_constraint",
        "request": NfrRecommendationRequest(
            requirement_id="INT-NFR-404",
            requirement_title="Exchange partner claim status",
            requirement_text=(
                "The claims service exchanges claim status with the "
                "partner claims interface."
            ),
            business_context=(
                "The partner interface is required for claims operations. "
                "No specific protocol, vendor, or technical standard was "
                "provided. Compatibility with the partner interface is the "
                "only quality requirement supplied; no separate performance, "
                "availability, or recovery requirement is present."
            ),
            business_domain="Insurance",
            data_sensitivity="Internal",
            criticality="Medium",
            known_constraints=[
                "The claim status exchange must remain compatible with the supplied partner claims interface."
            ],
            existing_nfrs=[
                "The system shall provide a traceable audit record for each confirmed invoice approval.",
                "The system shall provide a traceable audit record for each confirmed invoice approval.",
            ],
        ),
        "expected_relevant_categories": ["Compatibility"],
        "expected_irrelevant_categories": [
            "Accessibility",
            "Availability",
            "Auditability",
            "Compliance",
            "Maintainability",
            "Observability",
            "Performance",
            "Privacy",
            "Recoverability",
            "Reliability",
            "Scalability",
            "Security",
            "Usability",
        ],
    },
    {
        "case_id": "minimal_requirement_irrelevant_categories",
        "request": NfrRecommendationRequest(
            requirement_id="OPS-NFR-505",
            requirement_title="View current case status",
            requirement_text=(
                "The staff portal shows the current case status without "
                "undue delay."
            ),
            business_context=(
                "Staff use the status view during ordinary case work. No "
                "performance target, criticality, sensitive data, special "
                "accessibility need, supported platform, or compliance "
                "policy has been specified."
            ),
            business_domain="Operations",
            data_sensitivity="Unknown",
            criticality="Unknown",
        ),
        "expected_relevant_categories": ["Performance"],
        "expected_irrelevant_categories": [
            "Accessibility",
            "Availability",
            "Auditability",
            "Compatibility",
            "Compliance",
            "Maintainability",
            "Observability",
            "Privacy",
            "Recoverability",
            "Reliability",
            "Scalability",
            "Security",
            "Usability",
        ],
    },
]
