from pydantic import BaseModel

from app.schemas.analysis import IncidentAnalysisResponse


class EvaluationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class EvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    checks: list[EvaluationCheck]
    analysis: IncidentAnalysisResponse