# OpsPilot AI Interview Notes

## Why did you build this project?

I wanted a project directly related to DevOps work rather than another generic CRUD application. During incidents, engineers often correlate deployment history, service health, metrics, logs, and runbooks manually. OpsPilot centralizes the incident context and uses AI to create an initial grounded analysis while keeping production decisions with the engineer.

## Why FastAPI?

FastAPI is lightweight, Python-based, provides automatic API documentation, integrates cleanly with SQLAlchemy and AWS SDKs, and is well suited for a small service-oriented backend.

## Why PostgreSQL?

The application needs durable relational storage for services, incidents, deployments, runbooks, and AI analysis. PostgreSQL also supports pgvector, allowing relational and vector workloads to stay in one database for this project.

## Why pgvector?

Runbooks should be retrieved by meaning, not only exact keywords. pgvector lets OpsPilot store embeddings and perform cosine similarity search directly in PostgreSQL.

## Why Titan embeddings?

Titan converts incident and runbook text into vectors so semantically similar operational problems can be matched even when they use different wording.

## Why Nova Lite?

Nova Lite provides the generative analysis layer. It receives incident evidence plus the retrieved runbook and returns structured troubleshooting guidance.

## Why RAG?

RAG makes the AI response more grounded and auditable. The UI can show which runbook was retrieved instead of presenting recommendations as unsupported model output.

## Why cache incident embeddings?

Embedding an unchanged incident on every retrieval would create unnecessary network calls, latency, and cost. OpsPilot stores the incident embedding and reuses it.

## Why Alembic?

SQLAlchemy `create_all()` can create missing tables but does not safely manage changes to existing schemas. Alembic creates versioned, repeatable database migrations.

## Why Docker?

Docker makes the API runtime reproducible and isolates application dependencies. Docker Compose also lets the API and PostgreSQL + pgvector environment run together locally.

## Why both GitHub Actions and Jenkins?

The planned responsibility split avoids tool duplication:

- GitHub Actions: fast PR validation
- Jenkins: heavier CI, security scans, image build, ECR push, GitOps update
- Argo CD: deployment reconciliation into EKS

## Why doesn't Jenkins deploy directly to Kubernetes?

The target architecture uses GitOps. Jenkins produces and promotes artifacts and updates desired state in Git. Argo CD continuously reconciles the cluster with that desired state.

## Why doesn't the AI automatically fix incidents?

AI output can be incorrect or incomplete. OpsPilot is intentionally advisory. Engineers review evidence and recommendations before performing operational changes.

## What was a real problem you encountered while building it?

Database model changes required schema migrations. An added field existed in the SQLAlchemy model but not in the existing PostgreSQL table, which caused a runtime query failure. I introduced Alembic so future schema changes are version-controlled and repeatable.

Another issue occurred when a new Docker Compose file created a different PostgreSQL volume. The application appeared empty even though the original data still existed. I inspected Docker volumes, verified the original data, and configured Compose to use the correct external volume without deleting data.
