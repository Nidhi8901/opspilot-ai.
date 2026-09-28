# OpsPilot AI — CI/CD and GitOps

## 1. Responsibility split

OpsPilot uses three complementary automation layers:

```text
GitHub Actions → repository validation
Jenkins        → deeper CI / code quality / image security
Argo CD        → Kubernetes desired-state reconciliation
```

## 2. GitHub Actions

The GitHub Actions workflow runs on pushes and pull requests targeting `main`.

The validated workflow:

1. checks out the repository
2. configures Python 3.13
3. installs backend dependencies
4. starts PostgreSQL + pgvector
5. enables the vector extension
6. creates the application schema
7. starts FastAPI
8. runs smoke tests with pytest
9. validates that the Docker image builds

The tests intentionally do not require a live Bedrock generation call.

## 3. Jenkins pipeline

The final Jenkins pipeline completed successfully.

Stages:

```text
Checkout SCM
Checkout
Python Tests
SonarQube Analysis
Docker Build
Trivy Scan
Post Actions
```

### Python Tests

The Jenkins test stage creates an isolated Docker network and a temporary `pgvector/pgvector:pg16` container.

It then:

1. waits for PostgreSQL readiness
2. enables `vector`
3. creates the SQLAlchemy schema
4. starts FastAPI on port 8000
5. waits for `/health`
6. runs `pytest -q`
7. removes the temporary database/network

This made the test environment reproducible and independent of the developer's local database.

### SonarQube

Jenkins connects to the local SonarQube container through the shared Docker network:

```text
http://opspilot-sonarqube:9000
```

The scanner analyzes:

- `backend`
- `frontend`
- `tests`

### Docker build

Jenkins builds:

```text
opspilot-ai:jenkins-${BUILD_NUMBER}
```

### Trivy

Trivy scans the Docker image for `HIGH` and `CRITICAL` vulnerabilities.

The final portfolio pipeline uses:

```text
--exit-code 0
```

Therefore Trivy is used as a reporting control, not as a blocking release gate. This distinction is intentional in the documentation.

## 4. Amazon ECR

The application image was built and pushed to Amazon ECR during the cloud deployment workflow.

The EKS deployment used an immutable tagged image from:

```text
577638393088.dkr.ecr.ap-south-1.amazonaws.com/opspilot-ai
```

The final Jenkins pipeline did **not** automatically push to ECR. This repository documents that accurately rather than claiming an automation step that was not validated.

## 5. GitOps

Kubernetes desired state is stored in:

```text
https://github.com/Nidhi8901/opspilot-gitops
```

The repository contains the application deployment and Kustomize configuration.

Argo CD Core watches that repository and reconciles the EKS workload.

Validated status:

```text
opspilot-ai   Synced   Healthy
```

## 6. Why Jenkins does not run kubectl apply

The project follows the GitOps separation of responsibilities:

```text
CI builds/tests/scans
        ↓
Git stores desired state
        ↓
Argo CD reconciles the cluster
```

This avoids making Jenkins the direct owner of cluster state.

## 7. Current status

The live AWS resources were deleted after the completed demo to control cost. The application repository, GitOps repository, CI definitions, manifests, screenshots, and recordings remain as implementation evidence.
