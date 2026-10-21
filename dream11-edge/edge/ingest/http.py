from __future__ import annotations

import random
import time

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
APP_UA = ("Dalvik/2.1.0 (Linux; U; Android 13) Dream11/2024.1")

_last = [0.0]


def _throttle(min_gap: float = 0.6) -> None:
    gap = time.time() - _last[0]
    if gap < min_gap:
        time.sleep(min_gap - gap + random.uniform(0, 0.25))
    _last[0] = time.time()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=12))
def get_json(url: str, params: dict | None = None, ua: str = UA, timeout: int = 20):
    _throttle()
    r = httpx.get(url, params=params,
                  headers={"User-Agent": ua, "Accept": "application/json"},
                  timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    return r.json()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=12))
def get_text(url: str, params: dict | None = None, ua: str = UA, timeout: int = 20) -> str:
    _throttle()
    r = httpx.get(url, params=params, headers={"User-Agent": ua},
                  timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    return r.text
