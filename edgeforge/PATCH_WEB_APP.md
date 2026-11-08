# Kill old portal + official scoring parity

## 1. gl_engine/web_app.py (after CORS middleware)

```python
try:
    from edgeforge.migration import mount_edge_on_app, install_legacy_guards
    mount_edge_on_app(app)
    install_legacy_guards(app)
except Exception as _edge_exc:
    import logging
    logging.getLogger("uvicorn.error").warning("EdgeForge not mounted: %s", _edge_exc)
```

## 2. resolve_match_players — require match_id

```python
def resolve_match_players(match_id=None):
    if not match_id:
        raise HTTPException(400, "match_id is required")
    clean_id = match_id.removeprefix("display_")
    ...
```

## 3. gl_engine/config.py FantasyScoringConfig

- boundary_four = 4.0
- boundary_six = 6.0
- wicket = 30.0
- runs_25_bonus = 4.0 (highest-only: 25/50/75/100)
- five_wickets_bonus = 12.0
- Prefer edgeforge.score.dream11.Dream11Scorer everywhere
