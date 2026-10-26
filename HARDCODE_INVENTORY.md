# Hardcode inventory — current Phase 0 baseline

Baseline HEAD: `d9689d13144509424a26aab6545468fad5ea01c9`.
Audited implementation HEAD: `1937adc3a32616fc333818d659d1a468c67d03ba`.
Branch: `repair/phase-0-evidence-safety`. Date: 2026-10-26.

The previous inventory described an older commit and overstated repair completion. This inventory distinguishes confirmed removals from residual findings. Symbol names are the stable references; line numbers change during repair.

| Location / symbol | Evidence and disposition | State / next phase |
| --- | --- | --- |
| `gl_engine/web_app.py:get_portal_match_roster` | Embedded 22-player AFG-ZIM roster and catch-all fallback removed; active/requested resolver only | Repaired, Phase 0 |
| `gl_engine/match_catalog.py:get_match_data` | Fifth-match JSON formerly used for earlier fixtures, with hand-adjusted ownership | Repaired: exact fixture ID binding, Phase 0 |
| `gl_engine/portal_fixtures.py` | Six placeholder matchup lists, six handedness lists, six invented venue-player lists | Removed; unavailable arrays empty, Phase 0 |
| `gl_engine/rain_model.py:get_rain_scenarios` | Five fixed preferred_c/preferred_vc pairs such as ind_abhishek and wi_hope | CONFIRMED residual, Phase 1 |
| `gl_engine/web_app.py:solve_portal_lineup` | AFG_FAROOQI, AFG_OMARZAI, ZIM_RAZA, ZIM_MUZARABANI weight overrides; fixture-specific default scenario | CONFIRMED residual, Phases 1/5 |
| `gl_engine/web_app.py:query_ai_analyst` | Pooran/Samson/Kuldeep/Bumrah fallback selection in query branches | CONFIRMED residual, Phase 1 |
| `gl_engine/web_app.py:solve_portal_lineup` | Fixed uniqueness_percentile=99.98 and collision_probability<0.01% | CONFIRMED unsupported metrics, Phase 5 |
| `gl_engine/universal_engine.py:_profile_match_players` | Fixed recent_scores/recent_wickets, numerical priors and one fixture-specific registry path | CONFIRMED residual; explicit unverified response labeling only, Phases 1/4 |
| `gl_engine/venue_pitch_intelligence.py` | Static venue estimates without individual source verification | CONFIRMED residual, Phase 3 |
| `gl_engine/portal_fixtures.py`, `gl_engine/data/*.json`, registry/catalog modules | Bundled names and numerical claims lack independent source verification | NOT certified; audit and replace fixture-by-fixture, Phases 1/3/4 |
| `gl_engine/capabilities/c19_backtesting.py:replay_match_from_duckdb` | No 0.946 multiplier, but prem_rank uses target-match batters_data/bowlers_data workload | CONFIRMED leakage; chronological selection required, Phase 5 |
| `gl_engine/capabilities/c15_captain_engine.py`, `c07_batter_matchups.py` | Existing regression tests exercise supplied non-IND/WI players | Dynamic tested paths; not evidence all narrative capabilities are clean |
| `gl_engine/models.py:Player` and engine ownership consumers | Legacy 50%/30% ownership defaults remain | Must become unavailable or explicit priors, Phase 5 |
| `gl_engine/web_app.py:__main__` | Backend default still 8000 while frontend proxy defaults to 8001 | CONFIRMED residual, Phase 6 |
| `gl_engine/data/xgboost_fantasy_model.provenance.json` | R² 0.017, independent validation required; metadata incomplete | Skill not established, Phase 6 |
| `dream11-edge/edge/optimize/solver.py` | PuLP API incompatibility with installed 4.0.1 | CONFIRMED runtime failure, Phase 6 |

## Guard scope

`tests/test_phase0_safety.py` scans Python, TypeScript, TSX, HTML and JSON under the three engines and frontend/src for the requested prohibited literals. Source comments and role narratives are included, so harmless role text was rephrased. Behavioral tests separately check fixture isolation and solver team extraction; a text scan cannot establish these semantics.

No claim is made that all hardcodes have been purged. Provenance added in Phase 0 records UNVERIFIED / MODEL_ESTIMATE / SIMULATION as appropriate; it does not transform bundled data into verified observations.
