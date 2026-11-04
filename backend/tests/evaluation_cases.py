from app.schemas.incident import IncidentRequest


EVALUATION_CASES = [
    {
        "case_id": "clear_log_evidence",
        "incident": IncidentRequest(
            incident_id="EVAL-001",
            application="Payment Gateway",
            severity="High",
            description=(
                "Card payments are failing after payment "
                "authorization is completed."
            ),
            impact=(
                "Six percent of card-payment attempts are failing."
            ),
            logs=(
                "PaymentCaptureService returned HTTP 504 while "
                "waiting for the capture operation."
            ),
        ),
        "forbidden_claims": [
            "database failure",
            "network outage",
            "cache failure",
        ],
    },
    {
        "case_id": "insufficient_root_cause",
        "incident": IncidentRequest(
            incident_id="EVAL-002",
            application="Customer Portal",
            severity="Medium",
            description=(
                "Some customers see an unexpected error when "
                "opening their profile."
            ),
            impact=(
                "The number of affected customers is unknown."
            ),
            logs=(
                "An unexpected application error occurred. "
                "No additional diagnostic details are available."
            ),
        ),
        "forbidden_claims": [
            "database",
            "network",
            "cache",
            "deployment caused",
        ],
    },
    {
        "case_id": "missing_business_impact",
        "incident": IncidentRequest(
            incident_id="EVAL-003",
            application="Loan Application Portal",
            severity="Medium",
            description=(
                "Applicants occasionally receive an error when "
                "uploading income documents."
            ),
            impact=(
                "Business impact information was not provided."
            ),
            logs=(
                "Document upload failed with an unspecified error."
            ),
        ),
        "forbidden_claims": [
            "financial loss",
            "customer churn",
            "database failure",
        ],
    },
    {
        "case_id": "unaffected_secondary_channel",
        "incident": IncidentRequest(
            incident_id="EVAL-004",
            application="Internet Banking",
            severity="High",
            description=(
                "Some web customers cannot log in after valid "
                "credential and OTP submission. Mobile Banking "
                "customers are not affected."
            ),
            impact=(
                "Twelve percent of web login attempts are failing."
            ),
            logs=(
                "AuthenticationService session creation failed "
                "with HTTP status 500."
            ),
        ),
        "forbidden_claims": [
            "mobile application failure",
            "database failure",
        ],
    },
    {
        "case_id": "critical_full_service_outage",
        "incident": IncidentRequest(
            incident_id="EVAL-005",
            application="Digital Banking Platform",
            severity="Critical",
            description=(
                "Internet Banking and Mobile Banking are "
                "unavailable to all customers."
            ),
            impact=(
                "All digital customers are unable to log in, "
                "view balances, or initiate payments."
            ),
            logs=(
                "Health checks for the authentication endpoint "
                "are failing with HTTP status 503."
            ),
        ),
        "forbidden_claims": [
            "database failure",
            "cyberattack",
            "network outage",
        ],
    },
]