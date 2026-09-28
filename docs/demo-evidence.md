# OpsPilot AI — Demo Evidence

The following evidence was captured before the temporary AWS demo environment was intentionally deleted.

## Recommended README screenshots

### 1. Dashboard overview

`docs/assets/01-dashboard-overview.png`

Shows:

- system health
- current incident priority
- service topology
- RDS component
- AI incident-analysis panel

### 2. Incident details

`docs/assets/02-incident-details.png`

Shows the selected incident, severity, recent deployment, and evidence.

### 3. AI analysis

`docs/assets/03-ai-analysis.png`

Shows:

- generated summary
- probable cause
- impact
- recommended actions
- rollback consideration
- confidence
- semantic runbook grounding
- model/token/latency evidence

### 4. Recommended runbook

`docs/assets/04-recommended-runbook.png`

Shows the retrieved `HTTP 5xx Error Spike` runbook and troubleshooting steps.

### 5. Jenkins success

`docs/assets/05-jenkins-pipeline.png`

Shows all Jenkins stages completed successfully:

- Python Tests
- SonarQube Analysis
- Docker Build
- Trivy Scan

### 6. GitHub Actions

`docs/assets/06-github-actions.png`

Shows successful OpsPilot CI workflow runs.

### 7. Argo CD + EKS runtime proof

`docs/assets/07-argocd-eks-health.png`

Shows:

```text
opspilot-ai   Synced   Healthy
opspilot-api  1/1      Running
```

### 8. Health endpoint

`docs/assets/08-health-endpoint.png`

Shows:

```json
{"status":"healthy","database":"connected"}
```

### 9. ECR image evidence

`docs/assets/09-ecr-images.png`

Shows the ECR image list captured during the cloud deployment.

### 10. EKS console evidence

`docs/assets/10-eks-compute.png`

Shows the final EKS worker/node-group configuration.

### 11. RDS console evidence

`docs/assets/11-rds-database.png`

Shows the PostgreSQL database instance used by the deployment.

## Screenshots intentionally excluded from the public README

The detailed RDS connectivity/security screenshot is not recommended for public presentation because it exposes unnecessary infrastructure identifiers, endpoint details, and networking information.

## Screen recording

The strongest recording is the end-to-end dashboard incident investigation flow.

A concise silent demo should present:

```text
Dashboard
→ Incident details
→ AI analysis
→ Recommended runbook
→ EKS / Argo CD status
→ Jenkins pipeline
→ GitHub Actions
```

Do not show credentials, database passwords, `.env`, Kubernetes Secret values, or access tokens.
