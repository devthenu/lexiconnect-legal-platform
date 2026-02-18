# LexiConnect Architecture

## System Overview

LexiConnect runs as a containerized web stack on AWS:

- Client traffic enters through ALB (`HTTP:80`)
- ALB routes to EC2 instances managed by ASG
- Frontend container (nginx) serves SPA and proxies `/api` to backend
- Backend (FastAPI) talks to private RDS PostgreSQL

Flow:

`Client -> ALB -> EC2 (frontend nginx) -> backend (FastAPI) -> RDS (private)`

## Network and Subnets

VPC CIDR: `10.0.0.0/16`

| Tier | Subnet Type | AZ | CIDR | Purpose |
|---|---|---|---|---|
| Public | Public | ap-south-1a | 10.0.0.0/24 | ALB + EC2/ASG |
| Public | Public | ap-south-1b | 10.0.1.0/24 | ALB + EC2/ASG |
| Data | Private | ap-south-1a | 10.0.10.0/24 | RDS |
| Data | Private | ap-south-1b | 10.0.11.0/24 | RDS |

Routing notes:
- Public route table uses Internet Gateway.
- Private DB route table has no default internet route.
- NAT Gateway is intentionally not used (cost control for free-tier credits).

## Security Groups

| Security Group | Inbound | Outbound |
|---|---|---|
| `alb-sg` | TCP 80 from `0.0.0.0/0` | All |
| `ec2-sg` | TCP 80 from `alb-sg` | All |
| `rds-sg` | TCP 5432 from `ec2-sg` | All |

## Compute and Runtime

- Launch Template defines AMI, instance type, IAM profile, user data.
- ASG keeps minimum desired capacity of 1 instance for self-healing.
- Instances are tagged `Name=lexiconnect-dev-app` for SSM-based deployments.
- Backend is internal-only (`expose 8000`), not host-published in production compose.

## Deployment Topology

- `deploy/docker-compose.prod.yml` runs frontend + backend.
- Frontend nginx routes:
  - `/` -> SPA
  - `/api/` -> `backend:8000`
  - `/health` -> static `200 ok` for ALB health check

## Diagrams

- Architecture diagram: `diagrams/architecture.png`
- ERD: `diagrams/erd.png`

## Related Docs

- `INFRASTRUCTURE.md`
- `SECURITY.md`
- `RUNBOOK.md`
- `INCIDENT_RCA_ALB_UNHEALTHY_TARGET.md`
