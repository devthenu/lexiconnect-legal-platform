# LexiConnect

LexiConnect is a full-stack legal-service platform (FastAPI + React) built as a DevOps/SRE portfolio system. It demonstrates how to run a modern web app on AWS with reproducible infrastructure, containerized delivery, secure runtime controls, and incident-driven operational improvements.

## Why this project matters (DevOps/SRE focus)

- Infrastructure as Code with Terraform (VPC, ALB, ASG, private RDS, IAM, remote state).
- Production-safe network model: ALB edge, backend internal-only, RDS private subnets.
- Secret-free app bootstrapping via SSM Parameter Store and instance role permissions.
- CI/CD pipeline with GitHub Actions building/pushing GHCR images and SSM-based deploy.
- Monitoring and alerting with CloudWatch alarm + SNS notifications.
- Real incident response documented with RCA and corrective/preventative actions.

## Architecture

High-level architecture diagram:
- `docs/diagrams/architecture.png`

Detailed architecture and security-group/subnet tables:
- `docs/ARCHITECTURE.md`

## Live Demo

- Demo URL: `http://<ALB_DNS>`
- Health: `http://<ALB_DNS>/health`
- API health: `http://<ALB_DNS>/api/health`

The demo intentionally uses HTTP because no custom domain is attached for ACM certificate issuance. Production TLS plan: Route53/custom DNS + ACM cert + ALB `:443` + `80 -> 443` redirect + HSTS.

## Quickstart (Local)

```bash
cd deploy
docker compose -f docker-compose.local.yml --env-file .env.example up -d --build
```

Local endpoints:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Mailpit: `http://localhost:8025`

Stop local stack:

```bash
cd deploy
docker compose -f docker-compose.local.yml down
```

## Production Deployment (AWS)

Primary guides:
- `docs/INFRASTRUCTURE.md`
- `docs/RUNBOOK.md`

High-level flow:
- Provision AWS base with Terraform (`infra/envs/dev`).
- Store runtime secrets in SSM Parameter Store (`/lexiconnect/dev/*`).
- Build and publish images to GHCR (`release.yml`).
- Deploy to EC2 instances via SSM command (`deploy.yml`).
- Validate ALB health and app/API reachability.

## CI/CD

- Build workflow: `.github/workflows/release.yml`
- Deploy workflow: `.github/workflows/deploy.yml`

Pipeline behavior:
- On push to `main`, backend and frontend images are built and pushed to GHCR with `latest` and commit SHA tags.
- Deploy workflow triggers on successful build (`workflow_run`) and deploys to EC2 via SSM.
- Deploy uses SHA-pinned tags for deterministic releases and rollback safety.

## Observability

- CloudWatch alarm monitors unhealthy targets (`HealthyHostCount < 1`).
- SNS sends alert notifications for alarm state transitions.
- Evidence:
  - `docs/screenshots/cloudwatch_alarm_in_alarm.png`
  - `docs/screenshots/sns_email_notification.png`
  - `docs/screenshots/cloudwatch_alarm_history.png`

## Incident Response

- RCA: `docs/INCIDENT_RCA_ALB_UNHEALTHY_TARGET.md`

## Repo Structure

```text
.
├── backend/
├── frontend/
├── docs/
│   ├── diagrams/
│   ├── screenshots/
│   ├── ARCHITECTURE.md
│   ├── INFRASTRUCTURE.md
│   ├── RUNBOOK.md
│   ├── SECURITY.md
│   └── INCIDENT_RCA_ALB_UNHEALTHY_TARGET.md
├── deploy/
│   ├── docker-compose.local.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   └── scripts/
├── infra/
│   ├── README.md
│   └── envs/
└── README.md
```

Legacy/non-runtime artifacts are retained under `archive/`.

## License + Disclaimer

This is a student engineering project for educational demonstration.

- Not legal advice.
- Not a production legal platform.
- Demo environment hardening is applied pragmatically with AWS free-tier/credit constraints.
