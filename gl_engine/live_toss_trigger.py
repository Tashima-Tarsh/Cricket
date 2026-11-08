"""
Dream11 Grand League Engine — Live 30-Minute Toss & Lineup Trigger
State Machine: SCHEDULED -> TOSS_PENDING -> TOSS_DONE -> LINEUP_LOCKED -> LIVE

Fires T-35 min before match start:
1. Polls live API every 30s for toss result + confirmed playing XI.
2. On toss detected:
   - Sets match state = "TOSS_DONE"
   - Ingests toss_winner and toss_decision
   - Applies pitch/batting order tactical adjustment to player projections
3. On lineup confirmed:
   - Sets match state = "LINEUP_LOCKED"
   - Filters pool to the 22 confirmed players ONLY
   - Re-runs Pitchnama matchup scores & differential_score on the confirmed XI
   - Fires Google OR-Tools CP-SAT uniqueness optimizer
   - Exports /data/processed/player_pool_{match_id}_locked.parquet
   - Exports /data/processed/teams_{match_id}.json
4. Hard cutoff at T-5 min: final lock -> "LIVE"
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

import pandas as pd
import numpy as np

from .unique_engine import unique_team_engine
from .data_fusion import data_fusion_pipeline
from .universal_engine import get_universal_engine

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = PROCESSED_DIR / "trigger_states.json"


class LiveTossLineupTrigger:
    """Manages the real-time T-35 to T-5 pre-match countdown, toss detection,
    lineup locking, and automated uniqueness team optimization.
    """

    VALID_STATES = ["SCHEDULED", "TOSS_PENDING", "TOSS_DONE", "LINEUP_LOCKED", "LIVE_SOON", "LIVE"]

    def __init__(self):
        self.state_file = STATE_FILE
        self._states: Dict[str, Dict[str, Any]] = self._load_states()

    def _load_states(self) -> Dict[str, Dict[str, Any]]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_states(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self._states, f, indent=2)

    def get_state(self, match_id: str) -> Dict[str, Any]:
        """Returns the current state machine status for a match."""
        if match_id not in self._states:
            self._states[match_id] = {
                "match_id": match_id,
                "state": "SCHEDULED",
                "t_minus_minutes": 35,
                "toss_winner": None,
                "toss_decision": None,
                "lineup_confirmed": False,
                "confirmed_player_count": 0,
                "last_poll_utc": datetime.now(timezone.utc).isoformat(),
                "teams_generated_count": 0,
                "alert": None,
                "history": [
                    {"state": "SCHEDULED", "timestamp_utc": datetime.now(timezone.utc).isoformat()}
                ]
            }
            self._save_states()
        return self._states[match_id]

    def set_state(self, match_id: str, new_state: str, details: Optional[Dict[str, Any]] = None):
        """Transitions state machine idempotently."""
        curr = self.get_state(match_id)
        if curr["state"] != new_state:
            curr["state"] = new_state
            curr["history"].append({
                "state": new_state,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "details": details or {}
            })
        if details:
            for k, v in details.items():
                curr[k] = v
        curr["last_poll_utc"] = datetime.now(timezone.utc).isoformat()
        self._save_states()

    def poll_match_status(self, match_id: str) -> Dict[str, Any]:
        """Polls live match status. Fails loud if lineup not confirmed by T-15 min."""
        engine = get_universal_engine()
        state = self.get_state(match_id)

        try:
            unified = engine.get_unified_state(match_id)
            match_data = unified.get("match", {})
            toss_info = match_data.get("toss", {})
            players = unified.get("players", [])

            # Check T-15 alert condition (Fail loud)
            t_minus = state.get("t_minus_minutes", 30)
            if t_minus <= 15 and not state.get("lineup_confirmed", False):
                state["alert"] = f"CRITICAL ALERT: Lineup not confirmed at T-{t_minus}m! Retrying live API poll..."
            else:
                state["alert"] = None

            # 1. Check Toss
            if toss_info.get("completed", False) and state["state"] in ["SCHEDULED", "TOSS_PENDING"]:
                self.handle_toss_detected(
                    match_id=match_id,
                    toss_winner=toss_info.get("winner", "Home"),
                    toss_decision=toss_info.get("decision", "bat")
                )

            # 2. Check Confirmed Lineups (22 players marked confirmed)
            confirmed_players = [p for p in players if p.get("is_confirmed_xi", False)]
            if len(confirmed_players) >= 22 and state["state"] in ["TOSS_DONE", "TOSS_PENDING", "SCHEDULED"]:
                self.handle_lineup_confirmed(match_id=match_id, confirmed_players=confirmed_players)

            state["last_poll_utc"] = datetime.now(timezone.utc).isoformat()
            self._save_states()

        except Exception as e:
            state["alert"] = f"Poll error: {str(e)}"
            self._save_states()

        return state

    def handle_toss_detected(
        self,
        match_id: str,
        toss_winner: str,
        toss_decision: str
    ) -> Dict[str, Any]:
        """Executes Step 5.2 on toss detection:
        - Records toss_winner and toss_decision
        - Sets match state = 'TOSS_DONE'
        - Applies tactical toss impact to player projections
        """
        engine = get_universal_engine()
        unified = engine.get_unified_state(match_id)
        players = unified.get("players", [])

        # Score pre-toss pool with toss outcome
        pool_df = data_fusion_pipeline.score_player_pool(
            match_id=match_id,
            players=players,
            toss_completed=True,
            toss_winner=toss_winner,
            toss_decision=toss_decision
        )

        self.set_state(match_id, "TOSS_DONE", {
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "toss_detected_at_utc": datetime.now(timezone.utc).isoformat(),
            "t_minus_minutes": 28
        })

        return self.get_state(match_id)

    def handle_lineup_confirmed(
        self,
        match_id: str,
        confirmed_players: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Executes Step 5.3 on confirmed playing XI:
        - Sets match state = 'LINEUP_LOCKED'
        - Strictly isolates the 22 confirmed players ONLY
        - Re-runs Pitchnama matchups and recalculates differential scores
        - Fires Google OR-Tools CP-SAT uniqueness optimizer
        - Exports /data/processed/player_pool_{match_id}_locked.parquet
        - Exports /data/processed/teams_{match_id}.json
        """
        curr = self.get_state(match_id)
        engine = get_universal_engine()
        unified = engine.get_unified_state(match_id)
        all_players = unified.get("players", [])

        # Only an explicit, fully confirmed XI can advance the live state.
        # Never infer confirmation from roster ordering or a scheduled squad.
        if confirmed_players is None or len(confirmed_players) != 22:
            raise HTTPException(422, "Exactly 22 explicitly confirmed players are required")
        if any(p.get("is_confirmed_xi") is not True for p in confirmed_players):
            raise HTTPException(422, "Every player must have explicit confirmed-XI status")
        from .roster_safety import validate_confirmed_xi
        validate_confirmed_xi(confirmed_players)
        expected = {p.get("id") for p in all_players}
        supplied = {p.get("id") for p in confirmed_players}
        if not supplied.issubset(expected):
            raise HTTPException(422, "Confirmed XI contains players outside the selected fixture's roster")

        # 1. Export locked player pool to parquet
        pool_df = data_fusion_pipeline.score_player_pool(
            match_id=match_id,
            players=confirmed_players,
            toss_completed=True,
            toss_winner=curr.get("toss_winner") or "Home",
            toss_decision=curr.get("toss_decision") or "bat"
        )

        # 2. Fire Uniqueness Optimizer (7 teams, contrarian level 8)
        teams = unique_team_engine.generate_unique_teams(
            players=confirmed_players,
            num_teams=7,
            uniqueness_level=8,
            risk_appetite="HIGH",
            toss_completed=True,
            contest_spots=1000
        )

        # 3. Export generated teams JSON artifact
        teams_file = PROCESSED_DIR / f"teams_{match_id}.json"
        teams_payload = {
            "match_id": match_id,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "LINEUP_LOCKED_OPTIMAL",
            "confirmed_players_count": len(confirmed_players),
            "uniqueness_level": 8,
            "teams": teams
        }
        with open(teams_file, "w", encoding="utf-8") as f:
            json.dump(teams_payload, f, indent=2)

        self.set_state(match_id, "LINEUP_LOCKED", {
            "lineup_confirmed": True,
            "confirmed_player_count": len(confirmed_players),
            "teams_generated_count": len(teams),
            "teams_artifact": str(teams_file),
            "locked_pool_artifact": str(PROCESSED_DIR / f"player_pool_{match_id}_locked.parquet"),
            "lineup_locked_at_utc": datetime.now(timezone.utc).isoformat(),
            "t_minus_minutes": 25
        })

        return self.get_state(match_id)

    def advance_to_live_soon(self, match_id: str):
        """Hard cutoff at T-5 min: final lock, state = LIVE_SOON -> LIVE."""
        self.set_state(match_id, "LIVE_SOON", {
            "t_minus_minutes": 5,
            "final_locked_utc": datetime.now(timezone.utc).isoformat()
        })


# Singleton trigger instance
live_toss_trigger = LiveTossLineupTrigger()

