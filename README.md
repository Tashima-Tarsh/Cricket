# STRIKE//OS — Cricket research and lineup engineering

[![CI](https://github.com/Tashima-Tarsh/Cricket/actions/workflows/ci.yml/badge.svg)](https://github.com/Tashima-Tarsh/Cricket/actions/workflows/ci.yml)

A fixture-independent cricket research application with FastAPI, React,
DuckDB, XGBoost experiments and Google OR-Tools. It supports evidence-bound
batter–bowler analysis, legal fantasy roster validation and scenario exploration.

> **Current status: research-grade, not certified production-grade prediction.**
> Legal lineups are not proof of tournament performance, Rank-1 probability
> or profitability. Historical datasets and provider claims require independent
> verification; unlicensed or unavailable feeds must fail closed.

## Non-negotiable data contracts

- There are **no preloaded live fixtures, hardcoded active teams, player lists,
  venue conditions, fake deliveries or automatic fallback opponents**.
- The selected fixture must be explicitly connected, with exactly **11
  player records per side** and valid names, teams, roles, credits, orders,
  venue and toss. The application rejects invalid or missing roster data.
- Manual user submissions are **user-attested**, never provider-verified by
  virtue of upload. Provider-based XI agreement has its own validation.
- Real archive deliveries are historic research data, not the live selected XI.
  They cannot be silently substituted into a different match.
- Ownership projections, match simulations and optimization remain experimental,
  with score/version and source metadata where available. A missing calibrated
  distribution must be null/unavailable, never a made-up Rank-1 probability.

## Quick start (development)

Requires Python 3.11+, Node 24+ and npm.

```bash
python -m pip install -e '.[dev]'
cd frontend && npm ci && npm run build && cd ..
export CRICKET_ADMIN_TOKEN='replace-with-strong-random-secret'
python -m uvicorn gl_engine.web_app:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. New installs show **No match selected**.
Use Match Setup with the admin token to ingest your own validated fixture.
The token is not stored by the UI. Do not commit credentials.

```bash
curl http://127.0.0.1:8000/api/v1/readiness
curl http://127.0.0.1:8000/api/matches
```

Production-style container build (still requiring protected ingress and
production gates):

```bash
docker build -t strike-os:local .
docker run --rm -p 127.0.0.1:8000:8000 \
  -v strike-fixtures:/app/var \
  -e CRICKET_ENV=production \
  -e CRICKET_ADMIN_TOKEN="$CRICKET_ADMIN_TOKEN" \
  strike-os:local
```

The container builds the UI from source and stores the validated fixture
SQLite database in a persistent volume. Behind a TLS reverse proxy, set
`CRICKET_ALLOWED_ORIGINS` to the browser origins allowed to access the API.

## API overview

| Route | Meaning |
|---|---|
| `GET /api/matches` | Only persisted connected fixtures; initially empty |
| `POST /api/match/ingest` | Authorized manual fixture and XI validation |
| `GET /api/state?match_id=...` | The **requested** connected fixture only |
| `GET /api/portal/match-data?match_id=...` | Selected actual venue and roster metadata, unavailable fields omitted |
| `GET /api/live/toss-feed?match_id=...` | User-attested toss metadata, not invented source weather |
| `GET /api/duckdb/deliveries?match_id=...` | Recorded deliveries for the requested archive fixture, if any |
| `GET /api/v1/readiness` | Truthful capability and model calibration status |
| `GET /api/v1/scoring/rules` | Scoring version and reviewed rules |
| `POST /api/v1/optimize` | Explicit connected fixture and bounded requested teams |
| `GET /api/health` | Process/data-store liveness, not prediction certification |

The legacy bundled-report API and NZ–India single-match screenshot endpoint
are removed/disabled. MCP tools also require explicit fixture IDs.

## Development checks

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pytest -q
cd frontend && npm ci && npm run build && npm run lint
```

CI also runs a dated historical-model evaluation. That report is a research
artifact, not authorization to claim calibrated Rank-1 forecasts.

## Operations, data and documentation suite

Comprehensive engineering and operational documentation:

- **[Production Gap Audit](docs/PRODUCTION_GAP_AUDIT.md)**: Baseline audit and remediation matrix across 15 defect classes.
- **[System Architecture](docs/ARCHITECTURE.md)**: End-to-end 10-state match intelligence pipeline, readiness gates, and JSON/CSV export schemas.
- **[Provider Integrations](docs/PROVIDER_INTEGRATIONS.md)**: Canonical provider interface, rate limiting, circuit breaker, and cross-provider corroboration.
- **[Official Scoring Rules](docs/SCORING_RULES.md)**: Multi-format scoring specifications and published Dream11 rule benchmarks for T20, ODI, and T10.
- **[Model Validation & Forecasting](docs/MODEL_VALIDATION.md)**: Out-of-time chronological validation, prediction intervals, and honest calibration declarations.
- **[Grand League Optimizer](docs/GRAND_LEAGUE_OPTIMIZER.md)**: Google OR-Tools CP-SAT MILP mathematical formulation, dynamic credit boundaries, and anti-chalk constraints.
- **[Production Security](docs/SECURITY.md)**: Bearer authorization, response security headers, payload bounding (1MB), and IP rate limiting (240 rpm).
- **[Production Deployment Guide](docs/DEPLOYMENT.md)**: Multi-stage Docker packaging, non-root user execution, persistence volumes, and disaster recovery.
- **[Production Acceptance Report](docs/PRODUCTION_ACCEPTANCE_REPORT.md)**: Formal release certification, phase-by-phase audit matrix, and GO/NO-GO assessment.

Use `CRICKET_FIXTURE_DB` to relocate the SQLite fixture store. Set
`CRICKET_ENV=production` and a strong `CRICKET_ADMIN_TOKEN` on deployment.
Wildcard CORS is forbidden in production. Do not expose compute-heavy
research routes publicly before adding per-user quotas and rate limiting.

Source archives and test-only fixtures may remain for reproducible historical
experiments. They must never enter the live fixture selection automatically.

## License

Consult [LICENSE](LICENSE) and the terms of each cricket data provider.
