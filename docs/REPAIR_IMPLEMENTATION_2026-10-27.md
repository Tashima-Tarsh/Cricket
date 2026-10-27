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
