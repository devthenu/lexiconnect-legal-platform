# Incident RCA: ALB Target Unhealthy (LexiConnect Dev)

**Date:** 2026-02-18  
**Environment:** dev  
**Service:** LexiConnect (frontend + backend)  
**Severity:** SEV-2 (Service partially unavailable)  
**Status:** Resolved

## Summary

The LexiConnect dev environment experienced downtime where the Application Load Balancer (ALB) reported the target as unhealthy and users received `502 Bad Gateway` errors. The issue was caused by the frontend container being stopped, resulting in failed responses from the instance behind the ALB health checks. CloudWatch alarm for `HealthyHostCount < 1` triggered and SNS notification was received.

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

![CloudWatch Alarm In Alarm](docs/screenshots/cloudwatch_alarm_in_alarm.png)
![SNS Email Notification](docs/screenshots/sns_email_notification.png)

**Evidence:**
![CloudWatch Alarm In Alarm](docs/screenshots/cloudwatch_alarm_in_alarm.png)
![SNS Email Notification](docs/screenshots/sns_email_notification.png)

## Timeline (UTC)

| Time (UTC) | Event |
|-----------|------|
| 13:30 | Frontend container manually stopped using docker compose |
| 13:30 | `curl http://127.0.0.1/api/health` returned `502 Bad Gateway` |
| 13:32 | ALB Target Group health check failed |
| 13:33 | CloudWatch alarm moved to `INSUFFICIENT_DATA` |
| 13:35 | Alarm moved to `ALARM` |
| 13:36 | SNS email notification received |
| 13:40 | Frontend restarted using docker compose |
| 13:42 | ALB target became healthy |
| 13:43 | Alarm returned to `OK` |

![SSM Terminal 502](docs/screenshots/ssm_terminal_502.png)
![ALB Target Unhealthy](docs/screenshots/alb_target_unhealthy.png)
![CloudWatch Alarm History](docs/screenshots/cloudwatch_alarm_history.png)

**Evidence:**
![SSM Terminal 502](docs/screenshots/ssm_terminal_502.png)
![ALB Target Unhealthy](docs/screenshots/alb_target_unhealthy.png)
![CloudWatch Alarm History](docs/screenshots/cloudwatch_alarm_history.png)

## Root Cause

The frontend service container (`lexiconnect-frontend-1`) was stopped, causing the EC2 target to return failed responses for health checks. This resulted in ALB health checks failing and ALB reporting 0 healthy targets.

## Contributing Factors

- Backend container failure was not automatically recovered
- Deployment system did not use Auto Scaling Group (single EC2 instance)
- No container restart policy was configured initially
- CloudWatch alarm was configured with missing-data behavior that temporarily showed `INSUFFICIENT_DATA`

## Resolution

The frontend container was restarted using:

```bash
docker compose -f docker-compose.prod.yml up -d frontend
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
