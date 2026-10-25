# EdgeForge

Clean, zero-hardcode, simulation-first Grand League engine for cricket fantasy.

## Design Invariants

1. **No hard-coded players or matchups** – every roster comes from a verified store or provider.
2. **Single scoring source** – `edgeforge.score.dream11.Dream11Scorer` is the only place points are calculated.
3. **Full provenance** – every `Player`, `Fixture`, `Lineup` carries a `DataProvenance` object.
4. **Correlation must verify** – `copula.verify_correlation` must pass or the run is invalid.
5. **Rank & uniqueness over pure projected points**.

## Package Layout

```
edgeforge/
├── models/          # Pydantic schemas (Player, Fixture, Lineup, Provenance)
├── score/           # Dream11Scorer (T20 + ODI, includes dots)
├── ingest/          # RosterResolver + in-memory stores (never fabricates)
├── model/           # Copula + MatchSimulator + FieldSampler
├── optimize/        # RankOptimizer (OR-Tools, rank-percentile objective)
├── api/             # Clean FastAPI routes under /edge/*
└── app.py           # Standalone FastAPI entrypoint
```

## Quick Start

```bash
pip install -e .
pip install ortools fastapi uvicorn

uvicorn edgeforge.app:app --reload --port 8001
```

### Core API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/edge/health` | Health + loaded fixture count |
| POST | `/edge/fixtures` | Load a verified fixture + players |
| GET | `/edge/fixtures` | List loaded fixture IDs |
| GET | `/edge/roster/{fixture_id}` | Verified roster only (404 if missing) |
| POST | `/edge/score` | Official Dream11 points (includes dots) |
| POST | `/edge/optimize` | Rank-aware portfolio (OR-Tools + simulation) |

## Components

### Phase 0+1
- Strict schemas with mandatory provenance
- Complete Dream11 scorer (T20/ODI + dots)
- RosterResolver that refuses synthetic players

### Phase 2 – Simulator + Field
- MatchSimulator: game-script correlation + Gaussian copula
- FieldSampler: ownership-weighted opponent field
- Rank percentile helpers

### Phase 3 – Rank Optimizer
- OR-Tools CP-SAT
- Dynamic team balance (no hard-coded team names)
- Unspent credit band, differentials, role constraints
- Portfolio diversity + post-solve rank percentiles

### Clean API
- All routes under `/edge/*`
- Explicit 404 on missing data
- No fallback to hardcoded players
