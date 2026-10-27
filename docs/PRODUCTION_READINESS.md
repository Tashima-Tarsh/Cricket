# STRIKE//OS production readiness — 27 October 2026

## Truthful deployment status

The application is **not certified production-ready as a forecasting service**.
It is a research workstation that can be deployed behind authentication and a
TLS reverse proxy. A successful build does not establish profitable predictions.

### What is now guarded
- **No built-in current fixture.** New deployments start with an empty match
  catalog. `GET /api/state` without a selected fixture fails closed.
- **No screenshot-specific endpoints or current-game JSON.** The NZ–IND
  toss-time research was removed from tracked runtime files.
- **No automatically substituted playing XI.** Manual ingestion requires
  exactly 11 names on each side with valid roles, batting orders, credits,
  venue and toss; it is administrator-authorized and labelled USER SUPPLIED.
- **No fabricated pitch/delivery tracking in the React frontend.** No licensed
  tracking connection means no measured delivery trajectories are displayed.
- **No historical master match masquerading as live data.** Archived files
  remain for research/test evaluation only.
- **Scoring and optimization are separate.** An optimizer returning a legal XI
  does NOT establish calibrated rank-1 probability, unique-entry chance or ROI.

### Deployment

1. Set `CRICKET_ADMIN_TOKEN` to a long random secret. Do not commit tokens.
2. Build: `docker build -t strike-os:local .`
3. Run behind authenticated TLS reverse proxy:

   `docker run --rm -p 127.0.0.1:8000:8000 -v strike-fixtures:/app/var -e CRICKET_ADMIN_TOKEN="$CRICKET_ADMIN_TOKEN" strike-os:local`

4. Use the admin token only in the Match Setup dialog for validated manual XI
   ingestion; the dialog clears it afterwards.
5. Optional real providers require licensed `SPORTMONKS_API_TOKEN`,
   `CRICKETDATA_API_KEY`, or Roanuz keys. Those connections must be configured
   and tested before any provider verification claims.
6. Persist/backup the `/app/var` volume; SQLite is not a multi-node live
   synchronization mechanism. For multiple replicas implement transactional
   shared storage and distributed locking.
7. `/api/health` is *liveness*; a `degraded` status signals missing optional
   archive or solver data, not proof a fixture is available.

### Release blockers
- Out-of-time model calibration and credible uplift against transparent
  baselines; current per-player confidence and Rank-1 forecasts unvalidated.
- Historical scorecard/venue data licensing, provider uptime and real XI
  agreement policies; do not infer match readiness from credentials alone.
- Production identity, role-based access, rate limiting, quotas, billing and
  audit logs for internet-facing deployment. Bearer token protects ingestion,
  not every compute-heavy route.
- Request-time optimizer cancellation, concurrency budgets, structured
  observability, error monitoring, backup/restore drills and integration tests
  in a staging deployment.
- Training data leakage/match-format audits beyond the current regression
  suite, and historical rule versions for scoring.
- Dependency pinning and vulnerability management. Python dependencies have
  lower bounds, not a reproducible lockfile.

### Data policy

Short-lived user rosters, contests and screenshots stay out of Git. They
belong in the protected fixture store or separately configured provider cache.
Historical evidence can remain in an archive only with an identifiable source
and must never be represented as the active playing XI.

### Validation
CI performs backend unit tests, PyTest, compilation, model-validation audit
and a frontend build/lint. Follow the branch's latest GitHub Actions run,
not a statement of passing tests in a document.
