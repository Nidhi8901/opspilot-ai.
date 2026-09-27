from sqlalchemy import select

from backend.database import Base, SessionLocal, engine
from backend.models import Runbook


RUNBOOKS = [
    {
        "title": "Database Connection Exhaustion",
        "problem_type": "RDS PostgreSQL connection exhaustion",
        "description": "Use when database connections, pool usage, or database-related request failures increase.",
        "keywords": [
            "database connections",
            "connection pool",
            "postgresql",
            "rds",
            "timeout",
            "db connection",
        ],
        "content": """1. Check current PostgreSQL/RDS connection utilization.
2. Inspect application connection-pool size and timeout settings.
3. Identify long-running or idle transactions.
4. Confirm application code closes or returns connections correctly.
5. Compare the issue timeline with recent deployments.
6. Consider rollback only if evidence indicates the new release introduced connection leakage or pool misconfiguration.
7. Scale database capacity only after validating that the problem is genuine demand rather than leaked connections.""",
    },
    {
        "title": "Kubernetes Pod Restart Investigation",
        "problem_type": "Kubernetes pod restart CrashLoopBackOff",
        "description": "Use when pods restart repeatedly, fail health checks, or enter CrashLoopBackOff.",
        "keywords": [
            "pod restart",
            "restarted",
            "crashloop",
            "crashloopbackoff",
            "liveness",
            "readiness",
            "oom",
        ],
        "content": """1. Inspect pod status, restart count, and recent Kubernetes events.
2. Review container logs from the current and previous container instance.
3. Check readiness and liveness probe failures.
4. Compare memory usage against resource limits and look for OOMKilled events.
5. Check whether a recent image or configuration change preceded the restart.
6. Roll back only when the failure correlates with a recent deployment and the previous version is known healthy.""",
    },
    {
        "title": "HTTP 5xx Error Spike",
        "problem_type": "HTTP 500 502 503 5xx error spike",
        "description": "Use when application or load-balancer 5xx responses increase.",
        "keywords": [
            "http 500",
            "500 errors",
            "5xx",
            "502",
            "503",
            "error rate",
        ],
        "content": """1. Confirm which service and endpoint are producing 5xx responses.
2. Compare application logs with load-balancer and dependency errors.
3. Check CPU, memory, database, and downstream-service saturation.
4. Inspect recent deployments and configuration changes.
5. Validate health checks and target/pod availability.
6. If the errors began directly after a release, compare with the previous version before considering rollback.""",
    },
    {
        "title": "High CPU and Latency",
        "problem_type": "High CPU latency saturation",
        "description": "Use when CPU and response latency rise together.",
        "keywords": [
            "cpu",
            "latency",
            "slow",
            "response time",
            "saturation",
        ],
        "content": """1. Confirm CPU saturation duration and affected service replicas.
2. Correlate latency, request volume, and error rate.
3. Inspect expensive requests, loops, or downstream calls.
4. Check whether autoscaling has triggered and whether resource requests/limits are appropriate.
5. Compare the start of the issue with recent releases.
6. Scale temporarily only if traffic is legitimate and the application is otherwise healthy.""",
    },
    {
        "title": "Deployment Regression and Rollback",
        "problem_type": "Deployment regression rollback",
        "description": "Use when an incident begins soon after a deployment.",
        "keywords": [
            "deployment",
            "deployed",
            "release",
            "version",
            "rollback",
        ],
        "content": """1. Record the deployment version and exact deployment time.
2. Compare the incident start time with the release.
3. Review code/configuration changes introduced in the new version.
4. Verify whether the previous release was healthy under similar traffic.
5. Gather enough evidence to distinguish correlation from causation.
6. Roll back when the new release is strongly correlated with the incident and rollback risk is lower than continued impact.""",
    },
]


def seed_runbooks():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_titles = set(
            db.scalars(select(Runbook.title)).all()
        )

        created = 0
        for item in RUNBOOKS:
            if item["title"] in existing_titles:
                continue
            db.add(Runbook(**item))
            created += 1

        db.commit()
        print(f"Runbooks created: {created}")
        print(f"Runbooks already present: {len(RUNBOOKS) - created}")


if __name__ == "__main__":
    seed_runbooks()
