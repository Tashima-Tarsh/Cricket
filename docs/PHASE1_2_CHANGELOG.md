# Phase 1 + Phase 2 Execution Report

**Date:** 2026-10-26
**Branch:** main

## Phase 1 — Kill remaining hardcodes

### Fixed: `gl_engine/rain_model.py`
- Removed all hardcoded preferred_c / preferred_vc player IDs (`ind_abhishek`, `ind_mayank`, `wi_hope`, `wi_shepherd`, `ind_arshdeep`, `ind_tilak`, `wi_rutherford`, `wi_joseph`).
- `get_rain_scenarios(overs, players=None)` now:
  - Accepts optional live roster
  - Picks C/VC dynamically via `_pick_dynamic_c_vc` (roles, ceiling, order, pace, ownership leverage)
  - Returns null preferred fields when no roster is supplied (never invents names)
- Renamed team bias keys from `ind_bias`/`wi_bias` → `team_a_bias`/`team_b_bias` (format-agnostic)
- Softened "Rank #1 Solo" language → "High-Ceiling Concentration"
- Explicit `official_dls: False` and verification strings on every scenario

### Already clean (verified)
- `c15_captain_engine.py` — fully dynamic from active roster
- `c07_batter_matchups.py` — dynamic style insights
- No `0.946` multiplier in backtesting
- No "Top Batter 1" / "Star Opener" / "Tailender" strings in production paths

### Softened: `c19_backtesting.py`
- Curated benchmark rank labels changed from "Top 0.0x% finish" → "Top-decile finish [CURATED BENCHMARK ESTIMATE — NOT EMPIRICAL]"

## Phase 2 — Professional multi-format scoring

### Updated: `gl_engine/config.py`
- Documented T20/ODI/T10 support
- Invariants stated in module docstring

### Updated: `gl_engine/capabilities/c11_fantasy_scoring.py`
- First-class formats: **T20, ODI, T10**
- T10 milestones: 20 / 30 / 50
- T10 SR bands (min 5 balls)
- T10 economy bands (min 1 over)
- T10 wicket bonuses (2-wicket / 3-wicket)
- T10 maiden value elevated
- `is_womens` parameter reserved for future gender rule variants
- Dot balls always credited
- Provenance + verification on every response
- Captain/VC multipliers explicitly deferred to lineup evaluation

## Acceptance checklist

- [x] No residual hardcoded preferred player IDs in rain scenarios
- [x] Rain scenarios dynamic from roster or null
- [x] T10 scoring implemented
- [x] T20 + ODI scoring retained and format-aware
- [x] Dot balls present
- [x] Rank language honest on curated benchmarks
- [x] config.py on main (commit e8f3927)

## Remaining to land on remote

The following fixed files are ready and should be applied:
1. `gl_engine/rain_model.py` (full rewrite — dynamic scenarios)
2. `gl_engine/capabilities/c11_fantasy_scoring.py` (T10 + format completeness)
3. `gl_engine/capabilities/c19_backtesting.py` (honest rank labels)

## Next phases

- Phase 3: Venue expansion + live pitch provenance
- Phase 4: H2H sample-size display everywhere
- Phase 5: Optimizer honesty + true hold-out backtest
- Phase 6–8: Architecture cleanup, men/women threading, tests/CI
