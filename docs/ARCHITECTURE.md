# LexiConnect Architecture (AWS)

## Overview
LexiConnect is deployed on AWS ap-south-1 using a 3-tier layout:
- **Edge / Public**: Application Load Balancer (ALB)
- **App / Compute**: EC2 (Docker Compose: frontend nginx + backend)
- **Data / Private**: RDS PostgreSQL in private subnets

Traffic flow:
Client -> ALB (HTTP:80) -> EC2 (HTTP:80) -> Docker network -> FastAPI (internal) -> RDS (5432)

## Components
### ALB
- Listener: HTTP 80
- Target group: Instance targets on port 80
- Health check:
  - Path: `/health`
  - Matcher: `200`
  - Interval: 30s, timeout 5s
  - Healthy threshold 2, unhealthy 2

### EC2 (t3.micro, Amazon Linux 2023)
- Runs Docker Compose in production mode
- Frontend container serves static React build + acts as reverse proxy:
  - `/` -> React SPA
  - `/api/*` -> FastAPI backend (internal service)
- Backend is **not exposed publicly**; only reachable inside Docker network

### RDS (PostgreSQL)
- Private subnet only
- SG allows inbound 5432 only from EC2 security group

## Network Design
### VPC
CIDR: `10.0.0.0/16`

### Subnets
| Tier | Type | AZ | CIDR | Purpose |
|------|------|----|------|---------|
| Public | Public | ap-south-1a | 10.0.0.0/24 | ALB |
| Public | Public | ap-south-1b | 10.0.1.0/24 | ALB |
| Data | Private | ap-south-1a | 10.0.10.0/24 | RDS |
| Data | Private | ap-south-1b | 10.0.11.0/24 | RDS |

### Routing
- Public route table: `0.0.0.0/0 -> Internet Gateway`
- Private DB route table: **no default internet route**
- NAT Gateway: **not used** (credit-safe)

## Security Groups (Rules)
### alb-sg
Inbound:
- TCP 80 from `0.0.0.0/0`
Outbound:
- All (default)

### app-ec2-sg
Inbound:
- TCP 80 from `alb-sg`
- TCP 22 from *my IP only* (temporary admin)
Outbound:
- All (default)

### rds-sg
Inbound:
- TCP 5432 from `app-ec2-sg`
Outbound:
- Default

## Why these decisions
- **ALB in front**: stable endpoint, health checks, isolates app server exposure
- **Backend not publicly exposed**: API reachable only via nginx reverse proxy
- **RDS private**: data tier not internet reachable
- **No NAT Gateway**: avoids ongoing hourly charges while maintaining core best practices

## Evidence
Screenshots:
- [docs/screenshots/alb-targets-healthy.png](screenshots/alb-targets-healthy.png)
- [docs/screenshots/alb-listener-80.png](screenshots/alb-listener-80.png)
- [docs/screenshots/alb-dns.png](screenshots/alb-dns.png)
