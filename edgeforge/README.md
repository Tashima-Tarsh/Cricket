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
├── ingest/          # RosterResolver (never fabricates)
├── model/           # Copula, correlation, distributions, simulator
├── optimize/        # OR-Tools rank-aware portfolio (next)
├── provenance/      # helpers
└── api/             # FastAPI routes (next)
```

## Quick Start (Phase 0/1)

```python
from edgeforge.score import Dream11Scorer
from edgeforge.models import Player, DataProvenance, Role
from datetime import datetime

scorer = Dream11Scorer()
result = scorer.calculate(
    runs=67, balls_faced=42, fours=6, sixes=3,
    wickets=0, is_playing=True, match_format="T20"
)
print(result.to_dict())
```

## Next Phases

- Phase 2: Full Game-Script Copula simulator + field sampling
- Phase 3: Rank-percentile OR-Tools optimizer with ownership constraints
- Phase 4: Live confirmed-XI + toss watcher
- Phase 5: Backtest harness & public calibration report

## Migration from old gl_engine

Keep old code running. New endpoints and CLI will live under `/edge` or `edgeforge` namespace until cut-over.
