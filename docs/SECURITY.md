# InfraMon Security Documentation

**Document Version:** 1.0  
**Last Updated:** February 2026

---

## Security Features

InfraMon implements multiple layers of security to protect your infrastructure monitoring system.

### 1. Authentication & Authorization

- **JWT Token Authentication**: Access and refresh tokens with configurable expiration
- **Role-Based Access Control**: Superuser privileges for administrative operations
- **Password Hashing**: bcrypt with automatic salting

### 2. API Security

- **Rate Limiting**: 100 requests per 60-second window per IP
- **Request Size Limits**: Maximum 10MB per request body
- **Input Sanitization**: XSS and injection attack prevention
- **Secure Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection

### 3. CORS Configuration

Production CORS should be restricted to specific origins:

```bash
CORS_ORIGINS=["https://your-domain.com"]
```

### 4. Token Configuration

| Token Type | Default Expiration | Environment Variable |
|------------|-------------------|----------------------|
| Access Token | 30 minutes | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Refresh Token | 7 days | `REFRESH_TOKEN_EXPIRE_DAYS` |

---

## Environment Variables

### Required for Production

```bash
SECRET_KEY=<strong-random-secret-key-at-least-32-chars>
ADMIN_PASSWORD=<strong-password>
DEBUG=false
```

### Security Settings

```bash
# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Request Size (10MB default)
MAX_REQUEST_SIZE=10485760

# CORS
CORS_ORIGINS=["https://trusted-domain.com"]
```

---

## Security Best Practices

### 1. Secrets Management

- Never commit `.env` files to version control
- Use a secrets manager for production deployments
- Rotate secrets regularly

### 2. Network Security

```bash
# Restrict Docker socket access
chmod 660 /var/run/docker.sock

# Use firewall rules
ufw allow from 10.0.0.0/8 to any port 8065
```

### 3. Database Security

- SQLite is suitable for single-instance deployments
- Consider PostgreSQL for production with SSL
- Regular backups required

### 4. Container Security

```yaml
# docker-compose.prod.yml
services:
  backend:
    read_only: true
    cap_drop:
      - ALL
    no_new_privileges: true
```

---

## Vulnerability Mitigation

| Vulnerability | Mitigation |
|--------------|------------|
| XSS | Input sanitization + security headers |
| CSRF | Same-site cookie settings |
| SQL Injection | SQLAlchemy ORM parameterization |
| Rate Limiting | Built-in request throttling |
| Path Traversal | Input validation on file paths |
| Information Disclosure | Error handling + secure headers |

---

## Compliance Notes

InfraMon is designed with security best practices but requires:

1. **HTTPS/TLS termination** via reverse proxy
2. **Regular security audits** of deployed instances
3. **Monitoring and alerting** for suspicious activity
4. **Access logging** and audit trails

---

## Reporting Security Issues

For security vulnerabilities, please:

1. Do not open public issues
2. Contact: security@example.com
3. Allow 48 hours for initial response
