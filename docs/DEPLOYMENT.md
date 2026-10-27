# STRIKE//OS Production Deployment & Operations Guide

**Date:** 2026-10-27  
**Module:** `Dockerfile`, `docker-compose.yml`, `.env.example`

---

## 1. Container Architecture & Multi-Stage Builds

The container build pipeline is separated into two isolated stages:

1. **Stage 1: Frontend Build (`node:24-alpine`)**:
   - Executes `npm ci` and `npm run build`.
   - Compiles TypeScript and packages clean production assets into `/ui/dist`.
   - Leaves node binaries and `node_modules` out of the runtime container.
2. **Stage 2: Hardened Runtime (`python:3.11-slim`)**:
   - Copies static assets into `/app/frontend/dist`.
   - Installs Python dependencies in isolated wheels.
   - Runs as unprivileged non-root user `cricket` (`uid=10001`).
   - Mounts `/app/var` volume for persistent database storage.

---

## 2. Quickstart with Docker Compose

1. Copy `.env.example` to `.env` and set `CRICKET_ADMIN_TOKEN`:
   ```bash
   cp .env.example .env
   # Edit .env with your secrets
   ```
2. Build and launch:
   ```bash
   docker compose up -d --build
   ```
3. Verify liveness and readiness:
   ```bash
   curl http://localhost:8844/api/health
   curl http://localhost:8844/api/v1/readiness
   ```

---

## 3. Storage Architecture & Scaling Path

- **Single Instance (Default)**: SQLite storage at `/app/var/custom_fixtures.sqlite3`. Fast, transactional, zero-dependency. Safe for single-worker or single-container instances with persistent volume mounts.
- **Multi-Node / Multi-Replica Scaling**: When deploying behind a horizontal load balancer (e.g. Kubernetes with multiple replicas), SQLite is **not** safe for concurrent multi-host writes.
  - *Migration Path*: Configure `CRICKET_DATABASE_URL=postgresql://user:pass@host:5432/cricket`. Swap SQLite connection layer with SQLAlchemy or asyncpg connection pool with row-level locks.

---

## 4. Health Checks, Liveness & Readiness

- **Liveness Probe**: `GET /api/health`
  - Verifies DuckDB connectivity, historical delivery index count, and process latency.
- **Readiness Probe**: `GET /api/v1/readiness`
  - Reports registered fixture count and uncalibrated prediction notice. Returns HTTP 200 with structured readiness metrics.

---

## 5. Backup & Disaster Recovery

1. **Database Snapshot**:
   ```bash
   sqlite3 /app/var/custom_fixtures.sqlite3 ".backup '/app/var/backup_$(date +%Y%m%d).sqlite3'"
   ```
2. **Restoration**:
   ```bash
   cp /app/var/backup_20261027.sqlite3 /app/var/custom_fixtures.sqlite3
   ```
3. **Rollback Strategy**: Maintain immutable Docker image tags (`strike-os:3.0.0`, `strike-os:3.0.1`). If a release exhibits defects, repoint the reverse proxy or container orchestrator to the previous verified tag.
