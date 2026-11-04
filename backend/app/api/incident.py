from fastapi import APIRouter, HTTPException, status

from app.schemas.analysis import IncidentAnalysisResponse
from app.schemas.incident import IncidentRequest
from app.services.incident_service import (
    IncidentAnalysisError,
    IncidentService,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Analyzer"],
)


@router.post(
    "/analyze",
    response_model=IncidentAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_incident(
    request: IncidentRequest,
) -> IncidentAnalysisResponse:
    service = IncidentService()

    try:
        return await service.analyze(request)

    except IncidentAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    finally:
        await service.close()