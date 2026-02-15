# Security Notes

## Network Controls
- ALB is the only public entrypoint
- EC2 inbound is restricted to ALB SG (80) + my IP (22 temporary)
- RDS is private and only allows 5432 from EC2 SG

## Service Exposure
- Backend container is internal only (no host port published)
- Only port 80 is exposed on EC2 host

## SSH Hardening
- PasswordAuthentication disabled
- Root login disabled
- SSH restricted to admin IP (temporary)

## TLS / HTTPS
Current demo uses HTTP because no custom domain is attached, therefore ACM cannot issue a browser-trusted certificate for the ALB DNS name.
Production plan:
- Buy domain
- Validate in Route53 (or external DNS)
- Attach ACM cert to ALB 443
- Redirect 80 -> 443 and enable HSTS

## Evidence
Paste these outputs:

### docker ports

```text
[ec2-user@ip-10-0-0-158 ~]$ docker ps --format "table {{.Names}}\t{{.Ports}}"
NAMES                    PORTS
lexiconnect-frontend-1   0.0.0.0:80->80/tcp, :::80->80/tcp
lexiconnect-backend-1    8000/tcp
```

### host listening ports

```text
[ec2-user@ip-10-0-0-158 ~]$ sudo ss -lntp | egrep ':80|:8000' || true
LISTEN 0      4096         0.0.0.0:80         0.0.0.0:*    users:(("docker-proxy",pid=14818,fd=4))
LISTEN 0      4096            [::]:80            [::]:*    users:(("docker-proxy",pid=14826,fd=4))
```
