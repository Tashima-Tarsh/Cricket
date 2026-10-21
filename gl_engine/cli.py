"""Command-line interface with rich visuals for the Grand League Engine."""
import argparse
import sys
import os

# Fix Windows console UTF-8 encoding for Rich
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
except ImportError:
    import re
    class Console:
        def __init__(self, *args, **kwargs): pass
        def print(self, *args, **kwargs):
            for a in args:
                if hasattr(a, 'render'):
                    print(a.render())
                elif isinstance(a, str):
                    print(re.sub(r'\[/?[a-zA-Z0-9_\s#]+\]', '', a))
                else:
                    print(a)
    class Panel:
        def __init__(self, content, *args, **kwargs):
            self.content = content
        def render(self):
            clean = re.sub(r'\[/?[a-zA-Z0-9_\s#]+\]', '', str(self.content))
            return f"\n{'='*70}\n{clean}\n{'='*70}\n"
        @classmethod
        def fit(cls, content, *args, **kwargs):
            return cls(content)
    class Table:
        def __init__(self, *args, **kwargs):
            self.cols = []
            self.rows = []
        def add_column(self, name, *args, **kwargs):
            self.cols.append(name)
        def add_row(self, *args, **kwargs):
            self.rows.append([str(a) for a in args])
        def render(self):
            lines = [" | ".join(self.cols), "-" * 70]
            for r in self.rows:
                lines.append(" | ".join([re.sub(r'\[/?[a-zA-Z0-9_\s#]+\]', '', c) for c in r]))
            return "\n".join(lines)
    class Text:
        pass
    class box:
        ROUNDED = None

from .pipeline import GrandLeaguePipeline
from .live_feed import fetch_espn_cricinfo_live_matches
from .predict11 import Predict11Foundation

console = Console(force_terminal=True)

def run_cli():
    parser = argparse.ArgumentParser(description="20-Capability Grand League Cricket Intelligence & Dream11 Optimizer")
    parser.add_argument("--list", action="store_true", help="List all real live and upcoming cricket matches today from live feeds")
    parser.add_argument("--live", type=str, default=None, help="Select a live match by index number or name (e.g. --live 1 or --live 'Canada')")
    parser.add_argument("--match", type=str, default=None, help="Analyze a specific match by query (e.g. --match 'IND vs WI')")
    parser.add_argument("--teams", type=int, default=5, help="Number of Grand League teams to generate (default: 5, up to 10)")
    parser.add_argument("--sims", type=int, default=2000, help="Number of Monte Carlo simulations (default: 2000)")
    parser.add_argument("--csv", type=str, default="predict11_ortools_lineups.csv", help="CSV export destination for Dream11")
    parser.add_argument("--export", type=str, default="gl_report.json", help="File path to save results JSON")
    parser.add_argument("--watch", "--daemon", action="store_true", dest="watch", help="Start the autonomous pre-match watcher daemon")
    parser.add_argument("--mcp", action="store_true", help="Start the Model Context Protocol (MCP) server")
    parser.add_argument("--inject", action="store_true", help="Generate 1-click browser console injector snippet for Dream11")
    parser.add_argument("--sync", action="store_true", help="Discover and sync all daily matches worldwide")
    parser.add_argument("--portal", "--web", action="store_true", dest="portal", help="Launch the live dynamic working portal on http://127.0.0.1:8000/portal")
    args = parser.parse_args()

    # Live Portal Mode
    if args.portal:
        import uvicorn
        import webbrowser
        console.print(Panel.fit(
            "[bold cyan]⚡ STRIKE//OS PRO - LIVE DYNAMIC WORKING PORTAL[/bold cyan]\n"
            "[bold green]Serving portal at: http://127.0.0.1:8000/portal[/bold green]\n"
            "[dim]Live Match Selector • 4 Archetypes • 3 Invariable Laws • 1-Click Dream11 Injector[/dim]",
            border_style="cyan"
        ))
        try:
            webbrowser.open("http://127.0.0.1:8000/portal")
        except Exception:
            pass
        uvicorn.run("gl_engine.web_app:app", host="127.0.0.1", port=8000, reload=False)
        return

    # MCP Server Mode
    if args.mcp:
        from .mcp_server import CricketMCPServer
        server = CricketMCPServer()
        server.handle_stdio_rpc()
        return

    # Watcher Daemon Mode
    if args.watch:
        from .daemon_watcher import MatchWatcherDaemon
        console.print(Panel.fit(
            "[bold green]🤖 STRIKE//OS PRO - AUTONOMOUS DAEMON WATCHER ACTIVATED[/bold green]\n"
            "[dim]Monitoring fixtures worldwide | Auto-locking portfolios at T-30m[/dim]",
            border_style="green"
        ))
        daemon = MatchWatcherDaemon(poll_interval_sec=60)
        daemon.start_daemon()
        return

    # 1-Click Browser Injector Mode
    if args.inject:
        from .universal_engine import get_universal_engine
        from .browser_injector import BrowserLineupInjector
        engine = get_universal_engine()
        state = engine.get_unified_state("ind_w_vs_zim_w_2026_03")
        injector = BrowserLineupInjector(state.get("lineups", []))
        js_code = injector.generate_browser_console_script(0)
        console.print(Panel.fit(
            "[bold cyan]⚡ 1-CLICK BROWSER LINEUP INJECTOR GENERATED[/bold cyan]\n"
            "[dim]Paste the code below into Chrome/Edge DevTools Console on Dream11 to auto-fill Team 1[/dim]",
            border_style="cyan"
        ))
        console.print(js_code)
        userscript_path = injector.export_tampermonkey_userscript()
        console.print(f"[bold green]✔ Tampermonkey Userscript exported to: {userscript_path}[/bold green]\n")
        return

    # Daily Match Sync Mode
    if args.sync:
        from .daily_match_sync import get_daily_match_sync_engine
        sync_engine = get_daily_match_sync_engine()
        matches = sync_engine.discover_daily_matches(force_refresh=True)
        console.print(Panel.fit(
            f"[bold magenta]🌍 SYNCED {len(matches)} DAILY MATCHES WORLDWIDE[/bold magenta]",
            border_style="magenta"
        ))
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Match ID", style="yellow")
        table.add_column("Title", style="bold white")
        table.add_column("Format", style="cyan")
        table.add_column("AI Archetype", style="magenta")
        table.add_column("Status", style="green")
        for m in matches[:12]:
            table.add_row(m.get("match_id", ""), m.get("title", ""), m.get("format", ""), m.get("ai_archetype", ""), m.get("status", ""))
        console.print(table)
        return

    # 1. Handle --list flag: Show all live and upcoming matches today
    if args.list:
        console.print(Panel.fit(
            "[bold cyan]📡 REAL-TIME CRICKET FEEDS: LIVE & UPCOMING MATCHES TODAY[/bold cyan]\n"
            "[dim]Direct Feed: ESPN Cricinfo & Cricbuzz Telemetry Engine[/dim]",
            border_style="cyan"
        ))
        matches = fetch_espn_cricinfo_live_matches()
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("#", style="bold yellow", width=4)
        table.add_column("Match / Fixture", style="bold white")
        table.add_column("Live Score", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Live Telemetry & Pitch", style="dim")

        for idx, m in enumerate(matches, 1):
            status_style = "green" if "LIVE" in m["status"] else "yellow"
            score_str = f"{m.get('score_home', '')} {m.get('score_away', '')}".strip() or "Pre-Match"
            table.add_row(
                str(idx),
                m["title"],
                score_str,
                f"[{status_style}]{m['status']}[/{status_style}]",
                m.get("details", "")[:60] + "..." if len(m.get("details", "")) > 60 else m.get("details", "")
            )
        console.print(table)
        console.print("\n[bold green]💡 To run true Grand League analytics & Dream11 optimization for any match above:[/bold green]")
        console.print("   [bold yellow]python run_gl.py --live 1[/bold yellow]  (or replace 1 with match number)")
        console.print("   [bold yellow]python run_gl.py --match \"India vs West Indies\" --teams 5[/bold yellow]\n")
        return

    # Check for live match selection
    selected_match_title = "India vs West Indies (T20I)"
    if args.live:
        matches = fetch_espn_cricinfo_live_matches()
        target_match = None
        if args.live.isdigit():
            idx = int(args.live) - 1
            if 0 <= idx < len(matches):
                target_match = matches[idx]
        else:
            query = args.live.lower()
            for m in matches:
                if query in m["title"].lower() or query in m["team_home"].lower() or query in m["team_away"].lower():
                    target_match = m
                    break
        if target_match:
            selected_match_title = f"{target_match['title']} [{target_match['status']}]"
            console.print(f"[bold green]✔ Synchronized with Live Feed:[/bold green] [bold cyan]{target_match['title']}[/bold cyan]")
            if target_match.get("score_home") or target_match.get("score_away"):
                console.print(f"  [dim]Score:[/dim] {target_match.get('score_home', '')} {target_match.get('score_away', '')} | [dim]Details:[/dim] {target_match.get('details', '')}")
    elif args.match:
        selected_match_title = args.match

    console.print(Panel.fit(
        "[bold cyan]🏏 20-CAPABILITY GRAND LEAGUE CRICKET INTELLIGENCE ENGINE[/bold cyan]\n"
        f"[bold yellow]Active Match: {selected_match_title}[/bold yellow]\n"
        "[dim]Monte Carlo Simulation • H2H Matchups • Dew/Pitch Modeling • Google OR-Tools CP-SAT Optimizer[/dim]",
        border_style="cyan"
    ))

    with console.status("[bold green]Executing 20 Analytical & Strategic Capabilities...[/bold green]", spinner="dots"):
        pipeline = GrandLeaguePipeline()
        result = pipeline.run_all_capabilities(num_teams=args.teams, sim_iterations=args.sims)

    caps = result["capabilities"]
    fixture = caps["c01_fixture_research"]
    pitch = caps["c04_pitch_intelligence"]
    weather = caps["c05_weather_analysis"]
    toss = caps["c03_toss_analysis"]

    # 1. Match & Venue Conditions Panel
    env_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    env_table.add_column("Parameter", style="cyan")
    env_table.add_column("Value / Intelligence", style="white")
    env_table.add_row("Venue & Series", f"{fixture['venue_name']} | {fixture['series']}")
    env_table.add_row("Pitch Nature", pitch["surface_profile"])
    env_table.add_row("Pace vs Spin Dismissals", f"Pace: {pitch['pace_vs_spin_wickets']['pace_pct']}% | Spin: {pitch['pace_vs_spin_wickets']['spin_pct']}% (Ratio: {pitch['pace_vs_spin_wickets']['ratio']}x)")
    env_table.add_row("Dew Factor & Weather", f"Humidity {weather['humidity_pct']}% | Dew Risk: {weather['dew_risk_level']} (Multiplier: {toss['dew_multiplier_second_innings']}x)")
    env_table.add_row("Toss Impact", toss["recommended_strategy"])
    console.print(env_table)

    # 2. Key Matchup Levers
    matchups = caps["c07_batter_matchups"]
    m_table = Table(title="⚔️ Critical Batter vs Bowler Matchups", box=box.ROUNDED, header_style="bold yellow")
    m_table.add_column("Type", style="bold")
    m_table.add_column("Batter", style="cyan")
    m_table.add_column("Bowler", style="red")
    m_table.add_column("H2H Numbers", style="green")
    m_table.add_column("Tactical Significance", style="white")
    
    for adv in matchups["key_batter_advantages"][:3]:
        m_table.add_row("🔥 Domination", adv["batter"], adv["exploited_bowler"], f"SR: {adv['strike_rate']} ({adv['runs']} runs, {adv['balls']} balls)", adv["tactical_note"])
    for d in matchups["key_danger_zones"][:3]:
        m_table.add_row("⚠️ Danger Zone", d["batter"], d["nemesis_bowler"], f"{d['dismissals']} dismissals in {d['balls']} balls (SR {d['strike_rate']})", d["tactical_note"])
    console.print(m_table)

    # 3. Top Differentials (<35% Ownership)
    diffs = caps["c14_differential_finder"]
    diff_table = Table(title="💎 High-Leverage Grand League Differentials (< 35% Ownership)", box=box.ROUNDED, header_style="bold green")
    diff_table.add_column("Player", style="cyan")
    diff_table.add_column("Team", style="bold")
    diff_table.add_column("Role", style="magenta")
    diff_table.add_column("Ownership %", style="yellow")
    diff_table.add_column("Ceiling Pts", style="bold green")
    diff_table.add_column("Path to Ceiling", style="white")

    for d in diffs["top_differential_picks"]:
        diff_table.add_row(d["name"], d["team"], d["role"], f"{d['ownership_pct']}%", str(d["ceiling_score"]), d["path_to_ceiling"])
    console.print(diff_table)

    # 4. Monte Carlo Dream Team Probability Rankings
    sim_data = caps["c16_grand_league_simulator"]
    sim_table = Table(title=f"🎲 Monte Carlo Simulation ({sim_data['iterations']} iterations) - Dream Team Probability", box=box.ROUNDED, header_style="bold blue")
    sim_table.add_column("Rank", style="dim")
    sim_table.add_column("Player", style="cyan")
    sim_table.add_column("Team", style="bold")
    sim_table.add_column("Sim Mean", style="white")
    sim_table.add_column("P95 Ceiling", style="bold green")
    sim_table.add_column("Dream Team App %", style="bold yellow")

    for idx, p in enumerate(sim_data["top_dream_team_probabilities"], 1):
        sim_table.add_row(str(idx), p["name"], p["team"], str(p["simulated_mean"]), str(p["p95_elite_ceiling"]), f"{p['dream_team_appearance_pct']}%")
    console.print(sim_table)

    # 5. Generated Grand League Teams
    lineups = result["lineups"]
    opp_evals = {e["team_name"]: e for e in caps["c18_opponent_simulator"]["lineup_evaluations"]}

    for idx, l in enumerate(lineups, 1):
        opp = opp_evals.get(l.team_name, {})
        team_panel = Panel(
            f"[bold yellow]{l.team_name}[/bold yellow]\n"
            f"[dim]Scenario:[/dim] [cyan]{l.scenario_tag}[/cyan] | "
            f"[dim]Credits:[/dim] [green]{l.total_credits}/100[/green] | "
            f"[dim]Balance:[/dim] IND: {l.team_balance.get('IND')} / WI: {l.team_balance.get('WI')} | "
            f"[dim]Differentials:[/dim] {l.differential_count} players | "
            f"[dim]Uniqueness:[/dim] {opp.get('uniqueness_rating', '⭐️⭐️⭐️⭐️')}\n\n"
            f"[bold red]👑 CAPTAIN (2x):[/bold red] [bold yellow]{l.captain.name}[/bold yellow] ({l.captain.team} - {l.captain.role})\n"
            f"[bold blue]⚡ VICE-CAPTAIN (1.5x):[/bold blue] [bold cyan]{l.vice_captain.name}[/bold cyan] ({l.vice_captain.team} - {l.vice_captain.role})\n\n"
            f"[bold]XI Players:[/bold]\n" +
            " • " + "\n • ".join(
                f"[bold cyan]{p.name}[/bold cyan] ({p.team} | {p.role} | {p.credits} cr | Own: {p.projected_ownership}%)" +
                (" [bold red][C][/bold red]" if p.id == l.captain.id else "") +
                (" [bold blue][VC][/bold blue]" if p.id == l.vice_captain.id else "") +
                (" [dim green][DIFF][/dim green]" if p.projected_ownership <= 35.0 else "")
                for p in l.players
            ) + f"\n\n[bold italic magenta]Tactical Thesis:[/bold italic magenta] {l.tactical_rationale}\n"
            f"[dim]Duplication Risk:[/dim] {opp.get('duplication_risk_level', 'Low')} (Projected Field Duplicates: {opp.get('expected_duplicates_in_1M_field', 0)})",
            title=f"🏆 GRAND LEAGUE LINEUP #{idx}",
            border_style="green" if idx == 1 else "blue",
            box=box.ROUNDED
        )
        console.print(team_panel)

    # 6. Backtesting & Citations Summary
    backtest = caps["c19_backtesting"]
    analyst = caps["c20_ai_analyst"]
    console.print(Panel(
        f"[bold]Backtesting Historical Portfolio Efficiency:[/bold] [green]{backtest['average_portfolio_efficiency_vs_dream_team']}[/green] vs true winning Dream Teams\n"
        f"[bold]AI Analyst Citations:[/bold]\n" +
        "\n".join(f" - [bold]{c['source']}:[/bold] {c['finding']}" for c in analyst["tactical_citations"]),
        title="📚 Validation & Tactical Source Citations",
        border_style="magenta",
        box=box.ROUNDED
    ))

    if args.csv:
        pred_app = Predict11Foundation()
        exported_csv = pred_app.export_lineups_to_csv(lineups, output_path=args.csv)
        console.print(f"[bold green]✔ Official Dream11-compliant CSV exported to:[/bold green] [bold cyan]{exported_csv}[/bold cyan]")

    if args.export:
        import json
        with open(args.export, "w", encoding="utf-8") as f:
            export_obj = {
                "match": result["match"],
                "capabilities": {k: (v if not hasattr(v, "model_dump") else v.model_dump()) for k, v in caps.items()},
                "lineups": [l.model_dump() for l in lineups]
            }
            json.dump(export_obj, f, indent=2)
        console.print(f"[bold green]Exported full Grand League analysis to {args.export}[/bold green]")

if __name__ == "__main__":
    run_cli()
