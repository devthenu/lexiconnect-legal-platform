# Security Notes

## Runtime Exposure

- ALB is the public entrypoint.
- EC2 app instances accept traffic from ALB on port 80.
- Backend container is internal-only in production compose (no host port mapping).
- RDS is in private subnets and restricted to app security group on `5432`.

## Access Controls

- EC2 administration is via AWS SSM Session Manager (no static host credentials required).
- Instance role is scoped to required SSM parameter reads.
- App authorization uses JWT + RBAC controls.

## Secrets Handling

- Runtime config/secrets are sourced from SSM Parameter Store (`/lexiconnect/dev/*`).
- No production secrets are committed in repository files.

## HTTP Demo Limitation

Current demo uses HTTP for ALB endpoint because ACM cannot issue a browser-trusted certificate for raw ALB DNS names without a domain.

## Production TLS Plan

- Use custom domain (Route53 or delegated DNS).
- Request/validate ACM certificate.
- Attach cert to ALB listener `:443`.
- Redirect `:80 -> :443` and enable HSTS.

## Monitoring and Response

- CloudWatch alarm on ALB healthy targets.
- SNS notification fanout for alerting.
- RCA tracked in `INCIDENT_RCA_ALB_UNHEALTHY_TARGET.md`.
