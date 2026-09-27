from sqlalchemy import select

from backend.database import SessionLocal
from backend.embedding_service import embed_text, runbook_embedding_text
from backend.models import Runbook


def embed_runbooks(force: bool = False):
    with SessionLocal() as db:
        runbooks = db.scalars(select(Runbook).order_by(Runbook.id)).all()

        if not runbooks:
            print("No runbooks found. Run: python -m backend.runbook_seed")
            return

        updated = 0
        skipped = 0

        for runbook in runbooks:
            if runbook.embedding is not None and not force:
                print(f"SKIP  {runbook.id}: {runbook.title}")
                skipped += 1
                continue

            print(f"EMBED {runbook.id}: {runbook.title}")
            text = runbook_embedding_text(runbook)
            runbook.embedding = embed_text(text)
            updated += 1

        db.commit()

        print("")
        print(f"Embedded runbooks: {updated}")
        print(f"Skipped existing: {skipped}")
        print(f"Total runbooks: {len(runbooks)}")


if __name__ == "__main__":
    embed_runbooks()
