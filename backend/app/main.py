import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.nfr import router as nfr_router
from app.api.brd import router as brd_router
from app.api.incident import router as incident_router
from app.api.user_story import router as user_story_router
from app.api.ambiguity import router as ambiguity_router
from app.api.gap_analysis import router as gap_analysis_router
from app.api.requirement_risk import (
    router as requirement_risk_router,
)
from app.api.requirement_classifier import (
    router as requirement_classifier_router,
)
from app.api.requirement_conflict import (
    router as requirement_conflict_router,
)
from app.api.duplicate_requirement import (
    router as duplicate_requirement_router,
)
from app.api.acceptance_criteria import (
    router as acceptance_criteria_router,
)



logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)
app = FastAPI(
    title="Requirement Analysis Copilot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incident_router)
app.include_router(brd_router)
app.include_router(user_story_router)
app.include_router(acceptance_criteria_router)
app.include_router(nfr_router)
app.include_router(ambiguity_router)
app.include_router(gap_analysis_router)
app.include_router(duplicate_requirement_router)
app.include_router(requirement_conflict_router)
app.include_router(requirement_classifier_router)
app.include_router(requirement_risk_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": "Requirement Analysis Copilot",
    }


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Requirement Analysis Copilot Running",
    }