from pathlib import Path

app_file = Path("C:/Users/lenovo/.gemini/antigravity/scratch/Cricket/gl_engine/web_app.py")

with open(app_file, "r", encoding="utf-8") as f:
    text = f.read()

is_crlf = "\r\n" in text
text_norm = text.replace("\r\n", "\n")

target = """@app.get("/api/health")
def get_health():"""

new_endpoints = """@app.get("/api/sync/daily-matches")
def get_daily_synced_matches(force_refresh: bool = False):
    \"\"\"Discovers and synchronizes all live, upcoming, and completed matches across all formats.\"\"\"
    from .daily_match_sync import get_daily_match_sync_engine
    engine = get_daily_match_sync_engine()
    matches = engine.discover_daily_matches(force_refresh=force_refresh)
    return {
        "status": "success",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "count": len(matches),
        "matches": matches
    }

@app.get("/api/sync/match-commentary/{match_id}")
def get_match_commentary_and_scorecard(match_id: str):
    \"\"\"Scrapes live ball-by-ball commentary, scorecard, and pitch report for a specific fixture.\"\"\"
    from .daily_match_sync import get_daily_match_sync_engine
    engine = get_daily_match_sync_engine()
    data = engine.fetch_live_commentary_and_scorecard(match_id)
    return {
        "status": "success",
        "data": data
    }

@app.get("/api/health")
def get_health():"""

if target in text_norm:
    text_norm = text_norm.replace(target, new_endpoints)
    if is_crlf:
        text_norm = text_norm.replace("\n", "\r\n")
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(text_norm)
    print("web_app.py updated successfully!")
else:
    print("Target not found in web_app.py")
