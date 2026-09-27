from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.embedding_service import embed_text
from backend.models import Incident, Runbook


MINIMUM_SIMILARITY = 0.20


@dataclass
class RunbookMatch:
    runbook: Runbook
    similarity: float


def incident_embedding_text(incident: Incident) -> str:
    evidence = "\n".join(f"- {item}" for item in (incident.evidence or []))
    return (
        f"Incident title: {incident.title}\n"
        f"Severity: {incident.severity}\n"
        f"Status: {incident.status}\n"
        f"Summary: {incident.summary}\n"
        f"Evidence:\n{evidence or '- No evidence recorded'}\n"
        f"Recent deployment: {incident.recent_deployment or 'None'}"
    )


def get_or_create_incident_embedding(
    db: Session,
    incident: Incident,
) -> list[float]:
    if incident.embedding is not None:
        return list(incident.embedding)

    embedding = embed_text(incident_embedding_text(incident))
    incident.embedding = embedding

    # Persist immediately so repeated semantic searches do not call Titan again.
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return embedding


def retrieve_runbook_match(
    db: Session,
    incident: Incident,
) -> RunbookMatch | None:
    query_embedding = get_or_create_incident_embedding(db, incident)

    distance = Runbook.embedding.cosine_distance(query_embedding)

    row = db.execute(
        select(
            Runbook,
            distance.label("cosine_distance"),
        )
        .where(Runbook.embedding.is_not(None))
        .order_by(distance)
        .limit(1)
    ).first()

    if row is None:
        return None

    runbook, cosine_distance = row
    similarity = 1.0 - float(cosine_distance)

    if similarity < MINIMUM_SIMILARITY:
        return None

    return RunbookMatch(
        runbook=runbook,
        similarity=similarity,
    )


def retrieve_runbook_for_incident(
    db: Session,
    incident: Incident,
) -> Runbook | None:
    match = retrieve_runbook_match(db, incident)
    return match.runbook if match else None
