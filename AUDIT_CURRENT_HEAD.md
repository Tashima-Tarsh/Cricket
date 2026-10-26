# Current source audit — Phase 0

Repository: https://github.com/Tashima-Tarsh/Cricket

- Baseline main HEAD inspected: `d9689d13144509424a26aab6545468fad5ea01c9`.
- Audited implementation HEAD: `1937adc3a32616fc333818d659d1a468c67d03ba`.
- Branch: `repair/phase-0-evidence-safety`.
- Audit date: 2026-10-26. A subsequent documentation commit records this audit; the SHA above identifies the tested code, avoiding a self-referential document hash.

Research application — projections and Rank claims require independent validation.

## Phase 0 changes

1. Added a shared Pydantic `DataProvenance` in `gl_engine/provenance.py`, also imported by EdgeForge. It includes source, timezone-aware timestamp, verification_status and optional nonnegative sample_size. Legacy data defaults to UNVERIFIED, never VERIFIED. Labeling timestamps are explicitly not observation timestamps. Existing EdgeForge `last_updated` inputs remain accepted.
2. Both FastAPI applications label JSON responses, including handled errors, and nested player/fixture/lineup/projection entities. Invalid evidence metadata fails closed with 503. Downloads and HTML carry `X-Data-Provenance`; OpenAPI has that header but its protocol schema is not rewritten. Numeric team maps remain unchanged. This is transport labeling, not external source verification or a claim that every route has a typed OpenAPI response model.
3. Main Player/Lineup models and direct universal/EdgeForge/legacy portfolio outputs carry provenance. Legacy portfolio tests isolate serialization from its optional MILP solver.
4. The portal roster endpoint delegates to the fixture resolver. Removed its embedded AFG-ZIM roster and broad exception-swallowing fallback. Unknown fixture: 409. Missing/incomplete/duplicate/placeholder roster: 503. Validation runs before universal battle generation and optimization.
5. The bundled fifth-match roster now records its fixture ID. The catalog refuses to reuse it for earlier fixtures. The existing default active fixture remains supported; unknown explicit IDs never become the default.
6. Removed six sets of fabricated matchup/handedness/venue-player cards from the fixture catalog. Empty arrays express unavailable records. Reworded banned role-description phrases without renaming real players.
7. Added a production literal scan plus behavioral tests for match isolation, dynamically extracted teams, roster failures, evidence validation, success/error/download transport, numeric-map preservation and direct lineup output.

## Verification

Environment: Python 3.12, editable root and dream11-edge installs in an isolated virtual environment; dependencies resolved from pyproject.toml, not a production environment lock.

| Check | Result |
| --- | --- |
| Initial new safety tests against baseline | Failed for missing provenance, forbidden literals, missing roster guard and cross-fixture reuse |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | 54 passed |
| `python -m pytest tests dream11-edge/tests -q` | 75 passed; 23 subtests; one Starlette/httpx deprecation warning |
| `python -m pytest dream11-edge/tests -q` | 21 passed |
| `python -m pytest dream11-edge/tests edgeforge/score -q` before legacy provenance test addition | 21 passed, 3 failed; unchanged scoring discrepancies below |
| `npm ci`, `npm run build`, `npm run lint` | Exit 0; lint emits existing warnings; generated dist files not committed |
| `git diff --check` | Passed |
| Full repository `python -m pytest -q` | Six collection errors, listed below; NOT green |
| Remote CI | Not yet observed at audit time |

Full collection errors: `scratch/test_rain.py`, `scratch/test_rain_optimizer.py`, `scratch/test_state.py` connect to absent local servers at import time; `test_curl_statsguru.py` requires undeclared `curl_cffi`; `test_player_stats.py` and `test_statsguru.py` require undeclared `cricdata`.

Unchanged EdgeForge scoring failures: `test_boundary_and_six_bonuses` (58 vs expected 78), `test_wicket_and_dot` (66 vs expected 82), and `test_milestone_highest_only` (batting 138 vs expected 178). These source/tests were not edited. Phase 2 must establish the authoritative ruleset and reconcile the engines; these failures must not be hidden by changing expectations merely to match implementation.

Additional runtime finding: PuLP 4.0.1 satisfies the legacy package's loose dependency declaration but lacks `LpVariable.dicts`, used by `dream11-edge/edge/optimize/solver.py`. Existing solver coverage did not catch this. Phase 6 must fix/pin the compatible API and exercise the real solver. The new legacy provenance test mocks only that solver boundary and does not certify legacy optimization.

## Remaining acceptance gaps

Phase 0 establishes a safety baseline, not completion of the master repair. The literal scan is a bounded guard across gl_engine, edgeforge, dream11-edge/edge and frontend/src (including data JSON); it cannot prove absence of every possible fabricated identity or hardcoded behavior. Tests and offline scratch scripts are outside its production scope.

- Rain captain IDs, portal scenario weight overrides and analyst player-specific fallbacks remain (Phase 1).
- Bundled fixtures, venue estimates, player histories and ownership values remain unverified. Provenance labeling does not repair fabricated numerical histories (Phases 1, 3–4).
- T10, scoring parity, gender threading and DLS labeling require further work (Phases 2–3, 7).
- The artificial 0.946 scaling is absent from scanned production paths, but c19 still selects using workload from the evaluated match: NOT a valid pre-match holdout. Fixed uniqueness claims also remain (Phase 5).
- Three parallel engines, model limitations, API decomposition, port defaults, dependency compatibility and CI scope remain (Phases 6, 8).
- Model sidecar reports R² 0.017. Predictive skill is not established by this repair.

No deployment, default-branch merge or deletion of independently sourced data was performed. Removed invented records remain recoverable in Git history.
