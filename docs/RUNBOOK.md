# LexiConnect Runbook

## Service Endpoints
- Web: `http://<ALB_DNS>/`
- Health: `http://<ALB_DNS>/health`
- API Health: `http://<ALB_DNS>/api/health`
- Swagger: `http://<ALB_DNS>/docs` (also works: `http://<ALB_DNS>/api/docs`)

## Production Deployment Model
- EC2 runs Docker Compose (`deploy/docker-compose.prod.yml`)
- Frontend container serves static site + reverse proxies `/api/*` to backend service
- Backend is internal-only inside Docker network
- RDS is private and only reachable from EC2 SG

---

## Validate System Health (First response steps)

### From your laptop
```bash
curl -i http://<ALB_DNS>/health
curl -i http://<ALB_DNS>/api/health
```

Expected:
- `/health` -> HTTP 200
- `/api/health` -> HTTP 200

### From EC2
```bash
docker compose -f deploy/docker-compose.prod.yml ps
docker ps --format "table {{.Names}}\t{{.Ports}}"
docker compose -f deploy/docker-compose.prod.yml logs --tail=200
docker stats
```

### 1.3 Exposure proof (from EC2)

Run on EC2:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
sudo ss -lntp | egrep ':80|:8000' || true
```

What this proves:
- EC2 host is listening on `:80`
- EC2 host is **not** listening on `0.0.0.0:8000`
- Backend container shows `8000/tcp` only (no host mapping)

---

## Deploy (Manual)

### SSH into EC2
```bash
ssh -i <KEY>.pem ec2-user@<EC2_IP>
```

### Pull latest code
```bash
cd ~/lexiconnect-legal-platform
git pull
```

### Rebuild and restart
```bash
cd deploy
docker compose -f docker-compose.prod.yml down --remove-orphans
docker compose -f docker-compose.prod.yml up -d --build
```

### Confirm
```bash
docker compose -f docker-compose.prod.yml ps
```

---

## Rollback (simple)
```bash
cd ~/lexiconnect-legal-platform
git log --oneline -n 10
git checkout <KNOWN_GOOD_COMMIT>
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Common Incidents

### Incident: API returns 502 / not responding

Symptoms:
- Frontend works but `/api/*` fails
- ALB may still show healthy if `/health` is served by frontend Nginx

Checks:
```bash
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs backend --tail=200
docker compose -f deploy/docker-compose.prod.yml logs frontend --tail=200
```

Fix:
```bash
docker compose -f deploy/docker-compose.prod.yml restart backend
```

### Incident: DB connection errors

Symptoms:
- Backend logs show connection refused / timeout

Checks:
- Verify RDS SG allows 5432 from EC2 SG
- From EC2:

```bash
nc -vz <RDS_ENDPOINT> 5432
```

Fix:
- Correct security groups or DB endpoint env var

---

## Evidence (paste real outputs)

### curl results

```text
PS C:\Users\devmi> curl.exe -i http://lexi-alb-547422898.ap-south-1.elb.amazonaws.com/health
HTTP/1.1 200 OK
Date: Sun, 15 Feb 2026 08:08:43 GMT
Content-Type: text/plain
Content-Length: 3
Connection: keep-alive
Server: nginx/1.29.5

ok
PS C:\Users\devmi> curl.exe -i http://lexi-alb-547422898.ap-south-1.elb.amazonaws.com/api/health
HTTP/1.1 200 OK
Date: Sun, 15 Feb 2026 08:08:43 GMT
Content-Type: application/json
Content-Length: 15
Connection: keep-alive
Server: nginx/1.29.5

{"status":"ok"}
PS C:\Users\devmi>
```

### Exposure proof output

```text
PS C:\Users\devmi> ssh -i "D:\Projects\.ssh\lexi-key.pem" ec2-user@65.1.109.255
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
Last login: Sun Feb 15 08:08:13 2026 from 212.104.231.82
[ec2-user@ip-10-0-0-158 ~]$ docker ps --format "table {{.Names}}\t{{.Ports}}"
NAMES                    PORTS
lexiconnect-frontend-1   0.0.0.0:80->80/tcp, :::80->80/tcp
lexiconnect-backend-1    8000/tcp
[ec2-user@ip-10-0-0-158 ~]$ sudo ss -lntp | egrep ':80|:8000' || true
LISTEN 0      4096         0.0.0.0:80         0.0.0.0:*    users:(("docker-proxy",pid=14818,fd=4))
LISTEN 0      4096            [::]:80            [::]:*    users:(("docker-proxy",pid=14826,fd=4))
[ec2-user@ip-10-0-0-158 ~]$
```

### ALB target health

See screenshot: [`docs/screenshots/alb-targets-healthy.png`](screenshots/alb-targets-healthy.png)

### Screenshot links
- [`docs/screenshots/alb-targets-healthy.png`](screenshots/alb-targets-healthy.png)
- [`docs/screenshots/alb-listener-80.png`](screenshots/alb-listener-80.png)
- [`docs/screenshots/alb-dns.png`](screenshots/alb-dns.png)
