# STRIKE//OS Production Security Policy & Threat Model

**Date:** 2026-10-27  
**Status:** Enforced in Middleware & API Routers  
**Modules:** `gl_engine/admin_auth.py`, `gl_engine/security_middleware.py`, `gl_engine/web_app.py`

---

## 1. Authentication & Authorization Architecture

1. **Bearer Token Protection**:
   - All persistent mutation endpoints (`/teams/save`, `/api/fusion/run-pipeline`, `/api/trigger/*`, `/api/v1/live/verify-xi`) require an `Authorization: Bearer <CRICKET_ADMIN_TOKEN>` header.
   - If `CRICKET_ADMIN_TOKEN` is unset in the environment, mutation endpoints **fail closed** with `HTTP 503 Service Unavailable`.
   - Constant-time secret comparison (`secrets.compare_digest`) is enforced to prevent timing attacks.
2. **Read-Only Public Access**:
   - Fixture discovery, venue statistics, and read-only fantasy scoring rules are accessible without administrative privileges.

---

## 2. Defensive Security Middleware

### HTTP Response Security Headers
Every response emitted by the FastAPI backend carries:
- `X-Content-Type-Options: nosniff` (prevents MIME type sniffing)
- `X-Frame-Options: DENY` (clickjacking defense)
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### Request Payload Bounding
- `ContentSizeLimitMiddleware` inspects incoming `Content-Length`. Requests exceeding **1MB (1,048,576 bytes)** are rejected before processing with `HTTP 413 Payload Too Large`, preventing memory exhaustion DOS attacks.

### Per-IP Rate Limiting
- `IPRateLimiterMiddleware` tracks client IP requests in a 60-second sliding window.
- Traffic exceeding **240 requests/minute** receives `HTTP 429 Too Many Requests`. Health check endpoints (`/api/health`) are whitelisted for monitoring probes.

---

## 3. Strict CORS Isolation

- **Production Rules**: In `CRICKET_ENV=production`, wildcard CORS (`"*"`) is strictly prohibited. The application will raise a startup error if configured with wildcards.
- **Allowed Origins**: Explicitly enumerated via `CRICKET_ALLOWED_ORIGINS` (defaulting to local development ports only).

---

## 4. Secret Hygiene & Logging Guarantees

- Zero API keys, tokens, or credentials are hardcoded into Git.
- Authorization headers and provider secrets are masked in application logs and tracebacks.
