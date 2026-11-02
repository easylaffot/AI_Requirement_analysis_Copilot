from pydantic import BaseModel
from typing import List

class IncidentAnalysisResponse(BaseModel):
    incident_summary: str
    business_impact: str
    root_cause_hypothesis: str
    functional_requirements: List[str]
    user_story: str
    acceptance_criteria: List[str]
    risks: List[str]
    priority: str