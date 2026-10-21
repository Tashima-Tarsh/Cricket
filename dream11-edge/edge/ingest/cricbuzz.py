"""Cricbuzz. We only need the toss and the pitch report from here."""
from __future__ import annotations

try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    from selectolax.parser import HTMLParser

from .http import get_json, get_text

MOBILE = "http://mapps.cricbuzz.com/cbzios/match"
WEB = "https://www.cricbuzz.com"

PITCH_KEYS = {
    "green_seam": ("green", "seam", "grass", "swing", "moist"),
    "dry_turner": ("turn", "dry", "spin", "grip", "crack"),
    "flat_batting": ("flat", "batting", "true", "hard", "good"),
    "slow_low": ("low", "slow", "two-paced", "two paced", "sticky"),
}


def match_json(match_id: str) -> dict:
    return get_json(f"{MOBILE}/{match_id}")


def toss(match_id: str) -> tuple[str, str]:
    try:
        h = match_json(match_id).get("header", {})
        t = h.get("toss") or {}
        return t.get("winner", ""), t.get("decision", "")
    except Exception:
        return "", ""


def pitch_report(match_id: str, slug: str = "") -> str:
    urls = [f"{WEB}/cricket-match/pitch-report/{slug}/{match_id}" if slug else "",
            f"{WEB}/cricket-match/live-scores/{slug}-{match_id}" if slug else "",
            f"{WEB}/cricket-scores/{match_id}"]
    for url in urls:
        if not url:
            continue
        try:
            tree = HTMLParser(get_text(url))
            for sel in ("div.cbz-pitchreport", "div.cbz-toss", "div.pitch-report"):
                node = tree.css_first(sel)
                if node:
                    txt = node.text(strip=True)
                    if txt:
                        return txt
        except Exception:
            continue
    return ""


def classify_pitch(text: str, fallback: str = "flat") -> str:
    t = (text or "").lower()
    scores = {k: sum(t.count(w) for w in ws) for k, ws in PITCH_KEYS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else fallback
