# STRIKE//OS Provider Integrations & Canonical Data Architecture

**Date:** 2026-10-27  
**Status:** Certified Canonical Architecture  
**Module:** `gl_engine/providers/canonical_provider.py` & `gl_engine/live_xi_verification.py`

---

## 1. Supported Cricket Data Providers

| Provider | Purpose | License Tier | Key Environment Variable | Data Types Supported |
|---|---|---|---|---|
| **Sportmonks Cricket API** | Live matches, verified lineups, ball-by-ball, scoreboards | Commercial / Licensed API | `SPORTMONKS_API_TOKEN` | Fixtures, Lineups, Scorecards, Venues |
| **CricketData (CricAPI)** | Multi-match live scores, match squads, playing XI | Freemium / Licensed API | `CRICKETDATA_API_KEY` | Fixtures, Squads, Playing XIs, Scorecards |
| **Roanuz Cricket & Fantasy** | Real-time ball-by-ball telemetry, live fantasy points | Commercial Subscription | `ROANUZ_PROJECT_KEY`, `ROANUZ_API_KEY` | Real-time events, credits, live fantasy scores |
| **Cricsheet** | Free, open-source historical ball-by-ball archive | Open Access (Creative Commons) | Local archive / duckdb | 134,722+ deliveries, historical matches |
| **Cricbuzz** | Browser Reference Only | Restricted | None (Scraping prohibited by Terms of Use) | Manual human cross-check only |

> [!IMPORTANT]
> **No Cricbuzz Scraping**: Cricbuzz Terms of Use explicitly prohibit automated data extraction. STRIKE//OS strictly honors provider terms of service; no unofficial JSON endpoints or scrapers are executed.

---

## 2. Canonical Provider Architecture

Every external cricket provider adapts to a standardized schema through `BaseCanonicalAdapter`:

```
┌────────────────────────────────────────────────────────┐
│               Canonical Provider Interface             │
├──────────────────────────┬─────────────────────────────┤
│ CanonicalFixture         │ CanonicalXI / Lineup        │
│ - provider_fixture_id    │ - home_team & away_team     │
│ - competition & format   │ - 11 named home players     │
│ - gender (men/women)     │ - 11 named away players     │
│ - venue & start time UTC │ - toss winner & decision    │
│ - provenance metadata    │ - confirmed timestamp UTC   │
└──────────────────────────┴─────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [Resilience Layer]              [Verification Layer]
   - Timeouts (default 5.0s)       - CrossProviderVerifier
   - Exponential Backoff + Jitter  - Squad vs XI Guard
   - Token-Bucket Rate Limiter     - Conflict Quarantining
   - Circuit Breaker (5 err / 60s) - Provenance Audit Stamp
```

---

## 3. Reliability & Outage Handling

1. **Timeouts**: Every external HTTP call is bounded with a strict timeout (default: 5.0s).
2. **Exponential Backoff & Jitter**: Failed requests retry up to 3 times with `sleep = (2^attempt) * 0.1 + jitter`, preventing thundering herd spikes.
3. **Token Bucket Rate Limiting**: Each provider instance throttles outgoing requests against a configurable capacity and refill rate to prevent rate-limit bans (HTTP 429).
4. **Circuit Breakers**: When 5 consecutive failures occur, the circuit trips to `OPEN` for 60 seconds, immediately short-circuiting downstream calls and protecting the platform from cascading latency. It transitions to `HALF_OPEN` to test recovery before fully restoring to `CLOSED`.
5. **Idempotent Ingestion**: Fixtures and rosters are uniquely keyed by provider and external ID, ensuring repeated calls never duplicate records.

---

## 4. Cross-Provider Corroboration Protocol

To eliminate single-source hallucination or incorrect squad data:

1. **Both Providers Must Agree**: `CrossProviderVerifier` requires independent feeds (e.g. Sportmonks and CricketData) to declare exactly 11 confirmed players per side.
2. **Squad vs XI Distinction**: Generic team squad lists (`is_confirmed=False` or `lineup_status=False`) are rejected. Only explicitly confirmed playing XIs are accepted.
3. **Discrepancy Quarantine**: If provider A and provider B disagree on any player name or team identity, the match fails closed with `ValueError: Discrepancy detected`. Discrepancies are logged in structured JSON and quarantined from optimization pipelines.

---

## 5. Missing Credentials & Offline Operation

When `SPORTMONKS_API_TOKEN` or `CRICKETDATA_API_KEY` are not provided in the environment:

- Client instances report `is_live = False` and `is_configured = False`.
- Automated fixture discovery and live corroboration return structured status: **`BLOCKED — CREDENTIALS REQUIRED`** (HTTP 503).
- Offline tests run exclusively against isolated test-only fixtures (`tests/support_runtime_fixture.py`).
- Synthetic or mock data is **strictly barred** from entering production live feeds.

