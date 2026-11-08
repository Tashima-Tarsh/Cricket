"""Predict-11 Unified Master CLI: Cricsheet, CricketData, XGBoost & OR-Tools Engine.
Executes the full pipeline connecting:
1. Cricsheet Historical Match Database
2. CricketData Live API
3. Predict-11 Fantasy Foundation (Dream11 Rules Engine)
4. XGBoost Player Performance & Ceiling Predictor
5. Google OR-Tools Multi-Lineup CP-SAT Optimizer
"""

import sys
import io
import json
from pathlib import Path

# Force UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from gl_engine.cricsheet import CricsheetDatabase
from gl_engine.cricketdata_api import CricketDataClient
from gl_engine.providers import (
    SportmonksCricketClient,
    RoanuzCricketClient,
    RoanuzFantasyClient,
    UnifiedCricketDataHub,
    PROVIDER_METADATA
)
from gl_engine.pitch_venue_vision import PitchVenueVisionEngine
from gl_engine.player_battles_mcp import PlayerBattlesMCPEngine
from gl_engine.datasets_2026 import Datasets2026Pipeline, CricOracle2026
from gl_engine.predict11 import Predict11Foundation, Dream11Rules
from gl_engine.xgboost_model import XGBoostFantasyPredictor
from gl_engine.ortools_optimizer import ORToolsCricketOptimizer
from gl_engine.models import Player, VenueConditions, WeatherReport


console = Console(force_terminal=True, legacy_windows=False)


def run_full_suite():
    console.print(Panel.fit(
        "[bold cyan]🏏 PREDICT-11 FANTASY INTELLIGENCE SUITE[/bold cyan]\n"
        "[dim]Cricsheet Database • CricketData API • Dream11 Rules • XGBoost AI • Google OR-Tools[/dim]",
        border_style="cyan"
    ))

    # =========================================================================
    # 1. CRICSHEET HISTORICAL MATCH DATABASE
    # =========================================================================
    console.print("\n[bold yellow]1️⃣  HISTORICAL MATCH DATABASE (Cricsheet)[/bold yellow]")
    db = CricsheetDatabase()
    matches = db.list_matches()
    if not matches:
        console.print("[dim]Downloading sample Cricsheet dataset...[/dim]")
        db.download_dataset("ipl_json", limit_matches=10)
        matches = db.list_matches()

    console.print(f"✔ Cricsheet match files indexed: [bold green]{len(matches)}[/bold green]")
    if matches:
        sample_m = matches[0]
        parsed = db.parse_match(sample_m["file_path"])
        top_pts_player = sorted(parsed["players"], key=lambda x: x["fantasy_points"], reverse=True)[0]
        
        c_table = Table(title=f"Sample Match: {sample_m['teams'][0]} vs {sample_m['teams'][1]} ({sample_m['date']})", border_style="yellow")
        c_table.add_column("Top Performer", style="bold white")
        c_table.add_column("Team", style="cyan")
        c_table.add_column("Runs (SR)", style="green")
        c_table.add_column("Wickets (Econ)", style="blue")
        c_table.add_column("Dream11 Fantasy Pts", style="bold yellow")
        c_table.add_row(
            top_pts_player["player"],
            top_pts_player["team"],
            f"{top_pts_player['runs']} ({top_pts_player['strike_rate']})",
            f"{top_pts_player['wickets']} ({top_pts_player['economy']})",
            f"{top_pts_player['fantasy_points']} pts"
        )
        console.print(c_table)

    # =========================================================================
    # 2. MULTI-PROVIDER LIVE CRICKET DATA HUB
    # =========================================================================
    console.print("\n[bold magenta]2️⃣  LIVE CRICKET DATA PROVIDERS & APIS[/bold magenta]")
    hub = UnifiedCricketDataHub()
    prov_status = hub.get_providers_status()

    prov_table = Table(title="Integrated Cricket Data Providers: Endpoints & Best Use", border_style="magenta")
    prov_table.add_column("Provider", style="bold white")
    prov_table.add_column("Documentation / Endpoint", style="cyan")
    prov_table.add_column("Best Use Case", style="green")
    prov_table.add_column("Runtime Mode", style="bold yellow")

    for k, info in prov_status.items():
        meta = info["info"]
        mode = info.get("mode", f"{info.get('matches_cached', 0)} files cached")
        prov_table.add_row(
            meta["name"],
            f"{meta['documentation']}\n[dim]{', '.join(meta['endpoints'][:2])}[/dim]",
            meta["best_use"],
            mode
        )
    console.print(prov_table)

    # Demonstrate unified multi-provider cross-reference
    unified_live = hub.fetch_unified_live_match("ind-vs-wi-t20i-2026")
    console.print(f"✔ Cross-Referenced Live Match: [bold green]{unified_live['match_id']}[/bold green]")
    console.print(f"   • Toss ([dim]{unified_live['toss']['won'].upper()}[/dim]): [italic]{unified_live['toss']['str']}[/italic]")
    console.print(f"   • Verified Lineup via [bold cyan]{unified_live['lineup_source']}[/bold cyan]: {len(unified_live['lineup']['playing_xi']['home'])} home + {len(unified_live['lineup']['playing_xi']['away'])} away")
    console.print(f"   • Real-Time Fantasy Scoring via [bold yellow]{unified_live['fantasy_scoring_source']}[/bold yellow]: {len(unified_live['live_fantasy_points']['points'])} player live feeds active")

    # =========================================================================
    # 3. PITCH & VENUE VISION INTELLIGENCE (Hawkeye, Degradation & Boundaries)
    # =========================================================================
    console.print("\n[bold cyan]3️⃣  PITCH & VENUE VISION (Hawkeye Lengths, Pitch Degradation, Boundaries)[/bold cyan]")
    pv_engine = PitchVenueVisionEngine()
    hawkeye_pace = pv_engine.analyze_hawkeye_lengths("Pace")
    deg_info = pv_engine.evaluate_pitch_degradation(current_over=12.0, innings=2)
    b_zones = pv_engine.compute_boundary_risk_zones()

    pv_table = Table(title=f"Hawkeye Length Clusters: {pv_engine.pitch.name}", border_style="cyan")
    pv_table.add_column("Delivery Length", style="bold white")
    pv_table.add_column("Usage %", style="yellow")
    pv_table.add_column("Wicket Rate", style="bold red")
    pv_table.add_column("Economy", style="green")

    for length_name, metrics in list(hawkeye_pace["length_breakdown"].items())[:4]:
        pv_table.add_row(length_name, f"{metrics['usage_pct']}%", f"{metrics['wicket_rate']*100:.1f}%", f"{metrics['economy']:.1f}")
    console.print(pv_table)
    console.print(f"✔ Shortest Boundary: [bold yellow]{b_zones['shortest_boundary'][0].replace('_', ' ').title()}[/bold yellow] ({b_zones['shortest_boundary'][1]}m) | Dew Active: [bold cyan]{deg_info['dew_active']}[/bold cyan] ({deg_info['dew_severity_pct']}% severity)")

    # =========================================================================
    # 4. PLAYER BATTLES, ADVANCED MATCHUPS & MODEL CONTEXT PROTOCOL (MCP)
    # =========================================================================
    console.print("\n[bold magenta]4️⃣  PLAYER BATTLES, DLS & MODEL CONTEXT PROTOCOL (MCP)[/bold magenta]")
    pb_engine = PlayerBattlesMCPEngine()
    sample_h2h = pb_engine.query_h2h_battle("Nicholas Pooran", "Kuldeep Yadav")
    sample_dls = pb_engine.compute_dls_target(first_innings_runs=185, first_innings_overs=20, second_innings_overs=15, interruption_wickets=2)

    h2h_table = Table(title="Key H2H Player Battle (PitchNama / cric-metrics)", border_style="magenta")
    h2h_table.add_column("Batter", style="bold white")
    h2h_table.add_column("Bowler", style="bold cyan")
    h2h_table.add_column("Balls", style="yellow")
    h2h_table.add_column("Runs", style="green")
    h2h_table.add_column("Dismissals", style="bold red")
    h2h_table.add_column("Strike Rate", style="blue")
    h2h_table.add_column("Tactical Advantage", style="bold yellow")
    if sample_h2h:
        h2h_table.add_row(
            sample_h2h.batter_name, sample_h2h.bowler_name,
            str(sample_h2h.balls_faced), str(sample_h2h.runs_scored),
            str(sample_h2h.dismissals), str(sample_h2h.strike_rate),
            sample_h2h.tactical_advantage
        )
    console.print(h2h_table)
    console.print(f"✔ DLS Standard Target: [bold green]{sample_dls['dls_revised_target']} runs[/bold green] in {sample_dls['revised_second_innings_overs']} overs (RRR: {sample_dls['required_run_rate']})")
    console.print(f"✔ MCP Tool Dispatcher: [bold cyan]{len(pb_engine.get_mcp_tool_definitions())} active MCP tool endpoints[/bold cyan] ready for autonomous agent invocations")

    # =========================================================================
    # 5. 2026 MATCH RECORDS, OPENIPL & CRICORACLE LIVE WIN MODELS
    # =========================================================================
    console.print("\n[bold blue]5️⃣  2026 MATCH RECORDS, OPENIPL & CRICORACLE PREDICTIVE MODELS[/bold blue]")
    wpa_result = CricOracle2026.calculate_win_probability(target_runs=185, current_runs=118, balls_remaining=50, wickets_in_hand=8)
    score_proj = CricOracle2026.forecast_final_innings_score(current_runs=118, overs_bowled=11.4, wickets_lost=2)
    console.print(f"✔ CricOracle2026 Win Probability: Chasing Win: [bold green]{wpa_result['chasing_win_prob']*100:.1f}%[/bold green] | Defending Win: [bold red]{wpa_result['defending_win_prob']*100:.1f}%[/bold red]")
    console.print(f"✔ Projected Final Total: [bold yellow]{score_proj['projected']}[/bold yellow] (Confidence Bounds: [dim]{score_proj['floor']} - {score_proj['ceiling']}[/dim])")

    # =========================================================================
    # 6. XGBOOST PLAYER PREDICTION MODEL
    # =========================================================================
    console.print("\n[bold green]6️⃣  PLAYER PREDICTION MODELS (XGBoost)[/bold green]")
    predictor = XGBoostFantasyPredictor()
    if not predictor.is_trained:
        console.print("[dim]Training XGBoost Regressor on Cricsheet ball-by-ball matches...[/dim]")
        metrics = predictor.train_from_cricsheet(db, max_matches=15)
        console.print(f"✔ Model trained. RMSE: [bold green]{metrics['rmse']:.2f}[/bold green], R²: [bold green]{metrics['r2']:.3f}[/bold green]")
    else:
        console.print("✔ Loaded pre-trained XGBoost Fantasy Regressor")

    # Load 22 players for target match
    data_path = Path(__file__).parent / "gl_engine" / "data" / "ind_wi_match.json"
    with open(data_path, "r", encoding="utf-8") as f:
        match_json = json.load(f)

    players = [Player(**p) for p in match_json["players"]]
    venue = VenueConditions(**match_json["match_info"]["venue"])
    weather = WeatherReport(**match_json["match_info"]["weather"])

    xgb_forecasts = []
    for p in players:
        pred = predictor.predict_player(p, venue, weather)
        p.projected_points = pred["mean_points"]
        p.ceiling_score = pred["ceiling_90th"]
        p.floor_score = pred["floor_10th"]
        xgb_forecasts.append({
            "name": p.name,
            "role": p.role,
            "team": p.team,
            "mean": pred["mean_points"],
            "ceiling": pred["ceiling_90th"],
            "floor": pred["floor_10th"],
            "volatility": pred["std_dev"]
        })

    xgb_forecasts.sort(key=lambda x: x["ceiling"], reverse=True)

    xgb_table = Table(title="Top 5 XGBoost Predicted Ceilings (Grand League Levers)", border_style="green")
    xgb_table.add_column("Player", style="bold white")
    xgb_table.add_column("Role / Team", style="cyan")
    xgb_table.add_column("Projected Mean", style="yellow")
    xgb_table.add_column("10th Floor", style="blue")
    xgb_table.add_column("90th Ceiling", style="bold green")
    xgb_table.add_column("Volatility (σ)", style="magenta")

    for f in xgb_forecasts[:5]:
        xgb_table.add_row(
            f["name"], f"{f['role']} ({f['team']})",
            f"{f['mean']:.1f}", f"{f['floor']:.1f}", f"{f['ceiling']:.1f}", f"±{f['volatility']:.1f}"
        )
    console.print(xgb_table)

    # =========================================================================
    # 7. GOOGLE OR-TOOLS MULTI-LINEUP OPTIMIZER
    # =========================================================================
    console.print("\n[bold blue]7️⃣  MULTIPLE FANTASY LINEUP OPTIMIZER (Google OR-Tools CP-SAT)[/bold blue]")
    optimizer = ORToolsCricketOptimizer(players)
    lineups = optimizer.generate_grand_league_portfolio(
        num_teams=5,
        min_differentials_per_team=2,
        max_overlap_between_teams=8
    )
    console.print(f"✔ Generated [bold green]{len(lineups)}[/bold green] mathematically optimized Grand League lineups")

    ortools_table = Table(title="Google OR-Tools Grand League Portfolios", border_style="blue")
    ortools_table.add_column("Lineup", style="bold white")
    ortools_table.add_column("Captain (2x)", style="bold yellow")
    ortools_table.add_column("Vice-Captain (1.5x)", style="bold cyan")
    ortools_table.add_column("Credits", style="white")
    ortools_table.add_column("Proj Pts", style="green")
    ortools_table.add_column("90th Ceiling", style="bold magenta")
    ortools_table.add_column("Diffs (<35%)", style="blue")

    for idx, l in enumerate(lineups):
        ortools_table.add_row(
            f"T{idx+1}: {l.scenario_tag}",
            f"{l.captain.name} ({l.captain.team})",
            f"{l.vice_captain.name} ({l.vice_captain.team})",
            f"{l.total_credits:.1f}/100",
            f"{l.projected_points:.1f}",
            f"{l.simulated_ceiling:.1f}",
            f"{l.differential_count} picks"
        )
    console.print(ortools_table)

    # =========================================================================
    # 8. PREDICT-11 FANTASY FOUNDATION VALIDATION & EXPORT
    # =========================================================================
    console.print("\n[bold red]8️⃣  FANTASY APPLICATION FOUNDATION (Predict-11 / Dream11 Rules)[/bold red]")
    app = Predict11Foundation()
    
    # Validate each generated lineup
    all_valid = True
    for idx, l in enumerate(lineups):
        lineup_dicts = [p.model_dump() for p in l.players]
        res = app.validate_lineup(lineup_dicts, l.captain.id, l.vice_captain.id)
        if not res.is_valid:
            console.print(f"[red]Lineup {idx+1} Validation Failed: {res.errors}[/red]")
            all_valid = False
    
    if all_valid:
        console.print("✔ [bold green]All 5 Lineups Validated 100% Legal under Dream11 Roster & Salary Constraints![/bold green]")

    # Export to CSV
    export_csv = "predict11_ortools_lineups.csv"
    app.export_lineups_to_csv([l.model_dump() for l in lineups], export_csv)
    console.print(f"✔ Lineups exported to Dream11-compliant CSV: [bold underline]{export_csv}[/bold underline]")

    # Diversity Matrix
    overlap_df = app.compute_portfolio_overlap([l.model_dump() for l in lineups])
    console.print("\n[bold]Pairwise Lineup Overlap Matrix (Max overlap enforced <= 8):[/bold]")
    console.print(overlap_df)

    console.print(Panel(
        "[bold green]✨ COMPLETE PRODUCTION FANTASY CRICKET INTELLIGENCE PLATFORM ✨[/bold green]\n"
        "1. Cricsheet: Free historical ball-by-ball matches & Dream11 points\n"
        "2. CricketData / Sportmonks / Roanuz: 5-provider live data hub with real-time scoring\n"
        "3. Pitch & Venue Vision: Hawkeye lengths, pitch wear degradation, boundary risk\n"
        "4. Player Battles & MCP: Batter vs bowler matchups, DLS targets, and MCP tool protocols\n"
        "5. 2026 Datasets: OpenIPL telemetry & CricOracle live win probability model\n"
        "6. XGBoost AI: Multi-variate fantasy points & 90th percentile ceiling predictor\n"
        "7. Google OR-Tools: Exact CP-SAT optimizer generating diverse, constrained Grand League teams\n"
        "8. Predict-11 Foundation: Official Dream11 rules engine, lineup validator, and CSV exporter",
        border_style="green"
    ))


if __name__ == "__main__":
    run_full_suite()
