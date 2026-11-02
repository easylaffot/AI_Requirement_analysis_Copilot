from pydantic import BaseModel
from typing import Optional

class IncidentRequest(BaseModel):
    incident_id: str
    application: str
    severity: str
    description: str
    impact: str
    logs: Optional[str] = None