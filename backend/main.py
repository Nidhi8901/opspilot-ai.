from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from backend.bedrock_service import analyze_incident_with_bedrock
from backend.database import Base, engine, get_db
from backend.models import AIAnalysis, Deployment, Incident, Runbook, Service
from backend.retrieval import retrieve_runbook_match
from backend.schemas import (
    AIAnalysisResponse,
    DeploymentResponse,
    IncidentCreate,
    IncidentResponse,
    RunbookResponse,
    ServiceResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpsPilot AI API",
    description="Backend API for the OpsPilot AI incident response platform",
    version="0.7.0",
)


@app.get("/")
def home():
    return {
        "application": "OpsPilot AI",
        "status": "running",
        "database": "PostgreSQL",
        "ai_provider": "Amazon Bedrock",
        "retrieval": "Runbook grounded retrieval v1",
        "dashboard": "/dashboard",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }


@app.get("/services", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    return db.scalars(select(Service).order_by(Service.id)).all()


@app.get("/incidents", response_model=list[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    return db.scalars(
        select(Incident).order_by(Incident.detected_at.desc())
    ).all()


@app.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    service = db.get(Service, payload.service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail=f"Service {payload.service_id} not found",
        )

    current_max_id = db.scalar(select(func.max(Incident.id))) or 1000
    incident = Incident(
        id=current_max_id + 1,
        service_id=payload.service_id,
        title=payload.title,
        severity=payload.severity,
        status=payload.status,
        detected_at=datetime.utcnow(),
        summary=payload.summary,
        evidence=payload.evidence,
        recent_deployment=payload.recent_deployment,
    )

    db.add(incident)

    if payload.severity in {"high", "critical"}:
        service.status = "degraded"

    db.commit()
    db.refresh(incident)

    return incident


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@app.get("/runbooks", response_model=list[RunbookResponse])
def get_runbooks(db: Session = Depends(get_db)):
    return db.scalars(select(Runbook).order_by(Runbook.title)).all()


@app.get(
    "/incidents/{incident_id}/recommended-runbook",
    response_model=RunbookResponse,
)
def get_recommended_runbook(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    match = retrieve_runbook_match(db, incident)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="No matching runbook was found",
        )

    return match.runbook


@app.post(
    "/incidents/{incident_id}/analyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    service = db.get(Service, incident.service_id)

    if service is None:
        raise HTTPException(
            status_code=500,
            detail="Incident is linked to a missing service",
        )

    match = retrieve_runbook_match(db, incident)
    runbook = match.runbook if match else None

    try:
        result = analyze_incident_with_bedrock(
            incident=incident,
            service=service,
            runbook=runbook,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Bedrock analysis failed: {exc}",
        ) from exc

    analysis = AIAnalysis(
        incident_id=incident.id,
        runbook_id=result["runbook_id"],
        runbook_title=result["runbook_title"],
        runbook_similarity=match.similarity if match else None,
        model_id=result["model_id"],
        summary=result["summary"],
        probable_cause=result["probable_cause"],
        impact=result["impact"],
        recommended_actions=result["recommended_actions"],
        rollback_consideration=result["rollback_consideration"],
        confidence_percent=result["confidence_percent"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        total_tokens=result["total_tokens"],
        latency_ms=result["latency_ms"],
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@app.get(
    "/incidents/{incident_id}/analysis/latest",
    response_model=AIAnalysisResponse,
)
def get_latest_analysis(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    analysis = db.scalar(
        select(AIAnalysis)
        .where(AIAnalysis.incident_id == incident_id)
        .order_by(AIAnalysis.created_at.desc())
        .limit(1)
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No AI analysis exists for this incident yet",
        )

    return analysis


@app.get("/deployments", response_model=list[DeploymentResponse])
def get_deployments(db: Session = Depends(get_db)):
    return db.scalars(
        select(Deployment).order_by(Deployment.deployed_at.desc())
    ).all()


frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount(
    "/dashboard",
    StaticFiles(directory=str(frontend_dir), html=True),
    name="dashboard",
)
