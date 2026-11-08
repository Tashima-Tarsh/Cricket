# Audit repair plan

Scope: the findings in the supplied Cricket report, checked against commit 3eb5d68.
Preserve URLs and existing components. Do not claim live, scientific or production
verification without evidence. Do not add a replacement interface or engine.

1. Reproduce route bypasses, unknown-match fallback, SQL injection, unchecked
   infeasible rosters, ignored constraints, offline fixtures and fixed telemetry.
2. Connect the existing parameter-aware solver to the requested fixture; validate
   bounded inputs, enforce exact player IDs and preserve all hard constraints.
3. Validate and persist authenticated custom fixture ingestion; connect the form
   only after backend acceptance. Reject disconnected live fixtures explicitly.
4. Align the MCP schema and simulator signature and test JSON-RPC end to end.
5. Generate historical model features using strictly earlier dates and hold out
   entire dates. Distinguish synthetic training and unaudited model artifacts.
6. Remove invented current fixtures, provider measurements and calibrated metrics.
   Label sample graphics, rule-based analyst and approximate rain calculations.
7. Add backend and frontend CI checks; run tests/build locally and document limits.

Risks: infeasible requests now return fewer/no lineups instead of relaxing settings;
fixture writes require an admin token; old models require retraining to qualify for
the corrected training contract. Live providers and licensed DLS are external gates.
