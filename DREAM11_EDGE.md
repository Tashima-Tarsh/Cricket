# DREAM11 EDGE — Complete Build Spec

> A local-first, simulation-driven Dream11 grand league engine.
> Goal: consistent top-1% finishes and real shots at rank 1–3.
> Stack: Python 3.11+, DuckDB, NumPy/SciPy, PuLP, LightGBM, Three.js.

## 0. Instructions for the building agent

1. Create every file in the **File Manifest** with the **exact** contents given.
2. Directory structure matters — respect the paths.
3. After scaffolding: `pip install -e .`, then `edge init`, then `edge build --demo --entries 60`.
4. `edge build --demo` must complete with **zero network calls and zero API keys**.
   If it fails, fix it — do not stub it out.
5. Run `pytest -q`. All tests must pass.
6. Do not add features. Do not rename modules. Do not "improve" the math.

### Non-negotiable invariants

- `edge/model/copula.py::verify` must hold on every run.
  If realised correlation drifts more than 0.06 from target, the run is invalid.
- `edge/score.py` is the single source of truth for points. Nothing re-implements it.
- Every generated lineup must satisfy `edge/optimize/constraints.py::is_legal`.
- The optimizer maximises a **rank percentile**, not expected points.

## 1. What this system does

| Layer | Module | Purpose |
|---|---|---|
| Ingest | `edge/ingest/*` | ESPN fixtures/scorecards, Cricbuzz toss+pitch, Dream11 pool+ownership, Cricsheet corpus |
| Features | `edge/features.py` | Decay-weighted form, batter×bowler-type matchup, phase splits, pitch class |
| Fit | `edge/model/distributions.py` | Empirical family fitting per (role, projection window), affine-matched to each player |
| Correlate | `edge/model/copula.py`, `correlation.py` | Gaussian copula + Iman-Conover, cricket correlation structure |
| Simulate | `edge/model/projections.py`, `simulator.py` | Correlated point matrix (n_sims × n_players) |
| Field | `edge/optimize/field.py` | Sample opponent entries from ownership — the field **copies**, it does not sample independently |
| Optimize | `edge/optimize/solver.py`, `portfolio.py` | MILP with joint captain variables; rank-optimized unique portfolio |
| Live | `edge/live/*` | Toss watcher, conservative relock |

### The core idea

Don't predict points. **Simulate matches.** A projection is a number; a simulation
gives you the joint distribution across all 22 players, which is what lets you rank
lineups, price captains and know your duplication risk. Almost every public Dream11
tool multiplies independent point estimates together. Correlation is the whole game.

## 2. File Manifest

```
dream11-edge/
├── pyproject.toml
├── Makefile
├── .gitignore
├── .env.example
├── README.md
├── config/
│   ├── settings.yaml
│   ├── rules.yaml
│   └── venues.yaml
├── edge/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── score.py
│   ├── features.py
│   ├── report.py
│   ├── cli.py
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── http.py
│   │   ├── espn.py
│   │   ├── cricbuzz.py
│   │   ├── dream11.py
│   │   ├── cricsheet.py
│   │   └── normalize.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── distributions.py
│   │   ├── copula.py
│   │   ├── correlation.py
│   │   ├── ball_model.py
│   │   ├── simulator.py
│   │   └── projections.py
│   ├── optimize/
│   │   ├── __init__.py
│   │   ├── constraints.py
│   │   ├── solver.py
│   │   ├── field.py
│   │   └── portfolio.py
│   └── live/
│       ├── __init__.py
│       ├── watcher.py
│       └── relock.py
├── web/
│   └── dashboard.html
└── tests/
    ├── conftest.py
    ├── test_score.py
    ├── test_copula.py
    └── test_constraints.py
```

