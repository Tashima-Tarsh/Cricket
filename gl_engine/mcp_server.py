"""Standard Model Context Protocol (MCP) JSON-RPC 2.0 Server.
Enables Claude Desktop, Antigravity, Cursor, and any LLM agent to interact
natively with the Cricket Intelligence Syndicate via standardized tool calls.

Supported Tools:
1. `list_daily_fixtures`: Discovers live, upcoming, and completed cricket matches worldwide.
2. `deconstruct_pitch_commentary`: Extracts seam, spin, bounce, and captaincy quotes via zero-shot NLP.
3. `query_player_h2h`: Ball-by-ball head-to-head batter vs bowler records from 328k DuckDB deliveries.
4. `calculate_dls_target`: Illustrative rain resource estimate, not official DLS.
5. `simulate_ball_by_ball`: 9-class discrete ball delivery Monte Carlo simulation.
6. `solve_gpp_lineups`: Google OR-Tools CP-SAT optimizer enforcing 13.5-19.0 unspent credits and C/VC independence.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent path to sys.path for direct stdio execution
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gl_engine.daily_match_sync import DailyMatchSyncEngine
from gl_engine.nlp_deconstructor import NLPCommentaryDeconstructor
from gl_engine.player_battles_mcp import PlayerBattlesMCPEngine
from gl_engine.universal_engine import get_universal_engine
from gl_engine.ball_simulator import BallByBallGenerativeSimulator

logging.basicConfig(level=logging.ERROR)  # Keep stdout clean for MCP JSON-RPC


class CricketMCPServer:
    def __init__(self):
        self.sync_engine = DailyMatchSyncEngine()
        self.nlp = NLPCommentaryDeconstructor()
        self.battles = PlayerBattlesMCPEngine()
        self.universal = get_universal_engine()
        self.simulator = BallByBallGenerativeSimulator()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns the list of available MCP tools in standard format."""
        return [
            {
                "name": "list_daily_fixtures",
                "description": "Scrapes and returns all live, scheduled, and completed cricket fixtures worldwide with format and archetype tags.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force_refresh": {"type": "boolean", "default": False}
                    }
                }
            },
            {
                "name": "deconstruct_pitch_commentary",
                "description": "Zero-shot NLP deconstructor extracting quantitative pitch modifiers (seam, spin, par score delta) and tactical captain statements.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pitch_report": {"type": "string", "description": "Raw pitch report commentary text"},
                        "toss_quote": {"type": "string", "description": "Captain toss statement text"}
                    },
                    "required": ["pitch_report"]
                }
            },
            {
                "name": "query_player_h2h",
                "description": "Queries historical ball-by-ball head-to-head record between a batter and bowler from DuckDB (1,840 matches).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "batter": {"type": "string", "description": "Batter name (e.g. 'Harmanpreet Kaur')"},
                        "bowler": {"type": "string", "description": "Bowler name (e.g. 'Beloved Biza')"}
                    },
                    "required": ["batter", "bowler"]
                }
            },
            {
                "name": "calculate_dls_target",
                "description": "Illustrative rain-target estimate; not official or licensed DLS.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "first_innings_runs": {"type": "integer", "description": "Runs scored by 1st batting team"},
                        "first_innings_overs": {"type": "integer", "default": 20},
                        "second_innings_overs": {"type": "integer", "description": "Revised available overs for chasing team"},
                        "wickets_lost": {"type": "integer", "default": 0}
                    },
                    "required": ["first_innings_runs", "second_innings_overs"]
                }
            },
            {
                "name": "simulate_ball_by_ball",
                "description": "Simulates 10,000 matches using a 9-class discrete multinomial delivery model to generate fantasy distributions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {"type": "string", "minLength": 1},
                        "n_sims": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100},
                        "pitch_class": {"type": "string", "enum": ["BALANCED", "FLAT_HIGHWAY", "DRY_TURNER"], "default": "BALANCED"}
                    },
                    "required": ["match_id"]
                }
            },
            {
                "name": "solve_gpp_lineups",
                "description": "Runs uncalibrated CP-SAT fantasy lineup scenarios for a connected fixture.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {"type": "string", "minLength": 1}
                    },
                    "required": ["match_id"]
                }
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an MCP tool call to the internal quantitative module."""
        if name == "list_daily_fixtures":
            force = arguments.get("force_refresh", False)
            matches = self.sync_engine.discover_daily_matches(force_refresh=force)
            return {"fixtures": matches, "count": len(matches)}

        elif name == "deconstruct_pitch_commentary":
            pitch = arguments.get("pitch_report", "")
            toss = arguments.get("toss_quote", "")
            signals = self.nlp.process_pre_match_intel(pitch_report=pitch, toss_quote=toss)
            return signals

        elif name == "query_player_h2h":
            batter = arguments.get("batter", "")
            bowler = arguments.get("bowler", "")
            battle = self.battles.query_h2h_battle(batter, bowler)
            return battle.model_dump() if battle else {"status": "no_prior_matchup", "batter": batter, "bowler": bowler}

        elif name == "calculate_dls_target":
            return self.battles.compute_dls_target(
                first_innings_runs=arguments["first_innings_runs"],
                first_innings_overs=arguments.get("first_innings_overs", 20),
                second_innings_overs=arguments["second_innings_overs"],
                interruption_wickets=arguments.get("wickets_lost", 0)
            )

        elif name == "simulate_ball_by_ball":
            n_sims = arguments.get("n_sims", 100)
            pitch_class = arguments.get("pitch_class", "BALANCED")
            if type(n_sims) is not int or not 1 <= n_sims <= 1000:
                raise ValueError("n_sims must be an integer between 1 and 1000")
            if pitch_class not in {"BALANCED", "FLAT_HIGHWAY", "DRY_TURNER"}:
                raise ValueError("Unknown pitch_class")
            if set(arguments) - {"match_id", "n_sims", "pitch_class"}:
                raise ValueError("Unknown simulation argument; use match_id, n_sims and pitch_class")
            match_id = arguments.get("match_id")
            if not isinstance(match_id, str) or not match_id.strip():
                raise ValueError("Explicit match_id required")
            if match_id not in self.universal._matches:
                raise ValueError("Unknown or disconnected match")
            meta = self.universal._matches[match_id]
            players = self.universal._profile_match_players(meta)
            team_a = [p for p in players if p["team"] == meta["teams"]["home"]["code"]]
            team_b = [p for p in players if p["team"] == meta["teams"]["away"]["code"]]
            if len(team_a) != 11 or len(team_b) != 11:
                raise ValueError("Simulation requires two complete playing XIs")
            sim_results = self.simulator.simulate_match_distribution(
                team_a=team_a, team_b=team_b, n_sims=n_sims, pitch_class=pitch_class)
            return {"num_simulations": n_sims, "pitch_class": pitch_class,
                    "data_provenance": "SIMULATED_UNCALIBRATED", "player_distributions": sim_results}

        elif name == "solve_gpp_lineups":
            match_id = arguments.get("match_id")
            if not isinstance(match_id, str) or not match_id.strip():
                raise ValueError("Explicit match_id required")
            state = self.universal.get_unified_state(match_id)
            return {
                "match": state.get("match"),
                "lineups_count": len(state.get("lineups", [])),
                "lineups": state.get("lineups")
            }

        return {"error": f"Tool '{name}' not found"}

    def handle_stdio_rpc(self):
        """Processes JSON-RPC 2.0 messages from stdio."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                method = request.get("method")
                req_id = request.get("id")

                if method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"tools": self.get_tool_definitions()}
                    }
                elif method == "tools/call":
                    params = request.get("params", {})
                    t_name = params.get("name")
                    t_args = params.get("arguments", {})
                    from contextlib import redirect_stdout
                    with redirect_stdout(sys.stderr):
                        result = self.call_tool(t_name, t_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"status": "ok"}
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if "request" in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = CricketMCPServer()
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        print(json.dumps(server.get_tool_definitions(), indent=2))
    else:
        server.handle_stdio_rpc()
