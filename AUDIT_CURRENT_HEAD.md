# AUDIT_CURRENT_HEAD.md — STRIKE//OS Evidence-First Source Audit

**Repository**: `https://github.com/Tashima-Tarsh/Cricket`  
**Audit Reference Commit**: `73e11fc43b99a3f57c67289ea95effd7f89e8e07`  
**Current HEAD**: `73e11fc43b99a3f57c67289ea95effd7f89e8e07`  
**Auditor**: Senior Systems Architect & Quantitative Sports Modeler  
**Branch**: `fix/evidence-first-intelligence-repair`  

---

## 1. Executive Summary

A comprehensive source-level audit of the STRIKE//OS codebase was conducted across `gl_engine/`, `dream11-edge/`, `frontend/`, and integration test suites. The objective: eliminate hardcoded match-specific constants, fake data generation, and uncalibrated claims, establishing a single auditable workflow from verified cricket data to legal fantasy lineups.

Each finding is verified directly against executable code and classified as `CONFIRMED`, `PARTIALLY VERIFIED`, `UNVERIFIED`, or `NOT REPRODUCED`.

---

## 2. Source-Level Findings Matrix

### Finding 1: Hardcoded 22-Player Roster in `/api/portal/roster`
- **File**: `gl_engine/web_app.py`
- **Lines**: 1103–1130 (`get_portal_match_roster`)
- **Symbol**: `get_portal_match_roster`
- **Classification**: **CONFIRMED**
- **Problem**: Accepts parameter `match_id` but ignores any non-default match ID, always returning a fixed 22-player Afghanistan vs Zimbabwe roster (`AFG_GURBAZ`, `AFG_ZADRAN`, etc.).
- **Severity**: **CRITICAL**
- **Consumer**: Portal frontend, `/api/portal/solve-lineup`
- **Data Source**: Hardcoded in-memory python list
- **Repair**: Dynamically resolve the player pool using `resolve_match_players(match_id)` or `MASTER_FIXTURES`. Return an explicit 404/503 if the fixture has no verified player pool; do NOT return the AFG-ZIM list for unrelated matches.

---

### Finding 2: Unbound `match_data` in `/api/analyst/query`
- **File**: `gl_engine/web_app.py`
- **Line**: 885
- **Symbol**: `query_ai_analyst`
- **Classification**: **CONFIRMED**
- **Problem**: In the fallback branch, `query_ai_analyst` attempts to read `match_data.get('match_info', {})`. However, only `meta, players = resolve_match_players(clean_id)` exists in scope. Calling this branch raises an unhandled `UnboundLocalError: local variable 'match_data' referenced before assignment`.
- **Severity**: **HIGH**
- **Consumer**: AI Analyst UI chat endpoint
- **Data Source**: Runtime python variable
- **Repair**: Access `meta.get("name")` or `meta.get("title")` instead of referencing undefined `match_data`.

---

### Finding 3: Hardcoded Team Names in `/api/portal/solve-lineup`
- **File**: `gl_engine/web_app.py`
- **Lines**: 1173–1178
- **Symbol**: `solve_portal_lineup`
- **Classification**: **CONFIRMED**
- **Problem**: CP-SAT team balance constraints are hardcoded to `afg = [i for i, p in enumerate(players_data) if p["team"] == "AFG"]` and `zim = ...`. For any non-AFG/ZIM match, both lists are empty, causing CP-SAT to fail with `INFEASIBLE` when `sum(x[i] for i in afg) >= 4` is enforced. Additionally, the route docstring promises "mathematically optimal Solo Rank 1 lineup", violating Rule 8.
- **Severity**: **CRITICAL**
- **Consumer**: Lineup solver UI
- **Data Source**: Hardcoded string filter
- **Repair**: Extract unique teams dynamically from `players_data` (e.g. `teams = list({p["team"] for p in players_data if p.get("team")})`), apply balanced 4-to-7 constraints dynamically per team, and remove "Rank 1" claims from docstrings and responses.

---

### Finding 4: Dummy Player Synthesis in `extract_match_roster`
- **File**: `gl_engine/web_app.py`
- **Lines**: 1354–1389
- **Symbol**: `extract_match_roster`
- **Classification**: **CONFIRMED**
- **Problem**: When a match has fewer than 18 players in lineups, it manufactures fake players with names like `"Top Batter 1"`, `"Star Opener"`, `"Middle Anchor"`, `"Opp Key Opener"`, `"Tailender"`.
- **Severity**: **CRITICAL**
- **Consumer**: Portal DFS simulation, lineup exports
- **Data Source**: Hardcoded tuples `defaults_a` and `defaults_b`
- **Repair**: Remove dummy synthesis completely. Return only verified players present in the fixture. If a downstream consumer requires 22 players, fail fast with a descriptive error (`data_quality: "PARTIAL"`).

---

### Finding 5: Synthetic Matchups and False "LIVE & TRACKED" Label
- **File**: `gl_engine/web_app.py`
- **Lines**: 1535–1630 (`synthesize_bilateral_matchups`), Lines 1667–1710 (`get_portal_match_details`)
- **Symbol**: `synthesize_bilateral_matchups`, `get_portal_match_details`
- **Classification**: **CONFIRMED**
- **Problem**: When a match is not in `MASTER_FIXTURES`, fallback generates synthetic matchups between `"Top Batter 1"` and `"Strike Pacer"` with fake speeds (e.g., `144.2 km/h`) and fake balls faced (e.g., `22 balls, 36 runs`), while marking the fixture as `"LIVE & TRACKED"`.
- **Severity**: **HIGH**
- **Consumer**: Match details portal API
- **Data Source**: Hardcoded synthetic dict
- **Repair**: Return empty arrays for matchups when ball-by-ball delivery history is unavailable. Mark status as `"SCHEDULED_UNTRACKED"` or `"FALLBACK_ESTIMATE"`, explicitly labeling data provenance as unverified baseline.

---

### Finding 6: Artificial 0.946 Scaling in Backtesting
- **File**: `gl_engine/capabilities/c19_backtesting.py`
- **Lines**: 153–155
- **Symbol**: `CricketBacktesting.replay_match_from_duckdb`
- **Classification**: **CONFIRMED**
- **Problem**: Computes the optimal Dream Team from historical deliveries, then simply multiplies that score by `0.946` to simulate engine portfolio performance (`simulated_portfolio_top = round(actual_dream_team_points * 0.946, 1)`), falsely claiming "Backtesting proves that the multi-scenario game script approach consistently captures 94.5% - 96.5%".
- **Severity**: **CRITICAL**
- **Consumer**: Backtesting capability endpoint and CLI
- **Data Source**: Hardcoded float multiplier
- **Repair**: Compute actual portfolio score by simulating historical selection based on pre-match statistics/roles and calculating the real points achieved by those selected players in the holdout match.

---

### Finding 7: Hardcoded India vs West Indies Players in Captain Engine
- **File**: `gl_engine/capabilities/c15_captain_engine.py`
- **Lines**: 37–68
- **Symbol**: `CricketCaptainEngine.execute`
- **Classification**: **CONFIRMED**
- **Problem**: Returns fixed Grand League captain/vice-captain pairs featuring Abhishek Sharma, Arshdeep Singh, Tilak Varma, Mayank Yadav, Romario Shepherd, Shai Hope, Axar Patel, Kuldeep Yadav, Sanju Samson, and Matthew Forde, irrespective of what teams are playing.
- **Severity**: **HIGH**
- **Consumer**: Captaincy analytics and portal strategy views
- **Data Source**: Hardcoded python list
- **Repair**: Dynamically construct correlated captain-vice captain pairs from the actual roster players passed into `CricketCaptainEngine`, using player roles, ceiling scores, and ownership tiers.

---

### Finding 8: Hardcoded India vs West Indies Matchup Insights
- **File**: `gl_engine/capabilities/c07_batter_matchups.py`
- **Lines**: 55–59
- **Symbol**: `CricketBatterMatchups.execute`
- **Classification**: **CONFIRMED**
- **Problem**: Hardcodes three static text insights referring to Abhishek, Ishan, Tilak, Roston Chase, Shivam Dube, Akeal Hosein, and Kuldeep Yadav.
- **Severity**: **MEDIUM**
- **Consumer**: Matchup analysis views
- **Data Source**: Hardcoded strings
- **Repair**: Dynamically generate tactical insights from the input `self.matchups` and `self.players`.

---

### Finding 9: Missing Dot Ball Scoring and Format Flexibility in `c11_fantasy_scoring.py`
- **File**: `gl_engine/capabilities/c11_fantasy_scoring.py`
- **Lines**: 11–85
- **Symbol**: `CricketFantasyScoring.calculate_player_points`
- **Classification**: **CONFIRMED**
- **Problem**: Dot ball scoring (+1 pt in Dream11 T20) is absent from `calculate_player_points`. The method also lacks format awareness (T20 vs ODI vs TEST).
- **Severity**: **HIGH**
- **Consumer**: Fantasy scoring engine, backtesting
- **Data Source**: Logic implementation
- **Repair**: Add `dots: int = 0` to arguments, credit `dots * config.dot_ball`, and support format rules (ODI thresholds for strike rate and economy).

---

### Finding 10: Frontend Vite Proxy Hardcoded to Port 8000
- **File**: `frontend/vite.config.ts`
- **Line**: 16
- **Symbol**: `server.proxy['/api'].target`
- **Classification**: **CONFIRMED**
- **Problem**: Target is hardcoded to `http://127.0.0.1:8000`. Port 8000 is occupied by external processes (e.g., DISHA OSINT), while the local backend server runs on port 8001.
- **Severity**: **MEDIUM**
- **Consumer**: Frontend development server
- **Data Source**: Hardcoded configuration string
- **Repair**: Configure proxy target to use `process.env.VITE_BACKEND_PORT ? `http://127.0.0.1:${process.env.VITE_BACKEND_PORT}` : 'http://127.0.0.1:8001'`.

---

### Finding 11: Uncalibrated Claims in `field_simulator.py`
- **File**: `gl_engine/field_simulator.py`
- **Lines**: 149–153
- **Symbol**: `calibrated_gpp_verdict`
- **Classification**: **PARTIALLY VERIFIED**
- **Problem**: Outputs a field labeled `calibrated_gpp_verdict` even though opponent fields are synthetically generated and uncalibrated to actual contest entry logs.
- **Severity**: **LOW**
- **Consumer**: GPP simulation UI
- **Data Source**: Heuristic decision logic
- **Repair**: Label as `simulation_gpp_verdict` and explicitly output `"calibration_status": "MODEL_ESTIMATE_UNCALIBRATED"`.

---

## 3. Verification Summary

| ID | Module / Symbol | Severity | State | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `web_app.py:get_portal_match_roster` | CRITICAL | CONFIRMED | Dynamic player pool resolution |
| 2 | `web_app.py:query_ai_analyst` | HIGH | CONFIRMED | Fixed undefined `match_data` |
| 3 | `web_app.py:solve_portal_lineup` | CRITICAL | CONFIRMED | Dynamic team constraints & remove Rank 1 claims |
| 4 | `web_app.py:extract_match_roster` | CRITICAL | CONFIRMED | Removed fake dummy player synthesis |
| 5 | `web_app.py:synthesize_bilateral_matchups` | HIGH | CONFIRMED | Return empty matchups & unverified status |
| 6 | `c19_backtesting.py:0.946` | CRITICAL | CONFIRMED | Computed holdout selection points |
| 7 | `c15_captain_engine.py:gl_pairs` | HIGH | CONFIRMED | Dynamic C/VC pairs from active roster |
| 8 | `c07_batter_matchups.py:style_insights` | MEDIUM | CONFIRMED | Dynamic tactical insights |
| 9 | `c11_fantasy_scoring.py:dots` | HIGH | CONFIRMED | Added dot ball scoring & ODI format support |
| 10 | `vite.config.ts:proxy` | MEDIUM | CONFIRMED | Configured default port 8001 |
| 11 | `field_simulator.py:calibrated_gpp_verdict` | LOW | PARTIALLY VERIFIED | Labeled as `MODEL_ESTIMATE_UNCALIBRATED` |
