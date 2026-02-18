# Infrastructure Guide (AWS + Terraform)

## Scope

This document describes provisioning and operating LexiConnect infrastructure in `ap-south-1` using Terraform.

Provisioned components:
- VPC with public and private subnets
- ALB with target group + listener
- ASG-backed EC2 application layer
- Private RDS PostgreSQL
- IAM role/profile for EC2 + SSM access
- SSM Parameter Store integration via user data

## Terraform Location

- Root module: `../infra/envs/dev`

## Remote State

Terraform state uses S3 + DynamoDB locking:
- Bucket: `lexiconnect-tfstate-1771394861`
- Key: `lexiconnect/dev/terraform.tfstate`
- Region: `ap-south-1`
- Lock table: `lexiconnect-tf-locks`

Reference: `../infra/envs/dev/versions.tf`, `../infra/envs/dev/REMOTE_STATE.md`

## Usage

```bash
cd infra/envs/dev
terraform init -reconfigure
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Destroy when done:

```bash
cd infra/envs/dev
terraform destroy
```

## Required Variables

Set these securely before `plan/apply`:
- `TF_VAR_key_name`
- `TF_VAR_repo_url`
- `TF_VAR_db_password`

## Key Outputs

Current outputs include:
- `alb_dns_name`
- `asg_name`
- `rds_endpoint`

View outputs:

```bash
cd infra/envs/dev
terraform output
```

## Post-Apply Validation

```bash
curl -i http://<alb_dns_name>/health
curl -i http://<alb_dns_name>/api/health
```

Expected:
- `/health` -> `HTTP 200` and `ok`
- `/api/health` -> `HTTP 200` with JSON status

## Cost Notes (Free-tier/Credit Optimized)

- NAT Gateway intentionally omitted.
- Minimal footprint sizing (e.g., `t3.micro`, small RDS class).
- Private RDS with no public exposure.
- Destroy unused stacks to avoid unnecessary spend.

## Related Docs

- `ARCHITECTURE.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `../infra/README.md`
