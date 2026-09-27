import sys

from backend.database import SessionLocal
from backend.models import Incident
from backend.retrieval import retrieve_runbook_match


def main():
    incident_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1001

    with SessionLocal() as db:
        incident = db.get(Incident, incident_id)

        if incident is None:
            raise SystemExit(f"Incident {incident_id} was not found.")

        print(f"Incident: INC-{incident.id} - {incident.title}")
        print("Generating incident embedding with Amazon Titan...")
        match = retrieve_runbook_match(db, incident)

        if match is None:
            print("No runbook passed the semantic similarity threshold.")
            return

        print("")
        print("Semantic retrieval successful.")
        print(f"Runbook: {match.runbook.title}")
        print(f"Problem type: {match.runbook.problem_type}")
        print(f"Cosine similarity: {match.similarity:.4f}")


if __name__ == "__main__":
    main()
