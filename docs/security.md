# OpsPilot AI — Security Decisions

## 1. AWS credentials

The EKS workload did not use hard-coded AWS access keys.

Amazon Bedrock access was provided through:

```text
Kubernetes ServiceAccount
        ↓
EKS Pod Identity
        ↓
IAM workload role
        ↓
Bedrock Runtime
```

The in-pod identity was validated before Bedrock testing.

## 2. Database access

Amazon RDS PostgreSQL was placed in the project's private network path.

The database security group allowed PostgreSQL access from the EKS security path instead of opening the database broadly to the internet.

The application used a Kubernetes Secret for `DATABASE_URL`.

The Secret was not stored in the GitOps repository.

## 3. Repository secret hygiene

The project excludes sensitive local material such as:

- `.env`
- AWS configuration
- private keys
- local infrastructure state artifacts if present
- local backups
- generated logs

The documentation never requires users to commit credentials.

## 4. AI safety boundary

OpsPilot is advisory.

The AI cannot directly:

- restart pods
- execute shell commands
- change AWS resources
- roll back a deployment
- modify database infrastructure

The system prompt also instructs the model to avoid inventing unsupported evidence.

## 5. Container security

Trivy scans the built image for high and critical vulnerabilities.

For the final portfolio pipeline the scan is reporting-only (`--exit-code 0`), so the repository does not describe it as a blocking enforcement gate.

## 6. Code quality

SonarQube performs static analysis through Jenkins.

The project uses SonarQube as a code-quality control, while GitHub Actions and pytest provide executable CI validation.

## 7. Kubernetes controls

The EKS deployment uses:

- readiness probe
- liveness probe
- CPU requests/limits
- memory requests/limits
- dedicated service account
- non-public ClusterIP service

## 8. Public exposure

A public application load balancer was intentionally not added for the portfolio demo.

Access was provided through:

```text
kubectl port-forward
```

This reduced the exposed surface and avoided an additional continuously billed AWS resource.

## 9. Secret-management limitation

Kubernetes Secrets are not equivalent to a dedicated enterprise secrets-management platform.

For a production enterprise implementation, a managed secret store and automated secret rotation would be appropriate.

## 10. Cost/security cleanup

After final screenshots and recordings were captured, the live cloud resources were deleted.

The cleanup removed the project's EKS, RDS, NAT Gateway/EIP, ECR, CloudWatch log groups, Pod Identity/IAM project resources, project networking, and custom VPC while preserving the account's AWS default VPC and default security group.
