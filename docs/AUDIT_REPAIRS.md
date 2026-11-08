# Cricket audit repairs

Prepared on `fix/audit-integration-contracts`, based on commit `3eb5d68`.
Existing routes are preserved. Deployment remains unverified; repository history
records publication of these repairs.

## Implemented

- Removed the premature API returns and unreachable alternative state path.
  The interactive optimizer now consumes team count, risk, credit band, custom
  credit bounds, overs, captain, scenario, locks, exclusions, confirmed XI,
  exposure percentages and overlap. CSV export uses the same validated contract.
- Unknown fixture IDs return HTTP 409; a missing player pool returns HTTP 503.
  Neither condition selects another fixture. The frontend retains the selected
  fixture when refreshing; rain requests include its ID.
- Solver failure returns no unchecked roster. Hard constraints are never silently
  relaxed. Exposure percentages include zero; a partial exposure-limited portfolio
  is withheld rather than inflating actual exposure. Partial/infeasible status is
  explicit. Custom player IDs preserve distinct punctuation and Unicode names.
  Missing custom-fixture ownership is reported as unavailable: 50% is a neutral
  simulation prior, ownership constraints are omitted, and differential-heavy
  requests without the necessary estimates are rejected.
- Player profiling binds exact-name SQL values and opens DuckDB read-only.
  Historical matchup counts come from recorded deliveries. No hash-generated
  battles or invented control probabilities are returned by the repaired state path.
- Custom fixtures require two complete playing XIs with named players, roles,
  credits, batting hand and batting order. Validation precedes persistence to
  SQLite. An administrator bearer token is mandatory; writes are disabled when
  the server has no token. The form activates only a server-accepted fixture.
- MCP simulation resolves both actual rosters and passes `team_a`, `team_b`,
  `n_sims` and `pitch_class`. Its schema and runtime enforce 1-1,000 simulations.
  The separate contest-simulation API is bounded to 5,000 trials.
- Live-feed outages return an unavailable/empty result. A bundled fixture is
  never promoted to today's schedule. Catalog entries are marked unverified.
- Database health/counts and local query latency are measured. External provider
  configuration is separate from authentication, reachability and synchronization;
  unmeasured values are null. Fixed uniqueness and win probabilities were removed.
- The archive reads the backend catalog. Rain curves, synthetic-field metrics,
  sample graphics and keyword-based analyst replies are explicitly labelled.
  The CSS rule hiding evidence notes was removed.
- Historical XGBoost features use dates strictly before the target date, including
  all role/overs/phase proxies. Entire dates remain together in holdout splits.
  The bundled model was retrained and has a provenance sidecar. No zero-leakage
  certification or calibrated uncertainty claim is made.
- Added backend/frontend GitHub Actions checks and explicit setuptools package
  discovery. Source lint excludes generated bundles. The pre-existing portal is
  retained as a public build input so rebuilding preserves its URL.

## Verification on this checkout

- 26 backend integration/regression tests passed.
- 17 `dream11-edge` tests passed; this remains a separate subsystem.
- TypeScript checking and Vite production build passed.
- Source lint exits successfully with 104 warnings; it is not warning-free.
- Package discovery passed. GitHub Actions is configured, not remotely executed.
- Chrome loaded the rebuilt app, rendered the backend catalog with verification
  labels and switched the selected fixture to Afghanistan-Bangladesh.
- Fresh-process HTTP checks passed for selected-fixture state at 10 overs,
  a requested Tilak captain and scenario, CSV export, corrected model provenance,
  frontend HTML and connected database. See [runtime evidence](AUDIT_RUNTIME_CHECK.json).
- Corrected local model training used 17,526 rows. The saved run measured RMSE
  31.03 fantasy points and R-squared 0.017 on its whole-date holdout. This weak
  result does not establish useful predictive performance.

## Running and remaining gates

Install with `python -m pip install -e ".[dev]"`, build with `npm ci` and
`npm run build` in `frontend`, then run `python run_server.py`.
Set a strong `CRICKET_ADMIN_TOKEN` in the server environment to enable custom
fixture writes. An authorised administrator enters it for the save request;
it is not bundled into JavaScript or stored in browser storage. Optional
`CRICKET_FIXTURE_DB` selects the persistent SQLite file.

[VERIFY REQUIRED] Authenticated live-provider workflows have not been verified.
No actual LLM is connected to the analyst. Official DLS remains unavailable;
the exposed rain calculation is an illustration, not match adjudication.
Model skill, uncertainty coverage and contest metrics require independent
historical validation/calibration. Bundled fixture, venue and ownership claims
are unverified input assumptions. Legacy/reference modules outside the repaired
React flow retain separate data contracts and are not certified by these checks.

These are verified local repairs, not a production-readiness certificate.

## Phase 0 follow-up — 2026-10-26

Audited baseline `d9689d13144509424a26aab6545468fad5ea01c9`; repaired code `1937adc3a32616fc333818d659d1a468c67d03ba` on `repair/phase-0-evidence-safety`.

Added shared provenance, API transport enforcement and direct lineup metadata; removed embedded portal roster and placeholder fixture cards; prevented cross-fixture roster reuse; added fail-closed roster validation and regression tests. Core regression checks: 75 passed across tests/ and dream11-edge/tests. Frontend build/lint succeed with warnings.

This supersedes earlier completion claims: full pytest collection has six errors, EdgeForge has three scoring failures, legacy PuLP solver compatibility is broken, and c19 backtesting still leaks target-match workload. See AUDIT_CURRENT_HEAD.md and HARDCODE_INVENTORY.md for exact findings and remaining phases.

Research application — projections and Rank claims require independent validation.
