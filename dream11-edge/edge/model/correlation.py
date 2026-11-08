"""Cricket correlation structure from match geometry."""
from __future__ import annotations
import numpy as np
from .copula import repair_psd

BASE = {("same","BAT","BAT"):0.34, ("same","BOWL","BOWL"):0.22, ("same","AR","AR"):0.16,
        ("same","AR","BOWL"):0.14, ("same","AR","BAT"):0.11, ("same","WK","BAT"):0.20,
        ("same","WK","BOWL"):0.18, ("opp","BAT","BOWL"):-0.26, ("opp","AR","BOWL"):-0.17,
        ("opp","BAT","BAT"):-0.11, ("opp","WK","BOWL"):-0.14}
SHIFT = {"flat": {("same","BAT","BAT"):0.08, ("same","BOWL","BOWL"):-0.05},
         "green_seam": {("same","BOWL","BOWL"):0.10, ("same","BAT","BAT"):-0.06},
         "dry_turner": {("same","BOWL","BOWL"):0.07},
         "slow_low": {("same","BOWL","BOWL"):0.05}}


def build(players, pitch="flat"):
    k = len(players)
    C = np.eye(k)
    sh = SHIFT.get(pitch, {})
    for i in range(k):
        a = players[i]
        for j in range(i + 1, k):
            b = players[j]
            rel = "same" if a.team == b.team else "opp"
            r = BASE.get((rel, a.role, b.role), BASE.get((rel, b.role, a.role), 0.02))
            r += sh.get((rel, a.role, b.role), 0.0)
            if rel == "same" and a.role == "BAT" and b.role == "BAT":
                gap = abs(getattr(a, "bat_pos", 5) - getattr(b, "bat_pos", 5))
                r *= max(0.35, 1.0 - 0.16 * gap)
            C[i, j] = C[j, i] = r
    return repair_psd(C)
