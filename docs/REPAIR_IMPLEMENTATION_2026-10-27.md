# Evidence-first repository repairs — October 27, 2026

Branch: `repair/evidence-and-roster-safety-20261027`.

## Implemented in this branch

- Tracking measurements are never synthesized from a ball-by-ball scorecard.
  Unknown pitch coordinates, speed, control and shot categories remain null.
  Synthetic venue pace/soil/dew and win-rate constants were also removed from
  the fusion-derived parquet output.
- Rank-1 and top-10 probability fields are null until real-field calibration;
  the UI shows unavailable. Uncalibrated simulation diagnostics remain internal
  and must not be sold as probability forecasts.
- Optimizers do not reintroduce excluded players or relax missing role constraints,
  and the two core CP-SAT paths post-check role, team, credit and lock constraints.
- XI locking requires exactly 22 explicitly flagged players with 11 per team
  and matching selected fixture identities; never infer a playing XI by order.
- The three scoring *adapters* now use one shared legacy-v3 implementation.
  This is an integration consistency milestone, **not** a validation of
  contemporary Dream11 official scoring rules.
- The old curated backtesting efficiency and post-match-selected team ranks were
  removed. The replacement reports strictly prior-date *partial-score* MAE/RMSE
  for players with >=3 prior appearances. It deliberately excludes fielding,
  announced XI, role and pricing rules; it cannot establish rank-1 predictions.
- Persistent write endpoints require a server-defined CRICKET_ADMIN_TOKEN. The
  token is entered in frontend memory only. Never add real tokens to Git.
- /api/v1 exposes a bounded, versioned facade over the existing engine for
  fixture discovery, roster reading, compatibility scoring and portfolio solving.
- The Vite dev proxy targets port 8000 and covers legacy frontend paths.
- CI checks the TypeScript bundle, Python compilation, tests and EdgeForge scoring.

## Blocking gaps before serious use

1. **Actual official scoring**: the old internal `legacy_v3` profile differs
   from the contemporary Dream11 table (including T20 boundary and 25-run
   bonuses). Pin and verify a contest/date-specific rules snapshot from:
   https://www.dream11.com/fantasy-cricket/point-system
   prior to accepting official contest results. Do not silently reinterpret
   historical scores under newer rules.
2. **Live XI provenance**: an admin-submitted 22-player list is only an admin
   attestation; production needs source/observation timestamps plus
   independent provider cross-checking.
3. **Historical projections**: XGBoost holdout R²=0.017 (saved sidecar).
   An independent out-of-time holdout, calibration reliability, and confidence
   intervals are not established. Thus probabilities remain unavailable.
4. **API consolidation**: versioned endpoints are a facade; legacy routes and
   three source directories have NOT yet been removed. Each old path needs
   contract testing and a deprecation migration before it can be retired.
5. **Backtesting**: partial point proxy cannot be compared to actual platform
   leaderboard ranks until fielding, credits, ownership snapshots and the
   confirmed pre-match XI are sourced and timestamped.
6. **Operations**: no production deployment, rate limiting, managed
   authentication, or remote provider integration has been validated.


## Data-artifact quarantine

The previously committed `data/processed/player_matchups.parquet` and
`venue_profiles.parquet` were produced before the provenance fix and may
contain invented tracking and venue measurements. This repair removes both
derived files from the current branch (they remain retrievable in Git history)
and ignores their future regeneration. Any regeneration must originate from
independently sourced observations. Historical Cricsheet databases are retained.

The three old `/api/pitch/{hawkeye,boundary-geometry,degradation}` endpoints
now return HTTP 503 instead of leaking unsourced measurements from the
experimental pitch-vision module. Rendering-only mock trajectories in the
frontend remain labelled as sample illustrations and must never enter analysis
or be represented as observed.

## New dated official scoring profile (2026-10-27)

The source-backed `dream11_published_2026_10_27` profile is available via
`POST /api/v1/score` with an explicit `rule_version` field for T20, ODI and
T10. The old `legacy_v3` profile remains unchanged for previous consumers;
this avoids silently rewriting old archives. Source:
https://www.dream11.com/fantasy-cricket/point-system

The published rule profile uses T20 boundary +4, six +6, 25/50/75/100
bonuses 4/8/12/16 and five-wicket haul +12; ODI one point per **three**
dot balls with 25 through 150-run thresholds; T10 25/50/75/100 and
two-through-five wicket thresholds. The scorer does not guess dismissals
from a zero-run scorecard; `was_dismissed` must be explicit. Full match
substitute handling still needs fielding participation evidence.

