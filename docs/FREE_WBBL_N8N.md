# Free-only WBBL post-toss n8n integration (research staging)

These additions deliberately **do not** claim to verify an official playing XI or predict profit. This is a conservative first phase of the free-only automation. It runs on your own laptop and requires no paid cricket API.

## Run locally
1. Create a local `.env` from `.env.example`; set a strong `CRICKET_ADMIN_TOKEN` and a separate long random `N8N_ENCRYPTION_KEY`. Do not commit these values.
2. Run `docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d --build`. The backend is on localhost:8844 and n8n on localhost:5678. Both require appropriate local authentication; n8n webhooks are bound to loopback only.
3. Import the three JSON files from `n8n/` into n8n using **Import from File**, inspect the nodes, then activate them. They are shipped inactive intentionally.
4. Install the local userscript `browser/dream11-visible-pool.user.js` in an extension supporting `GM_xmlhttpRequest`, and open your own logged-in Dream11 match page. The script only reads *visible rows*. If the Dream11 UI shows one position tab at a time, visit all four tabs. No teams are selected, submitted or purchased.
5. For automated toss polling, configure `WBBL_FIXTURE_MAP` in `.env` as a JSON mapping from the free feed's match ID to the Dream11 match ID (e.g., `{"cricdata_123":"456"}`), restart n8n and activate its toss workflow. Unmapped matches are skipped rather than silently merged.
6. Use a permitted, source-backed XI publisher or authorized browser to POST an announced XI to the optional `/webhook/wbbl-source-xi` workflow. Two reports from different domains can be compared but are still marked **unattested** until origin and publication authenticity are independently established.

## Evidence and safety contract
- Browser snapshots require player name, explicit role, team and actual credit. Selection percentage can be null. Missing fields are **not invented**.
- Browser snapshots use an observed timestamp, a Dream11 page URL, and per-match local player IDs.
- Historical Cricsheet data must not be promoted to today's pitch or playing XI.
- Toss observations from the free cricdata/ESPN reference feed are `SOURCE_REPORTED_UNVERIFIED`, not official XI evidence.
- Source-reported XIs must contain exactly 11 unique names per team. Agreement between different URLs is **not proof of independent official authentication** because the intake caller supplies the URLs.
- `GET /api/v1/free/matches/{match_id}` (admin bearer required) returns merged recent browser players, latest toss, XI source agreement and the explicit `optimization_ready: false` guard. The legacy provider-verified optimizer is not bypassed.
- These workflows are not a complete automatic source-of-truth pitch/XI collector. A source must lawfully publish and permit access to those facts, and selectors need a real-match verification. Do not interpret an empty response as confirmed absence.
- n8n webhooks are local-only; use a firewall if running outside a private machine. Do not expose them publicly without webhook authentication and TLS.
- Source scraping must respect the publisher's terms. The collector does not access private Dream11 endpoints, cookies, hidden state or anti-bot controls.

## Validate
```bash
python -m pip install -r requirements.txt
python -m pip install 'pydantic>=2.8,<3' pytest
pytest tests/test_free_intake.py tests/test_live_feed_no_fabrication.py -q
```

## Remaining work before production use
1. Verify permitted real-world sources for official announced playing XIs and actual match-day pitch observations; integrate fetchers and a cryptographically/auditably trusted source-adapter boundary.
2. Test browser parsing against the real Dream11 web application and handle dynamic DOM changes without inventing values.
3. Add canonical fixture ID mapping in the application (rather than the environment JSON), full XI-to-Dream11 player mapping, confirmed XI readiness and legitimate fantasy-score optimization.
4. Reconcile legacy scoring and models; validate WBBL-only accuracy and test all full workflows against real matches before promoting them to production.

## WBBL historical API (no paid provider)

The source-filtered DuckDB analytics endpoints accept an explicit date cutoff to
prevent target-day result leakage:

- `GET /api/v1/free/wbbl-history/{player_name}?before=YYYY-MM-DD`
- `GET /api/v1/free/wbbl-matchup?batter=...&bowler=...&before=YYYY-MM-DD`

These report recorded ball-by-ball statistics from matches where both teams belong
to the WBBL franchise list. Results are **not** Dream11 points or a claim of legal
ball counts. Empty data are explicitly marked unavailable rather than replaced with
assumed numbers.
