# LexiConnect - Production Deployment Runbook (EC2 + Docker Compose + Nginx + RDS)

This runbook documents how LexiConnect is deployed and operated in production on AWS EC2 using Docker Compose, with PostgreSQL hosted on Amazon RDS.

> **Goal:** If the server is lost tomorrow, a new engineer can rebuild and verify production using this document.

---

## Table of Contents

- [1. Architecture](#1-architecture)
- [2. Live Endpoints](#2-live-endpoints)
- [3. Prerequisites](#3-prerequisites)
- [4. AWS Configuration](#4-aws-configuration)
- [5. Server Bootstrap](#5-server-bootstrap)
- [6. Deploy (Docker Compose)](#6-deploy-docker-compose)
- [7. Verification Checklist](#7-verification-checklist)
- [8. Operations](#8-operations)
- [9. Troubleshooting](#9-troubleshooting)
- [10. Evidence (Screenshots)](#10-evidence-screenshots)

---

## 1. Architecture

### Components

- **Frontend:** Vite build served by **Nginx** container (port 80)
- **Backend:** FastAPI served by **Uvicorn** container (port 8000)
- **Reverse Proxy:** Nginx proxies `/api/*` and `/docs` to backend
- **Database:** Amazon RDS PostgreSQL (private)
- **Host:** Amazon EC2 (Amazon Linux 2023, `t3.micro`)
- **Swap:** 2GB swap enabled (prevents OOM during build on `t3.micro`)

### Diagram (logical)

Client Browser
- `http://<PUBLIC_IP>/` -> Nginx (frontend)
- `http://<PUBLIC_IP>/api/*` -> Nginx -> Backend (Uvicorn)
- Backend -> RDS PostgreSQL

---

## 2. Live Endpoints

- **Frontend:** `http://<PUBLIC_IP>/`
- **API Health:** `http://<PUBLIC_IP>/api/health`
- **Swagger Docs:** `http://<PUBLIC_IP>/docs`

---

## 3. Prerequisites

### Local Machine (Your Laptop)

- SSH client (PowerShell / OpenSSH)
- EC2 keypair file: `lexi-key.pem`

### AWS Resources

- EC2 instance (public IP)
- RDS PostgreSQL instance
- Security Groups configured correctly:
  - EC2 SG allows inbound **22** from your IP, **80** from `0.0.0.0/0`
  - RDS SG allows inbound **5432** from **EC2 SG** (not open to the internet)

---

## 4. AWS Configuration

### 4.1 EC2 Security Group (Inbound)

- [x] SSH (22) -> **My IP**
- [x] HTTP (80) -> `0.0.0.0/0`
- [ ] Optional: Backend debug (8000) -> My IP (prefer OFF in final)

### 4.2 RDS Security Group (Inbound)

- [x] PostgreSQL (5432) -> **Source: EC2 Security Group**

> This ensures DB is private and only reachable from the app server.

---

## 5. Server Bootstrap

### 5.1 SSH into Server

```bash
ssh -i "lexi-key.pem" ec2-user@<PUBLIC_IP>
```

### 5.2 Install Docker

```bash
sudo dnf update -y
sudo dnf install docker -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
newgrp docker
```

Verify:

```bash
docker --version
```

### 5.3 Create Swap (Recommended for `t3.micro`)

Prevents build failures (OOM) when running `npm run build`.

```bash
sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -m
```

Persist across reboot:

```bash
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

---

## 6. Deploy (Docker Compose)

### 6.1 Clone Repo

```bash
cd ~
git clone <YOUR_REPO_URL>
cd lexiconnect-legal-platform
```

### 6.2 Ensure Uploads Directory Exists (Host)

```bash
mkdir -p uploads
```

### 6.3 Deploy Using Production Compose

```bash
cd deploy
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### 6.4 Check Status

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=80 backend
docker compose -f docker-compose.prod.yml logs --tail=80 frontend
```

---

## 7. Verification Checklist

Run these on EC2.

### 7.1 Containers Running

```bash
docker ps
docker compose -f docker-compose.prod.yml ps
```

- [ ] Backend container is Up
- [ ] Frontend container is Up
- [ ] Ports exposed: 80 and 8000

### 7.2 Backend Local Health

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

### 7.3 Nginx Proxy Health

```bash
curl http://localhost/api/health
```

Expected:

```json
{"status":"ok"}
```

### 7.4 Swagger via Proxy

```bash
curl -I http://localhost/docs
```

Expected:

```text
HTTP/1.1 200 OK
```

### 7.5 Public Browser Check

Open:

- [ ] `http://<PUBLIC_IP>/` loads frontend
- [ ] `http://<PUBLIC_IP>/docs` loads Swagger
- [ ] `http://<PUBLIC_IP>/api/health` returns OK

---

## 8. Operations

### 8.1 View Logs

```bash
cd ~/lexiconnect-legal-platform/deploy
docker compose -f docker-compose.prod.yml logs -f
```

### 8.2 Restart

```bash
docker compose -f docker-compose.prod.yml restart
```

Restart only backend:

```bash
docker compose -f docker-compose.prod.yml restart backend
```

### 8.3 Stop Stack

```bash
docker compose -f docker-compose.prod.yml down
```

### 8.4 Update Deployment (Pull Latest + Rebuild)

```bash
cd ~/lexiconnect-legal-platform
git pull

cd deploy
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 9. Troubleshooting

### Problem: Build hangs at `rendering chunks...`

Cause: Low memory on `t3.micro` during `npm run build`.

Fix:

- [ ] Ensure swap is enabled (`free -m`)
- [ ] Rebuild after swap is enabled

```bash
free -m
sudo swapon --show
```

### Problem: `/docs` works but API calls from frontend fail

Check:

- [ ] Nginx routes `/api/` correctly to backend
- [ ] Frontend uses `/api` (recommended) OR correct base URL

Quick test:

```bash
curl http://localhost/api/health
```

### Problem: Backend cannot connect to DB

Check:

- [ ] RDS SG allows inbound 5432 from EC2 SG
- [ ] `DATABASE_URL` is correct
- [ ] Backend logs show successful DB connection

```bash
docker compose -f docker-compose.prod.yml logs --tail=200 backend
```

---

## 10. Evidence (Screenshots)

Place screenshots in: `docs/screenshots/`

| File | Caption |
|---|---|
| `01-ec2-instance-overview.png` | EC2 instance running (public IP, status checks) |
| `02-ec2-security-group-inbound.png` | EC2 SG inbound rules (22 + 80) |
| `03-rds-endpoint-and-security.png` | RDS endpoint + SG inbound from EC2 SG |
| `04-ssh-login.png` | Successful SSH login |
| `05-swap-enabled-free-m.png` | Swap enabled output (`free -m`) |
| `06-docker-compose-ps.png` | Containers running (`docker compose ps`) |
| `07-health-checks.png` | Health checks via `curl` |
| `08-swagger-via-nginx.png` | Swagger accessible via Nginx |
| `09-frontend-homepage.png` | Frontend homepage working via public IP |
