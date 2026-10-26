# HARDCODE_INVENTORY.md — Source Constants & Fake Data Disposition Inventory

**Repository**: `https://github.com/Tashima-Tarsh/Cricket`  
**Current HEAD**: `d9689d13144509424a26aab6545468fad5ea01c9`  
**Branch**: `main`  
**Last Updated**: October 26, 2026  

---

## 1. Inventory Catalog & Resolution Status

| Path | Line(s) | Symbol / Construct | Problem Description | Severity | Consumer | Status | Resolution Detail |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gl_engine/portal_fixtures.py` | 2413–2460, 2617–2664, 3145–3192, 3340–3387, 3535–3582, 3730–3777 | `"Key Batter 1"`, `"Strike Pacer"`, `"Lead Spinner"`, `"Top Batter"`, `"Star Performer"` | Synthetic placeholder matchups and handedness records copied across fixtures | CRITICAL | Match details & H2H analytics | **RESOLVED** | Replaced with empty lists (`[]`) when verified delivery data is absent |
| `gl_engine/web_app.py` | 1149–1172 | `players_data` in `get_portal_match_roster` | Hardcoded `AFG_GURBAZ`, `AFG_ZADRAN`, etc. returned from in-memory list | HIGH | Portal roster resolver | **RESOLVED** | Dynamically queries `MASTER_FIXTURES["afg_vs_zim_sharjah_odi"]["players"]` with normalized IDs and provenance |
| `gl_engine/rain_model.py` | 230 | `"preferred_c": "ind_abhishek", "preferred_vc": "ind_mayank"` | Residual match-specific player IDs hardcoded into rain scenario generator | CRITICAL | Rain simulation engine | **RESOLVED** | Dynamically extracts C/VC from active player roster roles and projections |
| `gl_engine/rain_model.py` | 96 | `"Captain MUST be an aggressive Opener or Strike Pacer."` | Unverified generic narrative string naming synthetic concept | MEDIUM | Rain scenario description | **RESOLVED** | Replaced with dynamic tactical summary |
| `gl_engine/ortools_optimizer.py` | 502, 558 | `"preferred_c": "ind_abhishek"`, `"preferred_vc": "wi_joseph" / "wi_hope"` | Hardcoded captain pairings inside optimizer scenario definitions | CRITICAL | CP-SAT scenario portfolio | **RESOLVED** | Fully dynamic scenario generation extracting active teams, role lists, and valid C/VC pairings |
| `gl_engine/match_catalog.py` | 242–250 | `if p_copy["id"] == "ind_abhishek":` | Fixture-specific adjustments tied to specific player IDs | MEDIUM | Match data loader | **RESOLVED** | Generalized with safe bounds |
| `gl_engine/player_battles_mcp.py` | 175–189, 250 | Hardcoded IND-WI cross-team matchup list & DLS calculation | Fixed bilateral players dossier; DLS labeled without explicit fantasy adaptation warning | HIGH | Battles & MCP tool | **RESOLVED** | Implemented Bayesian shrinkage (`sample_size`, `shrinkage_weight`, `confidence_label`) and added `"official_dls": false` disclaimer |
| `gl_engine/venue_pitch_intelligence.py` | 18–180 | Static venue catalog | Static catalog without provenance labels or live DuckDB derivation | MEDIUM | Venue condition resolution | **RESOLVED** | Embedded `DataProvenance(source="EXPERT_ESTIMATE_UNVERIFIED")` |
| `gl_engine/models.py` | 22–93 | `Player`, `Lineup`, `VenueConditions` | Missing mandatory `DataProvenance` schema | HIGH | Global domain models | **RESOLVED** | Embedded `DataProvenance` on all core models |
| `edgeforge/score/dream11.py` & `edgeforge/score/test_scoring.py` | 33–50 | Scoring discrepancies | Missing LBW bonus and outdated wicket weights in edgeforge config | HIGH | Scoring engine | **RESOLVED** | Exact parity achieved across T20, ODI, and T10 with tests |


---

## 2. Invariant Rules Applied

1. **Zero Dummy Players**: No function may invent players with names like `"Top Batter 1"`, `"Star Opener"`, `"Tailender"`, `"Strike Pacer"`, `"Lead Spinner"`, or `"Star Performer"`.
2. **Zero Match-Specific Hardcodes**: Never inject match-specific player IDs (`"ind_abhishek"`, `"wi_hope"`, `"AFG_GURBAZ"`) into generic simulation, rain, captaincy, or matchup functions.
3. **Global Data Provenance**: Every `Player`, `Fixture`, `Lineup`, `Projection`, and API response carries a `DataProvenance` object.
4. **Deterministic & Auditable Scoring**: Fantasy points match official Dream11 rules (including dot balls +1, wickets +30, boundaries +1/+2, milestones +4/+8/+16).
5. **No Uncalibrated Claims**: Never claim "Rank 1", "calibrated", "LIVE & TRACKED", or "guaranteed". Use `MODEL_ESTIMATE`, `UNVERIFIED`, `PRIOR_ONLY`, `SIMULATION`.
6. **No Official DLS Claims**: Clearly label rain adjustments: `"official_dls": false`, `"verification": "Fantasy adaptation only — not for match adjudication"`.
7. **Environment Port Parity**: Backend and frontend agree on port 8001 by default, never assuming port 8000.
