"""One canonical player_id across three naming conventions."""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz, process


def key(name: str) -> str:
    n = re.sub(r"\(.*?\)", "", str(name)).lower()
    n = re.sub(r"[^a-z ]", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def resolve(names: list[str], roster: pd.DataFrame, threshold: int = 88):
    idx = {key(r.name): r.player_id for r in roster.itertuples()}
    out, misses = {}, []
    for n in names:
        k = key(n)
        if k in idx:
            out[n] = idx[k]
            continue
        hit = process.extractOne(k, list(idx), scorer=fuzz.token_set_ratio)
        if hit and hit[1] >= threshold:
            out[n] = idx[hit[0]]
        else:
            misses.append(n)
    return out, misses
