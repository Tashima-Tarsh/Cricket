# UI and frontend changes

Implemented locally in D:/cricket. Existing URL paths and workspace tab identifiers are retained. No publication or third-party account changes.

## Changes

- AppShell.tsx: light editorial shell, mobile navigation overlay, workspace/player search, explicit snapshot status and reload.
- index.css and index.html: paper/ivory surfaces, readable contrast, reduced decoration, mobile wrapping, focus indicators, reduced-motion support and restrained favicon. No external font requests.
- App.tsx and WorkspaceBoundary.tsx: lazy workspace loading, corrected dashboard navigation, recoverable workspace-loading errors.
- MatchContext.tsx: empty startup state, bounded loading, errors, retry and snapshot timestamps. No silent mock initialization.
- FantasyLab.tsx: real risk/scenario/captain requests, visible failures, result timestamps, no substitute lineup on failed solve, analysis-export labelling.
- web_app.py and ortools_optimizer.py: validated risk and scenario inputs, captain locking, scenario weights, disconnected-match rejection and vice-captain-only regression fix. Scenario weights remain assumptions.
- SettingsProviders.tsx, providerTelemetry.ts and useGraphics.ts: actual configuration refresh, unverified key status, no invented displayed latency, saved display settings connected to the renderer.
- FieldStrategy.tsx: match-specific device-local saving, save-failure messages, pointer dragging and keyboard positioning.
- useDialog.ts, MatchSetupModal.tsx and IntelligenceDrawer.tsx: dialog focus trap, background inertness, Escape, focus restoration and saved notes. Feed failures no longer become example live matches.
- field_simulator.py: bounded NumPy batch scoring replaces nested opponent-scoring loops. A scalar-reference regression verifies points, percentiles and tied-opponent handling. The final 8-test suite completed in 0.448 seconds, versus 291 seconds before this correction; these are suite timings, not a general workload benchmark.
- Stadium3D.tsx and StadiumWebGL.tsx: low-power 2D default, optional lazy WebGL, graphics-error fallback, pointer orbit, keyboard camera controls, zoom buttons, selectable sample deliveries, working heatmap visibility, frame-rate limit, resize observation and GPU resource disposal.
- Retained analytical views: sample/heuristic/source-verification labels. These labels do not establish the factual accuracy of the underlying records.

## Verification

- `npm run build` in frontend: PASS, includes TypeScript checking.
- `python -B -m unittest discover -s tests -p test_workspace_api.py -v`: PASS, 8 regression tests.
- Existing foundation validation and five-lineup optimizer tests: PASS.
- Browser: all 12 workspaces rendered at the narrow viewport available to the connected Chrome session (338 CSS px). No page-level horizontal overflow after the optimizer correction. An exact 320 CSS px viewport and physical touch hardware were not available for direct verification.
- Browser: navigation drawer and focus restoration, player search, provider configuration refresh, graphics preference saving, keyboard field editing and restoration after reload: PASS.
- Browser: actual custom PACE_DOMINANCE solve with Mayank captain and differential-heavy risk: PASS.
- Browser: optional WebGL canvas, zoom control, switching back to 2D and recovery after a stale lazy chunk: PASS.
- Lint: 0 errors, 97 warnings remain in the retained codebase; this change is not a full lint cleanup.
- Main production JS entry: 265.40 kB uncompressed, about 81.78 kB gzip. Optional WebGL chunk: 555.66 kB uncompressed. The old entry was about 1.03 MB uncompressed; these are asset sizes, not a measured page-load benchmark.

## Operational limits

Restart any already-running backend to load the changed Python API. The existing start_server.bat remains available. The temporary verification server used port 8001 and is stopped after review; an existing port 8000 process is left undisturbed.

Provider refresh checks configuration and the local archive. It does not verify a paid authenticated live request. The existing ML leakage, analytical calibration, official scoring/rule verification and genuine historical backtesting remain separate backend work. Custom match setup changes the local display; optimization is rejected until a matching player pool is connected.
