# STRIKE//OS Production Gap Audit & System Baseline

**Audit Date:** 2026-10-27  
**Branch:** `feature/master-execution-all-15`  
**Baseline Commit:** `7a9165b`  
**Auditor:** Autonomous Lead Engineering Team (Architecture, Python, Cricket Quant, MLOps, Security, DevOps, QA)

---

## 1. Executive Summary

This repository audit assesses the current state of **STRIKE//OS** against the **10 Non-Negotiable Engineering Invariants** and production requirements defined in the Master Execution Prompt.

Following the recent merges of Pull Request #6 and Pull Request #7 (`repair/evidence-and-roster-safety-20261027`), major architectural foundations for evidence-first execution, unverified data failing closed, and the elimination of synthetic tracking data have been established. However, critical production gaps and residual hardcodes remain across `gl_engine/`, legacy portal templates, frontend components, and provider integrations that must be resolved to achieve full fixture independence, official scoring fidelity, reproducible forecasting, and secure operation.

---

## 2. Identified Defect Matrix

| ID | Location / File Path | Severity | Current Behavior | Required Repair | Invariant / Phase |
|---|---|---|---|---|---|
| **GAP-01** | `gl_engine/web_app.py` (`solve_portal_lineup`) | **CRITICAL** | Hardcoded player ID weight overrides (`AFG_FAROOQI`, `AFG_OMARZAI`, `ZIM_RAZA`, `ZIM_MUZARABANI`) for specific scenario labels. Default scenario is `"zim_bat_1st"`. | Remove all hardcoded player IDs; compute scenario weights dynamically from active player stats and roles. Default scenario to dynamic `"balanced"`. | Invariant 1 (Zero Hardcodes), Phase 1 |
| **GAP-02** | `gl_engine/web_app.py` (`solve_portal_lineup`) | **CRITICAL** | Returns fabricated metrics: `"uniqueness_percentile": 99.98`, `"collision_probability": "<0.01%"`. | Remove fabricated percentage metrics. Replace with explicit uncalibrated status: `uniqueness_percentile: None`, `collision_probability: None`, `calibration_status: "UNCALIBRATED_SIMULATION"`. | Invariant 5 (No False Rank-1), Phase 1 |
| **GAP-03** | `frontend/src/views/FieldStrategy.tsx`, `GamePlan.tsx`, `ScenarioLab.tsx`, `components/AppShell.tsx` | **MEDIUM** | Displays fallback venue `"M. Chinnaswamy Stadium, Bengaluru"` or hardcoded pitch/dew values when no venue is selected. | Fall back to `"Venue Pending / Unspecified"` with `None` coordinates and explicit missing status. | Invariant 1 & 2, Phase 1 |
| **GAP-04** | `gl_engine/player_battles_mcp.py` | **MEDIUM** | Hardcoded default parameter `venue: str = "M. Chinnaswamy Stadium, Bengaluru"`. | Require explicit venue or default to generic neutral parameter. | Invariant 1, Phase 1 |
| **GAP-05** | `frontend/public/portal.html`, `gl_engine/templates/live_portal.html` | **MEDIUM** | Static HTML contains hardcoded `99.98%` uniqueness and `afg_vs_zim` / `zim_bat_1st` references. | Update templates to remove fixed fixtures and fake probabilities; indicate dynamic simulation status. | Invariant 1 & 5, Phase 1 |
| **GAP-06** | `gl_engine/live_xi_verification.py`, Provider Layer | **HIGH** | Sportmonks and CricketData adapters lack canonical unified interface, rate-limit budgeting, exponential backoff, and circuit breaker. | Implement `CanonicalProvider` interface with timeouts, bounded retries with jitter, schema validation, and health/freshness contracts. | Invariant 4, Phase 2 |
| **GAP-07** | Scoring Modules (`gl_engine/official_scoring.py`, `dream11-edge`, `edgeforge`) | **HIGH** | `official_scoring.py` introduced published rules (`dream11_published_2026_10_27`), but needs complete verification against official Dream11 documentation for T20, ODI, and T10 with all boundary, milestone, economy, and DLS rules. | Consolidate and certify date-versioned scoring rules (`dream11_t20_2026`, `dream11_odi_2026`, `dream11_t10_2026`) with comprehensive unit & boundary regression tests. | Invariant 4, Phase 3 |
| **GAP-08** | End-to-End Match Pipeline & State Machine | **HIGH** | Match state transitions lack formal event logging, multi-format transition checks (T20, ODI, T10, Men/Women), and strict phase validation from `DISCOVERED` to `LOCKED`. | Formalize state machine in `gl_engine/match_pipeline.py` with timestamped audit trail and JSON/CSV export schemas. | Invariant 3 & 4, Phase 4 |
| **GAP-09** | Forecasting & Model Evaluation (`gl_engine/model_validation.py`, `xgboost_model.py`) | **HIGH** | XGBoost model has holdout R² ≈ 0.017; lacks cross-format temporal holdout validation, calibration curves, and explicit uncertainty intervals. | Implement chronological train/test splits, prediction interval coverage, baseline comparisons, and generate `docs/MODEL_VALIDATION.md`. | Invariant 5, Phase 5 |
| **GAP-10** | Optimizer Constraints & Scenarios (`gl_engine/unique_engine.py`, `optimizer.py`) | **HIGH** | Target unspent credit ranges are partially fixed in certain endpoints (e.g. 14.0 Cr). Need fully configurable constraints (exposure, custom credit range, team ratios). | Make credit allocation, exposure caps, and scenario generations fully parameterized without hardcoded numbers. | Invariant 6, Phase 6 |
| **GAP-11** | Security, Rate Limiting & Auth (`gl_engine/admin_auth.py`, `web_app.py`) | **HIGH** | Admin token covers only 5 mutation routes. Public compute-heavy optimization endpoints lack rate limiting, request size limits, and security headers. | Implement rate limiting (token bucket / slowapi), payload size limits (1MB), and production security headers (HSTS, CSP, X-Frame-Options). | Invariant 8, Phase 7 |
| **GAP-12** | Docker & Deployment Configuration | **MEDIUM** | `Dockerfile` exists but requires multi-stage build optimization, non-root user verification, and documented migration from SQLite to transactional PostgreSQL for multi-worker scaling. | Enhance `Dockerfile` and `docker-compose.yml`, write `docs/DEPLOYMENT.md`, and test container lifecycle. | Invariant 7 & 10, Phase 8 |
| **GAP-13** | Frontend Edge Cases & Empty States | **MEDIUM** | Frontend views when no fixture is loaded must display clear guidance rather than empty cards or uncaught rendering errors. | Implement robust empty states, provider status widgets, and clear operator call-to-actions in React UI. | Phase 9 |
| **GAP-14** | Test Parity & CI Automation | **MEDIUM** | CI in `.github/workflows/ci.yml` runs unit tests and pytest, but needs integration test coverage for provider timeouts, optimizer constraints, and Docker build check. | Expand test suites with contract tests, end-to-end pipeline tests, and Docker container verification. | Invariant 10, Phase 8 |
| **GAP-15** | Comprehensive Documentation Suite | **MEDIUM** | Multiple required technical documents (`ARCHITECTURE.md`, `PROVIDER_INTEGRATIONS.md`, `SCORING_RULES.md`, `MODEL_VALIDATION.md`, `GRAND_LEAGUE_OPTIMIZER.md`, `SECURITY.md`, `DEPLOYMENT.md`, `PRODUCTION_ACCEPTANCE_REPORT.md`) need authoring or updating. | Deliver complete, verifiable documentation matching implementation reality. | Invariant 10, Phase 10 |

---

## 3. Test Baseline Assessment

- **Pytest Suite (`tests/`, `dream11-edge/tests/`, `edgeforge/`)**: **125 passed**, 1 warning, 38 subtests passed in 12.31s.
- **Python Version**: 3.11.9
- **Database Engine**: DuckDB 1.5.6 (historical ball-by-ball archive: 134,722 deliveries indexed) + SQLite runtime fixture store.
- **Zero Forbidden Production Literals**: Text scan over `gl_engine`, `edgeforge`, `dream11-edge/edge`, `frontend/src` confirmed zero hits for banned synthetic tokens.

---

## 4. Phase-by-Phase Remediation Roadmap

1. **Phase 1**: Fix GAP-01, GAP-02, GAP-03, GAP-04, GAP-05 (purge remaining residual player weight overrides, fake uniqueness percentiles, and hardcoded venue fallbacks).
2. **Phase 2**: Fix GAP-06 (canonical provider architecture, rate limiting, and contract tests; document in `docs/PROVIDER_INTEGRATIONS.md`).
3. **Phase 3**: Fix GAP-07 (official scoring consolidation and date-versioned rules; document in `docs/SCORING_RULES.md`).
4. **Phase 4**: Fix GAP-08 (dynamic end-to-end pipeline, state machine, and JSON/CSV exports; document in `docs/ARCHITECTURE.md`).
5. **Phase 5**: Fix GAP-09 (forecasting calibration, temporal holdout, and uncertainty; document in `docs/MODEL_VALIDATION.md`).
6. **Phase 6**: Fix GAP-10 (configurable Grand League optimization, exposure caps, and portfolio engine; document in `docs/GRAND_LEAGUE_OPTIMIZER.md`).
7. **Phase 7**: Fix GAP-11 (security hardening, rate limiting, request size bounds, and security headers; document in `docs/SECURITY.md`).
8. **Phase 8**: Fix GAP-12 & GAP-14 (Docker multi-stage, health checks, storage persistence, and CI; document in `docs/DEPLOYMENT.md` and `.env.example`).
9. **Phase 9**: Fix GAP-13 (frontend UI polish, empty states, and responsive views).
10. **Phase 10**: Fix GAP-15 (release acceptance report in `docs/PRODUCTION_ACCEPTANCE_REPORT.md` and updated `README.md`).
