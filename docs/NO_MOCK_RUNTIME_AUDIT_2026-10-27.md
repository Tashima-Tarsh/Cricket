# Fresh no-mock runtime audit — 27 October 2026

Base: `main@b88c911b835b116501a3917d69fbc513fc42af58`.
Scope: current user-visible routes, providers, fixture store, selected-match UI and optimizer.
Tests: GitHub Actions on this repair branch; run status must be checked independently.

## P0 repairs implemented in this branch
- Removed `gl_engine/cricbuzz_feed.py`: it padded observed players to 11, fabricated roles, credits, batting hands, bowling styles, ownership, toss and venue numbers.
- `/api/live/matches` returns source references only. `POST /api/live/load/{id}` refuses to create playable fantasy records from incomplete information and requires admin authentication.
- Removed synthetic Cricsheet fantasy ingestion. Real historical scorecards stay accessible as observations through `GET /api/cricsheet/scorecard/{numeric_id}`.
- Deleted fake Sportmonks and CricAPI client fixture/scorecard helper methods.
- Retired legacy fixed Zimbabwe/India four-team API and fixed-market Oracle endpoints; unsupported bookmaker lines, player props and team-phase benchmark data are explicitly unavailable.
- Removed named-player captain aliases, India/WI scenario weights and the 700,000-entry contest override; added explicitly configurable actual field sizes and differential targets.
- Changed Match Setup to prevent a live reference or historical scorecard from becoming a fabricated verified XI, and removed named-opponent scenarios and fake new-player statistics from Match Studio.
- Removed country-based mismatch classification and text-triggered captain point multipliers.
- Win-probability, projected-score, H2H and devig endpoints now require explicit parameters; no preset old fixture results.

## Remaining release blockers (not solved by green CI)

| Severity | File or system | Required proof / work |
|---|---|---|
| P0 | `gl_engine/providers/data_hub.py`, `live_xi_verification.py` | Normalize independent provider fixture IDs through an attested crosswalk; real fresh XI source times and roles/credits required; perform live contract tests with licensed credentials |
| P0 | `gl_engine/match_pipeline.py` | Enforce valid lifecycle transitions, 11 players per team, source trust and export legality instead of accepting any 22-player array |
| P0 | `gl_engine/official_scoring.py` and score adapters | Verify effective-date official rule snapshots and normalize cricket overs in six-ball units; `4.2` notation must not be treated as 4.2 decimal overs |
| P0 | `gl_engine/models.py`, `universal_engine.py` | Separate missing data from numeric zero or 50% priors; keep unobserved venue/ownership/ability fields nullable with evidence statuses; remove misleading fallback certainty |
| P0 | `gl_engine/xgboost_model.py`, `model_validation.py` | Evaluate the actual deployed prediction path against contemporaneous scored contests, not only partial-score archive proxies; historical holdout R² 0.0164 |
| P1 | `gl_engine/field_simulator.py` | Ensure synthetic opponent fields are always explicitly research simulations and cannot be interpreted as actual contest-win or rank probabilities |
| P1 | `frontend/src/views/MatchStudio.tsx` | Connect every editable player field and XI change to validated server state; otherwise retire local draft edit controls that do not affect optimization |
| P1 | `gl_engine/data`, `four_team_optimizer.py`, `datasets_2026.py`, archived scripts | Quarantine historical/single-match examples outside production imports and image; remove stale scheduled fixtures and hard-coded outputs from any remaining public route |
| P1 | Security/API | Per-identity auth, quotas for heavy solve endpoints, streamed request-size bounding, audit logs and shared rate limiting for replicas |
| P1 | Deployment | Build Docker in CI, smoke-test startup and volume persistence, live-provider outage behavior, backup/recovery, concurrency and TLS |
| P1 | Data licensing | Audit ESPN SDK and third-party source rights; no unlicensed automatic scraping of Cricbuzz or platforms |
| P1 | Documentation | Update README and production acceptance language so passing unit tests does not imply data freshness, live licensed XI confirmation or proven profitability |

## Required release gates
1. CI green on exact branch head, with new no-mock regressions.
2. Live licensed provider acceptance test using provider IDs and real observation timestamps; no proof is possible without credentials and service reachability.
3. New empty deployment must not show a playable fixture or bookmaker prices.
4. Manual ingestion must label user-provided data as attested but not independently verified.
5. Verified scoring and legal XI export under date-/format-specific rules.
6. Docker build/smoke run and dashboard E2E with source data.
7. Out-of-time model and ownership validation before surfacing calibrated ranks.

**Release verdict: NO-GO for unattended live forecasting or a public production deployment.** Controlled single-user research using explicitly supplied rosters remains possible. A truthful UNAVAILABLE state is an improvement over fabricated success, but it is not evidence that upstream integrations are working.
