from fastapi import FastAPI
from app.api.incident import router as incident_router

app = FastAPI(
    title="Requirement Analysis Copilot"
)

app.include_router(incident_router)

@app.get("/")
def root():
    return {
        "message": "Requirement Analysis Copilot Running"
    }