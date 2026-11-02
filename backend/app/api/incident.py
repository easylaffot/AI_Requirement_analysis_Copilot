from fastapi import APIRouter

from app.schemas.incident import IncidentRequest
from app.schemas.analysis import IncidentAnalysisResponse

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Analyzer"]
)

@router.post(
    "/analyze",
    response_model=IncidentAnalysisResponse
)
async def analyze_incident(
    request: IncidentRequest
):
    return IncidentAnalysisResponse(
        incident_summary=f"Incident detected in {request.application}",
        business_impact=request.impact,
        root_cause_hypothesis="Possible timeout issue",
        functional_requirements=[
            "System shall process transactions successfully",
            "System shall handle timeout conditions gracefully"
        ],
        user_story=(
            "As a banking customer, "
            "I want transactions processed successfully "
            "so that I can complete my transfer."
        ),
        acceptance_criteria=[
            "Given a valid transaction, when submitted, then it should succeed",
            "Given a timeout condition, appropriate error message should be shown"
        ],
        risks=[
            "Customer dissatisfaction",
            "Revenue impact"
        ],
        priority=request.severity
    )