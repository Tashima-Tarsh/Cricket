# HARDCODE_INVENTORY.md — Source Constants & Fake Data Disposition Inventory

**Repository**: `https://github.com/Tashima-Tarsh/Cricket`  
**Reference Commit**: `73e11fc43b99a3f57c67289ea95effd7f89e8e07`  
**Branch**: `fix/evidence-first-intelligence-repair`  

---

## 1. Inventory Catalog

| Path | Line(s) | Symbol / Construct | Problem Description | Severity | Consumer | Data Source | Planned Repair / Disposition |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gl_engine/web_app.py` | 1106–1128 | `players_data` in `get_portal_match_roster` | Hardcoded 22-player AFG vs ZIM list returned for any match | CRITICAL | Frontend roster selector, solver | Fixed Python list | Dynamically resolve via `resolve_match_players(match_id)` or return 404 |
| `gl_engine/web_app.py` | 1173–1178 | `afg`, `zim` team index lists in `solve_portal_lineup` | Hardcoded AFG and ZIM team keys cause CP-SAT to fail on other matches | CRITICAL | Lineup solver | Hardcoded string match | Extract dynamic unique teams from active roster |
| `gl_engine/web_app.py` | 1354–1389 | `defaults_a`, `defaults_b` in `extract_match_roster` | Synthesizes fake players ("Top Batter 1", "Star Opener", etc.) when real roster < 18 | CRITICAL | Portal DFS sim, lineup exports | Hardcoded mock tuples | Remove dummy synthesis; return only real players and flag partial quality |
| `gl_engine/web_app.py` | 1547–1630 | `synthesize_bilateral_matchups` | Generates fake head-to-head records (speed 144.2 km/h, 36 runs off 22 balls) | HIGH | Match details fallback | Algorithmic mock data | Return empty list when ball-by-ball data is absent; deprecate mock generator |
| `gl_engine/web_app.py` | 1683 | `"status": "LIVE & TRACKED"` in fallback match | Marks unverified fallback response as "LIVE & TRACKED" | HIGH | Portal header status | Mock string | Mark as "ESTIMATED_SCHEDULED" or "DATA_UNAVAILABLE" with unverified notice |
| `gl_engine/web_app.py` | 885 | `match_data.get(...)` in `query_ai_analyst` | References undefined `match_data`, causing UnboundLocalError | HIGH | AI Analyst chat | Bug in local variable | Replace with `meta.get("name")` / `meta.get("title")` |
| `gl_engine/capabilities/c19_backtesting.py` | 153 | `simulated_portfolio_top = round(actual_dream_team_points * 0.946, 1)` | Artificially scales optimal dream team by 0.946 instead of selecting holdout team | CRITICAL | Historical replay capability | Hardcoded multiplier | Compute actual selection points using pre-match projections / roles |
| `gl_engine/capabilities/c19_backtesting.py` | 16–45 | `curated_benchmarks` | Claims "Rank 1 Contender" without empirical competition log | MEDIUM | Capability execution | Hardcoded JSON list | Label rank as "In the money / Top decile [ESTIMATE]" |
| `gl_engine/capabilities/c15_captain_engine.py` | 37–68 | `gl_pairs` | Hardcodes India–WI players (Abhishek Sharma, Tilak Varma, etc.) for all matches | HIGH | Captaincy recommendation UI | Fixed dict list | Generate dynamic C/VC combinations from active match roster |
| `gl_engine/capabilities/c07_batter_matchups.py` | 55–59 | `style_insights` | Hardcodes India–WI narrative text strings | MEDIUM | Matchup analytics | Static string list | Build dynamic style insights from `self.matchups` and `self.players` |
| `gl_engine/capabilities/c11_fantasy_scoring.py` | 27–85 | `calculate_player_points` | Omit dot balls (+1) and lacks format distinction (T20 vs ODI) | HIGH | Fantasy scorer | Implementation omission | Add `dots` parameter (+1 pt) and ODI threshold handling |
| `gl_engine/portal_fixtures.py` | 16 | `"161190"` in `afg_vs_zim_sharjah_odi.aliases` | Alias collision: "161190" matches AFG-ZIM instead of NZ vs IND | MEDIUM | Fixture resolver | Misconfigured alias list | Remove "161190" from AFG-ZIM aliases |
| `gl_engine/field_simulator.py` | 149–153 | `calibrated_gpp_verdict` | Uses term "calibrated" for uncalibrated synthetic Monte Carlo field | LOW | GPP simulation view | Heuristic label | Rename to `simulation_gpp_verdict` with `MODEL_ESTIMATE_UNCALIBRATED` |
| `frontend/vite.config.ts` | 16 | `target: 'http://127.0.0.1:8000'` | Hardcoded port 8000 collides with other local services | MEDIUM | Vite proxy | Static URL | Read `VITE_BACKEND_PORT` env var with default `http://127.0.0.1:8001` |

---

## 2. Invariant Rules Applied

1. **Zero Dummy Players**: No function may invent players with names like `"Top Batter 1"`, `"Star Opener"`, or `"Tailender"`.
2. **Deterministic & Auditable Scoring**: Fantasy points must match official rules (including dot balls +1, wickets +30, boundaries +1/+2, milestones +4/+8/+16).
3. **No Uncalibrated "Rank 1" or "Calibrated" Claims**: Solvers find constrained mathematical optima; they do not guarantee tournament placement.
4. **Environment Port Parity**: Backend and frontend configs must agree on port 8001 by default, never assuming port 8000.
