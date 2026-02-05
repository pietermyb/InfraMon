# InfraMon Deployment Checklist

Use this checklist to ensure a secure and production-ready deployment.

## Pre-Deployment

### Environment Preparation

- [ ] Generate strong SECRET_KEY (at least 32 characters)
  ```bash
  openssl rand -hex 32
  ```

- [ ] Set secure ADMIN_PASSWORD (12+ characters)
  ```bash
  openssl rand -base64 16
  ```

- [ ] Configure CORS_ORIGINS for trusted domains only
  ```bash
  CORS_ORIGINS=["https://your-domain.com"]
  ```

### Security Review

- [ ] Review CORS configuration
- [ ] Verify rate limiting settings
- [ ] Check input sanitization is enabled
- [ ] Confirm DEBUG=false in production

### Infrastructure

- [ ] Provision server with recommended specs:
  - CPU: 2+ cores
  - Memory: 1GB+ RAM
  - Storage: 10GB+ for database and logs

- [ ] Configure firewall rules
  ```bash
  ufw allow 22/tcp
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw enable
  ```

- [ ] Set up SSL/TLS termination (nginx, traefik, or cloud provider)

## Deployment Steps

### 1. Clone Repository

```bash
git clone https://github.com/pietermyb/InfraMon.git
cd InfraMon
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with production values
```

Required `.env` settings:
```bash
SECRET_KEY=<your-strong-secret-key>
ADMIN_PASSWORD=<your-admin-password>
DEBUG=false
CORS_ORIGINS=["https://your-domain.com"]
```

### 3. Build and Start

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Verify health
curl http://localhost:8065/health
```

### 4. Verify Deployment

- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Frontend loads at configured URL
- [ ] API docs accessible at `/api/docs`
- [ ] Login works with admin credentials

## Post-Deployment

### Security Verification

- [ ] Security headers present in responses
- [ ] Rate limiting active (check logs)
- [ ] CORS restricting unauthorized origins

### Monitoring Setup

- [ ] Configure log aggregation
- [ ] Set up health monitoring alerts
- [ ] Enable access logging

### Backup Configuration

- [ ] Schedule regular database backups
- [ ] Test backup restoration procedure
- [ ] Document recovery procedures

## Rollback Procedure

If issues occur after deployment:

```bash
# View previous versions
docker compose -f docker-compose.prod.yml ps

# Rollback to previous version
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check backend health: `curl http://localhost:8065/health` |
| CORS errors | Verify CORS_ORIGINS includes your domain |
| Rate limited | Wait 60 seconds or adjust RATE_LIMIT settings |
| Database locked | Ensure no other processes accessing the DB file |

## Maintenance Schedule

| Task | Frequency |
|------|-----------|
| Review logs | Daily |
| Check health endpoints | Hourly |
| Rotate secrets | Quarterly |
| Backup verification | Monthly |
| Security audit | Annually |
