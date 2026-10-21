"""Poll for the toss and confirmed XI until the deadline."""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ..config import settings
from ..ingest import cricbuzz, espn


def now() -> datetime:
    return datetime.now(ZoneInfo(settings().tz))


def wait_for_xi(match: dict, deadline: datetime | None = None,
                poll: int = 25, verbose: bool = True):
    deadline = deadline or (now() + timedelta(hours=2))
    while now() < deadline:
        xi, toss = {}, ("", "")
        try:
            xi = espn.playing_xi(match["series_id"], match["match_id"])
        except Exception:
            pass
        try:
            toss = cricbuzz.toss(match["match_id"])
        except Exception:
            pass

        if xi and toss[0]:
            try:
                pitch_text = cricbuzz.pitch_report(
                    match["match_id"], match.get("slug", ""))
            except Exception:
                pitch_text = ""
            return dict(
                xi=xi,
                toss=dict(winner=toss[0], decision=toss[1]),
                pitch_text=pitch_text,
                pitch_class=cricbuzz.classify_pitch(pitch_text),
                captured_at=now().isoformat(timespec="seconds"),
            )

        if verbose:
            print(f"  waiting · xi={len(xi)} toss={bool(toss[0])} "
                  f"· {now():%H:%M:%S}")
        time.sleep(poll)
    return None
