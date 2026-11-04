from typing import NotRequired, TypedDict


class BrdEvaluationCase(TypedDict):
    case_id: str
    brd_title: str
    project_name: str
    business_domain: str
    brd_content: str
    expected_missing_information: list[str]
    minimum_story_count: int
    additional_instructions: NotRequired[str]


EVALUATION_CASES: list[BrdEvaluationCase] = [
    {
        "case_id": "complete_clear_functional_brd",
        "brd_title": "Personal Loan Application",
        "project_name": "Digital Lending",
        "business_domain": "Banking",
        "brd_content": (
            "Customers can start a personal loan application, enter "
            "their contact details and requested amount, and submit it "
            "for review. The portal must show a confirmation reference "
            "after submission. Loan officers can view submitted "
            "applications and record a decision. Applicants can view "
            "the current status of their own application."
        ),
        "expected_missing_information": [],
        "minimum_story_count": 1,
    },
    {
        "case_id": "missing_and_undecided_information",
        "brd_title": "Loan Document Retention",
        "project_name": "Lending Records",
        "business_domain": "Banking",
        "brd_content": (
            "Applicants can upload income documents to their loan "
            "application, and loan officers can view those documents "
            "during assessment. The document retention period is not "
            "specified. The approval threshold and maximum loan amount "
            "are undecided and require a business decision before "
            "automated eligibility behavior can be defined."
        ),
        "expected_missing_information": [
            "document retention period",
            "approval threshold",
            "maximum loan amount",
        ],
        "minimum_story_count": 1,
    },
    {
        "case_id": "multiple_actors_with_distinct_permissions",
        "brd_title": "Role-Based Loan Decisions",
        "project_name": "Loan Operations Portal",
        "business_domain": "Banking",
        "brd_content": (
            "Applicants may create applications and view only their "
            "own application status. Loan officers may review submitted "
            "applications and recommend an approval or rejection. "
            "Supervisors may approve or reject recommendations made by "
            "loan officers. This separates applicant submission, loan "
            "officer review, and supervisor decision permissions."
        ),
        "expected_missing_information": [],
        "minimum_story_count": 1,
    },
    {
        "case_id": "integration_with_unspecified_details",
        "brd_title": "Clearing Partner Transfers",
        "project_name": "Payments Modernization",
        "business_domain": "Banking",
        "brd_content": (
            "When an authorized customer submits a domestic transfer, "
            "the banking platform must send the transfer instruction "
            "to the clearing partner and show the customer the returned "
            "processing status. The API endpoint, authentication "
            "method, message field mapping, and partner error handling "
            "are not specified and must be confirmed with the partner."
        ),
        "expected_missing_information": [
            "API endpoint",
            "authentication method",
            "message field mapping",
            "partner error handling",
        ],
        "minimum_story_count": 1,
        "additional_instructions": (
            "The transfer instruction and returned processing status are "
            "confirmed behaviors. If their traceability is marked Covered, "
            "the notes must state that these behaviors are covered while "
            "identifying the unresolved API endpoint, authentication, "
            "message field mapping, and partner error handling."
        ),
    },
    {
        "case_id": "oversized_workflow_requires_story_splitting",
        "brd_title": "End-to-End Loan Application Workflow",
        "project_name": "Digital Lending",
        "business_domain": "Banking",
        "brd_content": (
            "A customer must be able to create a loan application, enter "
            "personal and financial information, validate required "
            "fields, upload supporting documents, submit the application, "
            "receive a reference number, and view its status. A loan "
            "officer must be able to review the submitted information, "
            "request additional documents, record an assessment, and "
            "recommend a decision. The system must notify the customer "
            "when the status changes."
        ),
        "expected_missing_information": [],
        "minimum_story_count": 2,
    },
]
