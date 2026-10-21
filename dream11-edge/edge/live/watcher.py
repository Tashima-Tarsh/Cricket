from __future__ import annotations
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ..config import settings
from ..ingest import cricbuzz, espn


def now():
    return datetime.now(ZoneInfo(settings().tz))


def wait_for_xi(match, deadline=None, poll=25, verbose=True):
    deadline = deadline or (now() + timedelta(hours=2))
    while now() < deadline:
        xi, ts = {}, ("", "")
        try:
            xi = espn.playing_xi(match.get("series_id", ""), match["match_id"])
        except Exception:
            pass
        try:
            ts = cricbuzz.toss(match["match_id"])
        except Exception:
            pass
        if xi and ts[0]:
            txt = ""
            try:
                txt = cricbuzz.pitch_report(match["match_id"], match.get("slug", ""))
            except Exception:
                pass
            return dict(
                xi=xi,
                toss=dict(winner=ts[0], decision=ts[1]),
                pitch_text=txt,
                pitch_class=cricbuzz.classify_pitch(txt),
                captured_at=now().isoformat(timespec="seconds"),
            )
        if verbose:
            print(f"  waiting · xi={len(xi)} toss={bool(ts[0])} · {now():%H:%M:%S}")
        time.sleep(poll)
    return None
