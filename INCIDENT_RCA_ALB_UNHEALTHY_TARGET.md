# Incident RCA: ALB Target Unhealthy (LexiConnect Dev)

**Date:** 2026-02-18  
**Environment:** dev  
**Service:** LexiConnect (frontend + backend)  
**Severity:** SEV-2 (Service partially unavailable)  
**Status:** Resolved

## Summary

The LexiConnect dev environment experienced downtime where the Application Load Balancer (ALB) reported the target as unhealthy and users received `502 Bad Gateway` errors. The issue was caused by the backend container being stopped, resulting in NGINX failing to proxy requests to the backend health endpoint. CloudWatch alarm for `HealthyHostCount < 1` triggered and SNS notification was received.

## Impact

- ALB returned `502 Bad Gateway` for `/api/health`
- Backend API became unreachable
- Frontend could not load API-dependent features
- Duration of outage: ~10 minutes
- Only dev environment affected

## Detection

The incident was detected through:

1. CloudWatch Alarm `lexiconnect-dev-alb-unhealthy-target`
2. Alarm transitioned from OK -> ALARM
3. SNS email notification received
4. Manual verification showed `502 Bad Gateway` on backend health endpoint

![TODO: CloudWatch Alarm In Alarm](screenshots/cloudwatch_alarm_in_alarm.png)
![TODO: SNS Email Notification](screenshots/sns_email_notification.png)

**Evidence:**
- Screenshot: `screenshots/cloudwatch_alarm_in_alarm.png`
- Screenshot: `screenshots/sns_email_notification.png`

## Timeline (UTC)

| Time (UTC) | Event |
|-----------|------|
| 12:05 | Backend container manually stopped using docker compose |
| 12:05 | `curl http://127.0.0.1/api/health` returned `502 Bad Gateway` |
| 12:07 | ALB Target Group health check failed |
| 12:08 | CloudWatch alarm moved to `INSUFFICIENT_DATA` |
| 12:10 | Alarm moved to `ALARM` |
| 12:11 | SNS email notification received |
| 12:15 | Backend restarted using docker compose |
| 12:17 | ALB target became healthy |
| 12:18 | Alarm returned to `OK` |

![TODO: SSM Terminal 502](screenshots/ssm_terminal_502.png)
![TODO: ALB Target Unhealthy](screenshots/alb_target_unhealthy.png)
![TODO: CloudWatch Alarm History](screenshots/cloudwatch_alarm_history.png)

**Evidence:**
- Screenshot: `screenshots/ssm_terminal_502.png`
- Screenshot: `screenshots/alb_target_unhealthy.png`
- Screenshot: `screenshots/cloudwatch_alarm_history.png`

## Root Cause

The backend service container (`lexiconnect-backend-1`) was stopped, causing NGINX reverse proxy to fail when forwarding requests to the backend. This resulted in ALB health checks failing and ALB reporting 0 healthy targets.

## Contributing Factors

- Backend container failure was not automatically recovered
- Deployment system did not use Auto Scaling Group (single EC2 instance)
- No container restart policy was configured initially
- CloudWatch alarm was configured with missing-data behavior that temporarily showed `INSUFFICIENT_DATA`

## Resolution

The backend container was restarted using:

```bash
docker compose -f docker-compose.prod.yml up -d backend
```

After restart, ALB health checks succeeded and the target group returned to healthy status. CloudWatch alarm transitioned back to OK.

## Corrective Actions Taken

- Implemented CloudWatch Alarm on HealthyHostCount
- Connected SNS email notifications for alerts
- Verified alarm transitions through simulated backend outage
- Confirmed deterministic deployments using SHA pinned tags

## Preventative Improvements (Planned)

- Add Auto Scaling Group (ASG) to replace failed EC2 automatically
- Add docker restart policy (`restart: always`) for backend and frontend
- Add CloudWatch log shipping for backend logs
- Add ALB 5XX alarm to detect proxy failures early

## Lessons Learned

- CloudWatch alarms require real metric datapoints; otherwise they remain in INSUFFICIENT_DATA
- Backend container availability is critical for ALB health checks
- Alerting is only useful when combined with automated recovery
- SHA-based deployments provide safer rollback and version traceability

## Screenshot Checklist

| Filename | What to Screenshot |
|---|---|
| `cloudwatch_alarm_in_alarm.png` | Alarm showing red "In alarm" |
| `cloudwatch_alarm_history.png` | Alarm History tab showing transitions |
| `sns_email_notification.png` | The email from SNS |
| `ssm_terminal_502.png` | SSM terminal showing curl 502 |
| `alb_target_unhealthy.png` | Target group showing unhealthy |
| `github_actions_deploy_success.png` | Deploy workflow run success |
| `github_actions_build_sha.png` | Build workflow showing commit SHA |
