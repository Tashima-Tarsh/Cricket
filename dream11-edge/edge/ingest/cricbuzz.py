from __future__ import annotations
try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    from selectolax.parser import HTMLParser
from .http import get_json, get_text

MOBILE = "http://mapps.cricbuzz.com/cbzios/match"
WEB = "https://www.cricbuzz.com"
PITCH_KEYS = {"green_seam": ("green","seam","grass","swing","moist"),
              "dry_turner": ("turn","dry","spin","grip","crack"),
              "flat_batting": ("flat","batting","true","hard","good"),
              "slow_low": ("low","slow","two-paced","sticky")}


def toss(match_id):
    try:
        t = (get_json(f"{MOBILE}/{match_id}").get("header") or {}).get("toss") or {}
        return t.get("winner", ""), t.get("decision", "")
    except Exception:
        return "", ""


def pitch_report(match_id, slug=""):
    for url in ([f"{WEB}/cricket-match/pitch-report/{slug}/{match_id}"] if slug else []) + \
               [f"{WEB}/cricket-scores/{match_id}"]:
        try:
            tree = HTMLParser(get_text(url))
            for sel in ("div.cbz-pitchreport", "div.cbz-toss", "div.pitch-report"):
                n = tree.css_first(sel)
                if n and n.text(strip=True):
                    return n.text(strip=True)
        except Exception:
            continue
    return ""


def classify_pitch(text, fallback="flat"):
    t = (text or "").lower()
    sc = {k: sum(t.count(w) for w in ws) for k, ws in PITCH_KEYS.items()}
    b = max(sc, key=sc.get)
    return b if sc[b] > 0 else fallback
