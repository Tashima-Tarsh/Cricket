# Fresh frontend build: no previously committed demo bundle is used.
FROM node:24-alpine AS frontend-build
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 \
    CRICKET_FIXTURE_DB=/app/var/custom_fixtures.sqlite3
WORKDIR /app
COPY . /app
COPY --from=frontend-build /ui/dist /app/frontend/dist
RUN python -m pip install --no-cache-dir . && \
    mkdir -p /app/var && \
    useradd --create-home --uid 10001 cricket && \
    chown -R cricket:cricket /app/var
USER cricket
EXPOSE 8000
VOLUME ["/app/var"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1
CMD ["sh", "-c", "exec uvicorn gl_engine.web_app:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips 127.0.0.1"]
