# STRIKE//OS Platform Architecture & End-to-End Match Pipeline

**Date:** 2026-10-27  
**Status:** Certified Engineering Architecture  
**Modules:** `gl_engine/match_pipeline.py`, `gl_engine/fixture_store.py`, `gl_engine/universal_engine.py`

---

## 1. System Overview

**STRIKE//OS** is an institutional-grade, evidence-first cricket analytics and fantasy optimization platform. It enforces strict data provenance, zero synthetic tracking hallucinations, dynamic multi-format scoring, and constraint-satisfaction integer programming.

```
+-----------------------------------------------------------------------------------------------+
|                                      STRIKE//OS PLATFORM                                      |
+-----------------------------------------------------------------------------------------------+
|  DATA INGESTION & PROVIDERS       SCORING & INTELLIGENCE           OPTIMIZATION & DEPLOYMENT  |
|  - Canonical Provider Interface   - Published Rules Scorer         - OR-Tools CP-SAT Solver   |
|  - Circuit Breaker & Rate Limiter - Bayesian Matchup Shrinkage     - Configurable Credits     |
|  - Cross-Provider Verifier        - Weather & DLS Resource Decay   - Provenance JSON / CSV    |
|  - Cricsheet Historical DuckDB    - Out-of-Time XGBoost Model      - Hardened FastAPI Service |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. End-to-End Match Intelligence Pipeline

```
[1. Fixture Discovery] ──▶ [2. Roster Verification] ──▶ [3. Toss Update]
           │                         │                         │
           ▼                         ▼                         ▼
[6. Matchup Analysis]  ◀── [5. Research Ingestion] ◀── [4. XI Confirmed]
           │
           ▼
[7. Player Projections] ──▶ [8. Scenario Engine] ──▶ [9. CP-SAT Optimizer]
                                                              │
                                                              ▼
                                                    [10. Validated Export]
                                                    (JSON & Contest CSV)
```

1. **Fixture Discovery**: Discovers upcoming fixtures across competitions (IPL, BBL, PSL, ICC World Cups) without preloaded demo defaults.
2. **Roster Verification**: Validates initial squad availability and credit assignments.
3. **Toss Registration**: Records toss winner and batting/bowling decision.
4. **XI Confirmation**: Enforces exactly 11 confirmed players per side (22 total).
5. **Research Ingestion**: Queries historical ball-by-ball deliveries from DuckDB.
6. **Matchup Analysis**: Evaluates batter vs bowler head-to-head records with sample-size shrinkage.
7. **Player Projections**: Computes format-aware expected points, ceiling, and floor.
8. **Scenario Engine**: Generates tactical narratives (pacer surge, spin lock, high chase, collapse recovery).
9. **CP-SAT Optimizer**: Mixed Integer Linear Programming (MILP) solving role, team, and credit constraints.
10. **Validated Export**: Generates validated JSON and upload-ready CSV lineups carrying full audit provenance.

---

## 3. Match Lifecycle State Machine

The platform implements 10 formal states in `gl_engine/match_pipeline.py`:

```
DISCOVERED ───────────▶ ROSTER_PENDING
     │                       │
     ▼                       ▼
ROSTER_AVAILABLE ─────▶ TOSS_PENDING
     │                       │
     ▼                       ▼
XI_PENDING ───────────▶ XI_CONFIRMED
                             │
                             ▼
                      ANALYSIS_READY ──▶ LOCKED ──▶ LIVE ──▶ COMPLETED
```

- `DISCOVERED`: Match ID and metadata registered.
- `ROSTER_PENDING`: Incomplete player pool (<22 players).
- `ROSTER_AVAILABLE`: Full player pools loaded with credit valuations.
- `TOSS_PENDING`: Toss registered; match tactics initialized.
- `XI_PENDING`: Toss completed, waiting for official starting lineups.
- `XI_CONFIRMED`: Exactly 22 players confirmed by independent feeds.
- `ANALYSIS_READY`: Model estimates and matchup telemetry populated.
- `LOCKED`: Contest lock timestamp reached; lineups finalized.
- `LIVE`: Match in progress; live scorecards processing.
- `COMPLETED`: Final fantasy points calculated and archived.

---

## 4. Match Isolation Guarantees

Under Non-Negotiable Invariant 1:
- Every query requires an explicit `match_id`.
- Fixture store and pipeline registries are partitioned by `match_id`.
- Requesting an unknown match fails closed (`HTTP 409` / `HTTP 404`).
- No match ever inherits or falls back to players, statistics, venue coordinates, or captain choices from another match.

---

## 5. Lineup Export Schema

### JSON Schema
```json
{
  "fixture_id": "match_t20_001",
  "format": "T20",
  "scenario": "pacer_dominance",
  "lifecycle_state": "XI_CONFIRMED",
  "readiness": {
    "fixture_discovered": true,
    "roster_available": true,
    "official_xi_confirmed": true,
    "fantasy_credits_available": true,
    "optimization_ready": true
  },
  "total_credits_used": 98.5,
  "unused_credits": 1.5,
  "captain": { "id": "p_01", "name": "Player 1", "team": "TEAM_A", "role": "BAT", "credits": 9.5 },
  "vice_captain": { "id": "p_02", "name": "Player 2", "team": "TEAM_B", "role": "BOWL", "credits": 9.0 },
  "players": [...],
  "exported_at_utc": "2026-10-27T13:35:00Z",
  "provenance": {
    "source": "match_pipeline:match_t20_001",
    "verification_status": "VERIFIED"
  }
}
```

### CSV Schema
```csv
MatchID,PlayerID,PlayerName,Team,Role,Credits,IsCaptain,IsViceCaptain,Scenario
match_t20_001,p_01,Player 1,TEAM_A,BAT,9.5,1,0,pacer_dominance
match_t20_001,p_02,Player 2,TEAM_B,BOWL,9.0,0,1,pacer_dominance
...
```
