# Runbook: LexiConnect Dev Operations (AWS)

## Scope

Operational runbook for deploy, validate, rollback, and troubleshoot in AWS dev.

## Deploy Model

- Build pipeline pushes GHCR images (`latest` + SHA tags).
- Deploy pipeline triggers after successful build and runs SSM commands on instances tagged `Name=lexiconnect-dev-app`.
- Compose services are pulled and started from GHCR images.

## Validation Commands

Run from laptop against ALB:

```bash
curl -i http://<ALB_DNS>/health
curl -i http://<ALB_DNS>/api/health
```

Run from SSM shell on instance:

```bash
cd /home/ec2-user/LexiConnect/deploy
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=150 backend
docker compose -f docker-compose.prod.yml logs --tail=150 frontend
```

## Deploy (Manual Fallback)

```bash
aws ssm start-session --target <instance-id> --region ap-south-1
cd /home/ec2-user/LexiConnect/deploy
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

## Rollback

Preferred rollback uses SHA-pinned image tags.

1. Identify known-good commit SHA from GitHub Actions build history.
2. On instance, pin compose images to that SHA.
3. Pull and restart stack.

Example:

```bash
cd /home/ec2-user/LexiConnect/deploy
sed -E -i 's#(ghcr.io/devthenu/lexiconnect-backend:).*#\1<KNOWN_GOOD_SHA>#' docker-compose.prod.yml
sed -E -i 's#(ghcr.io/devthenu/lexiconnect-frontend:).*#\1<KNOWN_GOOD_SHA>#' docker-compose.prod.yml
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Incident Checks

If ALB target unhealthy / 502 observed:

```bash
# from laptop
curl -i http://<ALB_DNS>/api/health

# from instance
cd /home/ec2-user/LexiConnect/deploy
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=200 backend
docker compose -f docker-compose.prod.yml logs --tail=200 frontend
```

## Monitoring

- CloudWatch alarm monitors ALB healthy target count.
- SNS notifies alarm transitions.

Evidence:
- `screenshots/cloudwatch_alarm_in_alarm.png`
- `screenshots/cloudwatch_alarm_history.png`
- `screenshots/sns_email_notification.png`

## Related Docs

- `INFRASTRUCTURE.md`
- `SECURITY.md`
- `INCIDENT_RCA_ALB_UNHEALTHY_TARGET.md`
