# OpsPilot Terraform

This directory contains the AWS infrastructure for OpsPilot AI.

## Phase 1

The first phase defines:

- one VPC
- two public subnets across two Availability Zones
- two private subnets across two Availability Zones
- one Internet Gateway
- public and private route tables
- one Amazon ECR repository
- no NAT Gateway yet
- no EKS or RDS yet

The private route table intentionally has no default internet route in Phase 1. EKS egress will be designed deliberately in the next infrastructure phase instead of creating a NAT Gateway early.

## Safe workflow

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

Do not run `terraform apply` until the plan has been reviewed.
