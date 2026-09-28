# OpsPilot AI — Troubleshooting and Lessons Learned

This project included multiple real deployment/debugging situations. These are useful because they demonstrate how the final system was actually made operational.

## 1. AWS CLI authentication appeared broken

### Symptom

AWS commands failed even after browser-based profile authentication.

### Cause

Old AWS credential environment variables were overriding the valid profile.

### Fix

```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN
```

Then commands used the authenticated `opspilot` profile.

### Lesson

AWS credential provider precedence matters. Environment variables can override profile-based authentication.

---

## 2. Original EKS worker size failed

### Symptom

The initial managed node-group configuration could not launch with the expected instance type/account eligibility.

### Fix

The node-group configuration was adjusted.

A `t3.micro` node then proved too constrained for Kubernetes system pods plus the application.

The final demo used a `t3.small`.

### Lesson

Instance cost is not the only constraint. Kubernetes workload capacity also depends on CPU, memory, and networking/pod limits.

---

## 3. EKS pod scheduling failed with "Too many pods"

### Cause

The smaller node reached its pod allocation limit after Kubernetes system components consumed available slots.

### Fix

The workload moved to the final `t3.small` worker.

### Lesson

EKS instance selection must consider maximum pod density, not only compute size.

---

## 4. Fresh RDS database did not contain the application database/schema

### Fix

The project database was created and pgvector enabled:

```sql
CREATE DATABASE opspilot;
CREATE EXTENSION IF NOT EXISTS vector;
```

### Lesson

Database server availability does not mean the application database/schema already exists.

---

## 5. Migration baseline limitation

### Symptom

Applying the existing Alembic history against the completely fresh RDS database failed because an early migration expected a table that did not yet exist.

### Operational workaround

For the portfolio deployment:

1. SQLAlchemy metadata created the fresh schema.
2. Alembic was stamped to the current head.

### Lesson

A migration chain should be tested from an empty database. A baseline that assumes prior state is technical debt.

This limitation is intentionally documented rather than hidden.

---

## 6. Argo CD application stayed Unknown

### Error

```text
Application referencing project default which does not exist
```

### Fix

An Argo CD `AppProject` named `default` was created.

### Result

Argo CD moved to:

```text
Synced
Progressing
```

and later `Healthy`.

---

## 7. Argo CD rollout created two containers in one pod

### Symptom

The new pod showed:

```text
1/2 CrashLoopBackOff
```

and Uvicorn reported:

```text
address already in use
```

### Cause

The existing Deployment container was named `opspilot-ai` while the GitOps manifest used `opspilot-api`.

The server-side merge retained both container entries, so two Uvicorn processes attempted to bind to port 8000 inside the same pod.

### Fix

The GitOps manifest container name was changed to match the existing container name.

### Result

The deployment returned to `1/1 Running` and Argo CD reached `Synced / Healthy`.

### Lesson

Kubernetes list merge identity matters. Naming consistency is important in declarative updates.

---

## 8. Jenkins smoke tests returned Connection refused

### Symptom

All HTTP smoke tests failed with:

```text
httpx.ConnectError: [Errno 111] Connection refused
```

### Cause

The first Jenkins pipeline ran pytest before starting FastAPI.

### Fix

The test stage was changed to:

1. create temporary pgvector PostgreSQL
2. create schema
3. start Uvicorn
4. wait for `/health`
5. run pytest
6. clean up

### Lesson

Integration tests must reproduce the services they depend on.

---

## 9. Jenkins module path was wrong

### Error

```text
ModuleNotFoundError: No module named 'backend.app'
```

### Cause

The actual application entrypoint is:

```text
backend.main:app
```

### Fix

The Jenkinsfile was corrected to import:

```text
backend.database
backend.models
backend.main
```

### Result

The final Jenkins pipeline completed successfully.

---

## 10. Safe AWS teardown

The project used several dependent AWS resources, so deletion order mattered.

The final cleanup removed:

- EKS/node groups
- RDS
- NAT Gateway and EIP
- ECR
- project CloudWatch log groups
- project IAM/Pod Identity resources
- project subnets and route tables
- internet gateway
- custom OpsPilot VPC

A final blocker was two non-main route tables. After deleting them, the custom VPC deleted successfully.

The account's real default VPC and default security group were verified before and after cleanup.

### Lesson

Cloud teardown is a dependency-management problem. Always identify the exact VPC/resource IDs and protect default/shared resources.
