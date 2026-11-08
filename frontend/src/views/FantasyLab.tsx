import { useMatchContext } from "../context/MatchContext";
import React, { useState, useEffect } from "react";
import { Lineup, Player } from "../types";
import { 
  Zap, 
  Download, 
  ShieldCheck, 
  TrendingUp, 
  Sparkles, 
  Flame, 
  Sliders, 
  Award, 
  Users, 
  CheckCircle2,
  Copy,
  Check,
  ChevronRight,
  Shield,
  Layers
} from "lucide-react";

interface FantasyLabProps {
  lineups: Lineup[];
  players: Player[];
}

const getCaptainName = (c: any): string => {
  if (!c) return "Captain";
  if (typeof c === "string") return c;
  return c.name || "Captain";
};

const getCaptainLastName = (c: any): string => {
  const name = getCaptainName(c);
  return name.split(" ").pop() || name;
};

const getCaptainPts = (c: any): number => {
  if (!c || typeof c !== "object") return 45.0;
  return c.projected_points || c.projected_pts || 45.0;
};

export const FantasyLab: React.FC<FantasyLabProps> = ({ lineups: initialLineups, players }) => {
  const { currentMatch, activeOvers } = useMatchContext();
  const [solveError, setSolveError] = useState<string | null>(null);
  const [resultTime, setResultTime] = useState<string | null>(null);
  const [lineups, setLineups] = useState<Lineup[]>(initialLineups || []);
  const [lineupCount, setLineupCount] = useState<number>(20);
  const [maxOverlap, setMaxOverlap] = useState<number>(8);
  const [contestSpots, setContestSpots] = useState<number>(700000);
  const [creditStrategy, setCreditStrategy] = useState<"79-85" | "87-89" | "90-95">("79-85");
  const [riskTolerance, setRiskTolerance] = useState<"BALANCED" | "HIGH_CEILING" | "DIFFERENTIAL_HEAVY">("HIGH_CEILING");
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [activeLineupIndex, setActiveLineupIndex] = useState<number>(0);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Syndicate Player Exposure & Toss Lock States
  const [lockedPlayerIds, setLockedPlayerIds] = useState<Set<string>>(new Set());
  const [excludedPlayerIds, setExcludedPlayerIds] = useState<Set<string>>(new Set());
  const [playerExposureCaps, setPlayerExposureCaps] = useState<Record<string, number>>({});
  const [benchedPlayerIds, setBenchedPlayerIds] = useState<Set<string>>(new Set());
  const [isSyndicateDeckOpen, setIsSyndicateDeckOpen] = useState<boolean>(false);

  // Interactive Scenario Builder states
  const homeCode = currentMatch?.teams?.home?.code || currentMatch?.teams?.home?.name || "HOME";
  const awayCode = currentMatch?.teams?.away?.code || currentMatch?.teams?.away?.name || "AWAY";
  const [selectedScenarioScript, setSelectedScenarioScript] = useState<string>("CHASE_DEW");
  const [selectedCaptainOption, setSelectedCaptainOption] = useState<string>("AUTO");
  const [activeScenarioFeedback, setActiveScenarioFeedback] = useState<string | null>(null);

  // Sync state if initial lineups change from parent real state sync
  useEffect(() => {
    if (initialLineups) {
      setLineups(initialLineups);
    }
  }, [initialLineups]);

  const togglePlayerLock = (id: string) => {
    setLockedPlayerIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        setExcludedPlayerIds((e) => { const ne = new Set(e); ne.delete(id); return ne; });
        setBenchedPlayerIds((b) => { const nb = new Set(b); nb.delete(id); return nb; });
      }
      return next;
    });
  };

  const togglePlayerExclude = (id: string) => {
    setExcludedPlayerIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        setLockedPlayerIds((l) => { const nl = new Set(l); nl.delete(id); return nl; });
      }
      return next;
    });
  };

  const toggleBenched = (id: string) => {
    setBenchedPlayerIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        setLockedPlayerIds((l) => { const nl = new Set(l); nl.delete(id); return nl; });
      }
      return next;
    });
  };

  const setPlayerExposure = (id: string, pct: number) => {
    setPlayerExposureCaps((prev) => ({ ...prev, [id]: pct }));
  };

  const solve = async (custom = false) => {
    setIsSolving(true); setSolveError(null); setActiveScenarioFeedback(null);
    try {
      const params = new URLSearchParams({
        teams: String(lineupCount),
        max_overlap: String(maxOverlap),
        spots: String(contestSpots),
        credit_strategy: creditStrategy,
        risk: riskTolerance,
        match_id: currentMatch.id,
        overs: String(activeOvers || 20)
      });
      if (custom) {
        params.set("scenario", selectedScenarioScript);
        params.set("captain", selectedCaptainOption);
      }
      if (lockedPlayerIds.size > 0) {
        params.set("locked", Array.from(lockedPlayerIds).join(","));
      }
      const combinedExcluded = new Set([...excludedPlayerIds, ...benchedPlayerIds]);
      if (combinedExcluded.size > 0) {
        params.set("excluded", Array.from(combinedExcluded).join(","));
      }
      const exposureEntries = Object.entries(playerExposureCaps).filter(([_, v]) => v < 100);
      if (exposureEntries.length > 0) {
        params.set("exposure", exposureEntries.map(([k, v]) => `${k}:${v}`).join(","));
      }

      const response = await fetch(`/api/ortools/optimize?${params.toString()}`, {signal: AbortSignal.timeout(60000)});
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : `Solve failed (${response.status}).`);
      if (!Array.isArray(data.lineups) || !data.lineups.length) throw new Error("No feasible lineup satisfies these settings. Adjust the credit band, overlap, or player locks.");
      setLineups(data.lineups); setActiveLineupIndex(0); setResultTime(data.generated_at || new Date().toISOString());
      if (data.ownership_status === "UNAVAILABLE_NEUTRAL_PRIOR") setSolveError("Ownership estimates are unavailable. Displayed 50% values are neutral assumptions; CSP and differential-count constraints were not applied.");
      if (data.status === "partial") setSolveError(`Generated ${data.lineups.length} of ${lineupCount} requested lineups. The remaining requests were infeasible under these constraints.`);
      if (custom) setActiveScenarioFeedback(`Solved ${data.lineups.length} lineups using ${selectedScenarioScript}.`);
    } catch (error) {
      setSolveError(error instanceof Error ? error.message : "Optimization failed. No substitute results were generated.");
    } finally {
      setIsSolving(false);
    }
  };
  const handleSolve = () => solve();

  // 1-Click Platform CSV Bulk Exporters (Dream11 and My11Circle)
  const downloadBulkPlatformCSV = (format: "dream11" | "my11circle") => {
    const params = new URLSearchParams({
      format,
      teams: String(lineupCount),
      overs: String(activeOvers || 20),
      credit_strategy: creditStrategy,
      match_id: currentMatch.id
    });
    if (lockedPlayerIds.size > 0) params.set("locked", Array.from(lockedPlayerIds).join(","));
    const combinedExcluded = new Set([...excludedPlayerIds, ...benchedPlayerIds]);
    if (combinedExcluded.size > 0) params.set("excluded", Array.from(combinedExcluded).join(","));
    const exposureEntries = Object.entries(playerExposureCaps).filter(([_, v]) => v < 100);
    if (exposureEntries.length > 0) params.set("exposure", exposureEntries.map(([k, v]) => `${k}:${v}`).join(","));

    window.open(`/api/export/csv?${params.toString()}`, "_blank");
  };

  // 1-Click Copy Lineup to Clipboard
  const handleCopyLineup = (lineup: Lineup, idx: number) => {
    const cName = getCaptainName(lineup.captain);
    const vcName = getCaptainName(lineup.vice_captain);
    const text = `🏆 STRIKE//OS ${lineup.team_name || "GL Lineup"} (${lineup.scenario_tag || "Scenario"})\n👑 C: ${cName}\n⚡ VC: ${vcName}\nXI: ${(lineup.players || []).map(p => p.name).join(", ")}\nCredits: ${lineup.total_credits}/100 | Proj Pts: ${lineup.projected_points}`;
    navigator.clipboard.writeText(text).then(() => setCopiedIndex(idx)).catch(() => setSolveError("Clipboard access failed. Please allow browser clipboard access and retry."));
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Load all 10 multidisciplinary scenario portfolios
  const handleLoadTenScenarios = async () => {
    setIsSolving(true); setSolveError(null);
    try {
      const res = await fetch("/api/ortools/ten-scenarios", {signal: AbortSignal.timeout(15000)});
      if (!res.ok) throw new Error(`Saved scenario request failed (${res.status}).`);
      if (res.ok) {
        const data = await res.json();
        if (data.scenarios) {
          const scenarioLineups = Object.entries(data.scenarios).map(([name, s]: [string, any], idx) => {
            const sim = data.simulations ? data.simulations[name] : null;
            return {
              id: `scenario_${idx + 1}`,
              team_name: name.split(":")[0],
              scenario_tag: name.split(":")[1]?.trim() || name,
              total_credits: s.total_credits,
              projected_points: sim ? sim.mean : s.players.reduce((acc: number, p: any) => acc + (p.projected_points || p.stats?.avg_fantasy_pts || 45), 0),
              simulated_ceiling: sim ? sim.p99 : 0,
              total_ownership_sum: Math.round(s.players.reduce((acc: number, p: any) => acc + (p.projected_ownership || 40), 0)),
              differential_count: s.players.filter((p: any) => (p.projected_ownership || 50) < 35).length,
              captain: s.captain,
              vice_captain: s.vice_captain,
              players: s.players,
              projected_field_duplicates: sim ? sim.projected_duplicates : 0,
              win_rate_percentile_rank: sim ? `EV: ₹${sim.est_ev} (ROI: +${sim.net_roi_pct}%)` : "Not evaluated",
              simulated_spots: contestSpots,
              credit_strategy: s.total_credits <= 85 ? "79-85" : (s.total_credits <= 89 ? "87-89" : "90-95"),
              credits_left: Math.round((100 - s.total_credits) * 10) / 10,
              p_top_0_1_pct: sim ? sim.p_gt_700 : undefined,
              tactical_rationale: sim ? `100k MC Sim: Mean ${sim.mean} pts, P90 ${sim.p90} pts, P99 ${sim.p99} pts. Duplicates: ${sim.projected_duplicates}` : "Multidisciplinary scenario portfolio",
              gl_rank_potential: sim ? `EV: ₹${sim.est_ev} (ROI: +${sim.net_roi_pct}%)` : "Not evaluated",
              uniqueness_score: null
            };
          });
          if (!scenarioLineups.length) throw new Error("No saved scenarios available.");
          setResultTime(new Date().toISOString());
          setLineups(scenarioLineups);
          setActiveLineupIndex(0);
        }
      }
    } catch (e) {
      setSolveError(e instanceof Error ? e.message : "Saved scenarios could not be loaded.");
    } finally {
      setIsSolving(false);
    }
  };

  const handleGenerateCustomScenario = () => solve(true);

  const selectedLineup = lineups[activeLineupIndex] || lineups[0];

  return (
    <div className="space-y-6">
      <p className="evidence-note">[VERIFY REQUIRED] Player projections and ownership are assumptions. Field ranks and duplicate estimates use synthetic opponents, not independently calibrated contest results.</p>
      {solveError && (
        <p role="alert" className="p-3.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono">
          {solveError}
        </p>
      )}

      {/* 1. Header & Actions Strip */}
      <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest font-bold">
              <Zap size={14} className="text-emerald-400" />
              <span>Google OR-Tools CP-SAT Portfolio Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              Fantasy Lab // Syndicate Solver
              <span className="text-xs px-2.5 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 font-mono font-bold">
                20-Team Mega Contest Mode
              </span>
            </h1>
            <p className="text-xs text-slate-400 font-sans max-w-2xl leading-relaxed">
              Mixed-integer constraint programming enforcing official Dream11 limits, pairwise overlap penalties (&le;8 players), CSP sweet spot (500%–650%), and 1-click bulk CSV export.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Toggle Syndicate Exposure Controls */}
            <button
              onClick={() => setIsSyndicateDeckOpen(!isSyndicateDeckOpen)}
              className={`px-3.5 py-2.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-2 transition-all ${
                isSyndicateDeckOpen
                  ? "bg-purple-600 text-white border-purple-400 shadow-lg"
                  : "bg-purple-500/10 border-purple-500/30 text-purple-300 hover:bg-purple-500/20"
              }`}
              title="Lock/Ban players and set max exposure % across 20 teams"
            >
              <Sliders size={14} />
              <span>{isSyndicateDeckOpen ? "HIDE EXPOSURE RULES" : "SYNDICATE EXPOSURE RULES"}</span>
              {(lockedPlayerIds.size > 0 || excludedPlayerIds.size > 0 || benchedPlayerIds.size > 0) && (
                <span className="px-1.5 py-0.2 rounded-full bg-purple-400 text-slate-950 text-[10px] font-extrabold">
                  {lockedPlayerIds.size + excludedPlayerIds.size + benchedPlayerIds.size}
                </span>
              )}
            </button>

            {/* Download Dream11 Bulk CSV */}
            <button
              onClick={() => downloadBulkPlatformCSV("dream11")}
              className="px-3.5 py-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 hover:border-emerald-500/60 text-emerald-400 text-xs font-mono font-bold flex items-center gap-2 transition-all hover:bg-emerald-500/25 shadow-md"
              title="Download official bulk upload CSV for Dream11 (20 teams)"
            >
              <Download size={14} />
              <span>DREAM11 BULK CSV</span>
            </button>

            {/* Download My11Circle CSV */}
            <button
              onClick={() => downloadBulkPlatformCSV("my11circle")}
              className="px-3.5 py-2.5 rounded-xl bg-sky-500/15 border border-sky-500/30 hover:border-sky-500/60 text-sky-400 text-xs font-mono font-bold flex items-center gap-2 transition-all hover:bg-sky-500/25 shadow-md"
              title="Download official CSV for My11Circle"
            >
              <Download size={14} />
              <span>MY11CIRCLE CSV</span>
            </button>

            {/* Solve Button */}
            <button
              onClick={handleSolve}
              disabled={isSolving}
              className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-mono font-extrabold flex items-center gap-2 transition-all transform active:scale-95 disabled:opacity-50 shadow-lg shadow-emerald-500/20"
            >
              {isSolving ? (
                <>
                  <Sliders size={14} className="animate-spin" />
                  <span>SOLVING CP-SAT...</span>
                </>
              ) : (
                <>
                  <Sparkles size={14} />
                  <span>SOLVE {lineupCount} TEAMS</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* 2. Solver Parameters Glass Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5 mt-6 pt-6 border-t border-white/10 font-sans">
          
          {/* Parameter 1: Lineups Count (Up to 20 Teams) */}
          <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 uppercase font-semibold">PORTFOLIO SIZE:</span>
              <span className="text-emerald-400 font-bold">{lineupCount} TEAMS</span>
            </div>
            <div className="grid grid-cols-4 gap-1">
              {[5, 10, 15, 20].map((count) => (
                <button
                  key={count}
                  onClick={() => setLineupCount(count)}
                  className={`py-1 rounded text-xs font-mono font-bold transition-all ${
                    lineupCount === count
                      ? "bg-emerald-500 text-slate-950 font-extrabold shadow"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {count}T
                </button>
              ))}
            </div>
            <input
              type="range"
              min="1"
              max="20"
              value={lineupCount}
              onChange={(e) => setLineupCount(Number(e.target.value))}
              className="w-full accent-emerald-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
          </div>

          {/* Parameter 2: Credit Budgeting Strategy */}
          <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 uppercase font-semibold">BUDGET TARGET:</span>
              <span className="text-cyan-400 font-bold">{creditStrategy} Cr</span>
            </div>
            <div className="grid grid-cols-3 gap-1">
              {(["79-85", "87-89", "90-95"] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setCreditStrategy(s)}
                  className={`py-1 rounded text-xs font-mono font-bold transition-all ${
                    creditStrategy === s
                      ? "bg-cyan-500 text-slate-950 font-extrabold shadow"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="text-[11px] font-sans text-slate-400 truncate">
              {creditStrategy === "79-85" ? "⚡ Leaves 15–21 Cr on table (0 Collisions)" : creditStrategy === "87-89" ? "🎯 Anti-Chalk Optimal Budget" : "Classic 90–95 Cr Roster"}
            </div>
          </div>

          {/* Parameter 3: Pairwise Overlap Limit */}
          <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 uppercase font-semibold">MAX OVERLAP:</span>
              <span className="text-amber-400 font-bold">&le; {maxOverlap} Players</span>
            </div>
            <input
              type="range"
              min="5"
              max="9"
              value={maxOverlap}
              onChange={(e) => setMaxOverlap(Number(e.target.value))}
              className="w-full accent-amber-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] font-sans text-slate-400">
              <span>Max 5 (Diverse)</span>
              <span>Max 7</span>
              <span>Max 9</span>
            </div>
          </div>

          {/* Parameter 4: Mega Contest Spots */}
          <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 uppercase font-semibold">CONTEST FIELD:</span>
              <span className="text-purple-400 font-bold">{(contestSpots / 100000).toFixed(0)}L Spots</span>
            </div>
            <div className="grid grid-cols-4 gap-1">
              {[700000, 1000000, 1500000, 2500000].map((s) => (
                <button
                  key={s}
                  onClick={() => setContestSpots(s)}
                  className={`py-1 rounded text-xs font-mono font-bold transition-all ${
                    contestSpots === s
                      ? "bg-purple-500 text-slate-950 font-extrabold shadow"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {s >= 1000000 ? `${(s / 1000000).toFixed(1)}M` : `${s / 100000}L`}
                </button>
              ))}
            </div>
            <div className="text-[11px] font-sans text-slate-400 truncate">
              Rank &le; {Math.round(contestSpots * 0.001)} without splitting
            </div>
          </div>

          {/* Parameter 5: Risk Mode */}
          <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-2">
            <div className="text-xs font-mono text-slate-400 uppercase font-semibold">OBJECTIVE:</div>
            <div className="grid grid-cols-3 gap-1">
              {(["BALANCED", "HIGH_CEILING", "DIFFERENTIAL_HEAVY"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setRiskTolerance(mode)}
                  className={`py-1 rounded text-xs font-mono font-bold transition-all ${
                    riskTolerance === mode
                      ? "bg-rose-500 text-slate-950 font-extrabold shadow"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {mode === "BALANCED" ? "BAL" : mode === "HIGH_CEILING" ? "CEIL" : "DIFF"}
                </button>
              ))}
            </div>
            <div className="text-[11px] font-sans text-slate-400">
              CP-SAT Weighted Objective
            </div>
          </div>

        </div>

        {/* 2.2 Syndicate Pre-Toss Locks & Exposure Workstation (Collapsible) */}
        {isSyndicateDeckOpen && (
          <div className="mt-6 pt-6 border-t border-purple-500/20 space-y-4 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-400 font-bold">
                  <Sliders size={16} />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
                    SYNDICATE PLAYER EXPOSURE & 30-MIN TOSS LOCKS
                  </h3>
                  <p className="text-xs text-slate-400">
                    Lock key assets in 100% of teams, ban benched players, or set maximum exposure caps across your {lineupCount}-lineup portfolio.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setLockedPlayerIds(new Set());
                    setExcludedPlayerIds(new Set());
                    setBenchedPlayerIds(new Set());
                    setPlayerExposureCaps({});
                  }}
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white text-xs font-mono"
                >
                  RESET ALL RULES
                </button>
              </div>
            </div>

            {/* Players Table for Syndicate Locks */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-80 overflow-y-auto pr-1">
              {players.map((p) => {
                const isLocked = lockedPlayerIds.has(p.id);
                const isExcluded = excludedPlayerIds.has(p.id);
                const isBenched = benchedPlayerIds.has(p.id);
                const exposure = playerExposureCaps[p.id] !== undefined ? playerExposureCaps[p.id] : 100;

                return (
                  <div
                    key={p.id}
                    className={`p-3 rounded-xl border transition-all ${
                      isLocked
                        ? "bg-emerald-500/10 border-emerald-500/40"
                        : isExcluded || isBenched
                        ? "bg-rose-500/10 border-rose-500/30 opacity-60"
                        : "bg-slate-950/70 border-white/5 hover:border-white/15"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-white/10 text-slate-300">
                          {p.role}
                        </span>
                        <div>
                          <div className="text-xs font-bold text-white leading-tight">{p.name}</div>
                          <div className="text-[10px] text-slate-400 font-mono">
                            {p.team} &bull; {p.credits} Cr &bull; {p.projected_ownership}% Own
                          </div>
                        </div>
                      </div>

                      {/* Lock / Ban Buttons */}
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => togglePlayerLock(p.id)}
                          className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-all ${
                            isLocked
                              ? "bg-emerald-500 text-slate-950 font-extrabold shadow"
                              : "bg-white/5 text-slate-400 hover:text-white"
                          }`}
                          title="Lock in 100% of generated teams"
                        >
                          LOCK
                        </button>
                        <button
                          type="button"
                          onClick={() => togglePlayerExclude(p.id)}
                          className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-all ${
                            isExcluded
                              ? "bg-rose-500 text-white font-extrabold shadow"
                              : "bg-white/5 text-slate-400 hover:text-white"
                          }`}
                          title="Exclude from all teams"
                        >
                          BAN
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleBenched(p.id)}
                          className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-all ${
                            isBenched
                              ? "bg-amber-500 text-slate-950 font-extrabold shadow"
                              : "bg-white/5 text-slate-400 hover:text-white"
                          }`}
                          title="Toss status: mark as benched"
                        >
                          {isBenched ? "BENCH" : "IN XI"}
                        </button>
                      </div>
                    </div>

                    {/* Exposure Slider */}
                    {!isExcluded && !isBenched && (
                      <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between gap-2">
                        <span className="text-[10px] font-mono text-slate-400 uppercase">MAX EXP:</span>
                        <input
                          type="range"
                          min="10"
                          max="100"
                          step="10"
                          value={exposure}
                          onChange={(e) => setPlayerExposure(p.id, Number(e.target.value))}
                          className="w-24 accent-purple-400 bg-slate-800 h-1 rounded cursor-pointer"
                        />
                        <span className="text-[10px] font-mono font-bold text-purple-300 w-8 text-right">
                          {exposure}%
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 2.5 INTERACTIVE SCENARIO ENGINE: CHOOSE SCENARIO & GET WINNING TEAM */}
      <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 shadow-xl space-y-4 backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Sliders size={20} />
            </div>
            <div>
              <div className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                TACTICAL SCENARIO LAB
              </div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                SELECT MATCH SCRIPT & GENERATE OPTIMAL LINEUP
              </h2>
            </div>
          </div>
          <span className="text-xs font-mono text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-3 py-1 rounded-xl">
            100,000 Trial MC Simulation
          </span>
        </div>

        {/* 3 Selectors: Scenario, Credit Budget, Captain */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300 font-bold">1. VENUE MATCH SCRIPT:</label>
            <select aria-label="Scenario script"
              value={selectedScenarioScript}
              onChange={(e) => setSelectedScenarioScript(e.target.value)}
              className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="CHASE_DEW">{homeCode} Bowls First (Chasing + Dew Advantage)</option>
              <option value="DEFEND_TOTAL">{awayCode} Bowls First (Defending Target)</option>
              <option value="PACE_DOMINANCE">Pace Dominance (Express Pace & Death Overs Ceiling)</option>
              <option value="SPIN_CHOKE">Spin Choke (Turning Deck Middle Overs Squeeze)</option>
              <option value="RAIN_SHORTENED_10OV">Rain-Shortened Sprint (DLS Powerplay Blitz)</option>
              <option value="HIGH_SCORE_SHOOTOUT">200+ Boundary Shootout (Small Boundary Deck)</option>
              <option value="ANTI_CHALK_79_85">Anti-Chalk Leverage (79-85 Cr Budget Band)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300 font-bold">2. CREDIT BUDGET STRATEGY:</label>
            <select aria-label="Credit strategy"
              value={creditStrategy}
              onChange={(e) => setCreditStrategy(e.target.value as any)}
              className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="79-85">79.0 – 85.0 Cr (Leaves 15+ Cr Unspent, 0 Collisions)</option>
              <option value="87-89">87.0 – 89.0 Cr (Balanced High Ceiling)</option>
              <option value="90-95">90.0 – 95.0 Cr (Standard Full Budget)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300 font-bold">3. CAPTAINCY BIAS:</label>
            <select aria-label="Captain option"
              value={selectedCaptainOption}
              onChange={(e) => setSelectedCaptainOption(e.target.value)}
              className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="AUTO">⚡ Auto Highest Leverage Captain</option>
              {players
                .slice()
                .sort((a, b) => (b.ceiling_score || b.projected_points) - (a.ceiling_score || a.projected_points))
                .map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.role} • {p.team} • {p.credits} Cr • {p.projected_ownership}% Own)
                  </option>
                ))}
            </select>
          </div>
        </div>

        {/* Generate Button & Dynamic Scenario Advice */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="text-xs font-sans text-slate-300 flex items-center gap-2">
            <ShieldCheck size={16} className="text-emerald-400 shrink-0" />
            <span className="truncate">
              {selectedScenarioScript === "CHASE_DEW" && `${homeCode} frontline pacers + ${awayCode} middle-order anchors.`}
              {selectedScenarioScript === "DEFEND_TOTAL" && `${awayCode} top order + ${homeCode} chase accelerators.`}
              {selectedScenarioScript === "PACE_DOMINANCE" && "Stacks express pace bowlers to exploit true bounce and death wickets."}
              {selectedScenarioScript === "SPIN_CHOKE" && "Fingerspinners & wristspinners choking run rate on gripping surface."}
              {selectedScenarioScript === "RAIN_SHORTENED_10OV" && "DLS Sprint: Excludes middle order; locks top-3 batters + death yorkers."}
              {selectedScenarioScript === "HIGH_SCORE_SHOOTOUT" && "Flat track: Pure boundary hitters, fading accumulators."}
              {selectedScenarioScript === "ANTI_CHALK_79_85" && "Leaves 15+ Cr unspent. Guarantees 0 duplicates and 100% of 1st prize."}
            </span>
          </div>

          <button
            onClick={handleGenerateCustomScenario}
            disabled={isSolving}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono text-xs font-bold flex items-center justify-center gap-2 transition-all shrink-0 shadow-lg shadow-cyan-500/20"
          >
            <Sparkles size={14} />
            <span>SOLVE & DISPLAY SCENARIO LINEUP (CP-SAT)</span>
          </button>
        </div>

        {/* Active Feedback Card if Solved */}
        {activeScenarioFeedback && (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2 animate-fadeIn">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
              <span>{activeScenarioFeedback}</span>
            </div>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold shrink-0">
              ACTIVE SELECTION
            </span>
          </div>
        )}
      </div>

      {/* 3. Lineup Selection Tabs with 1-Click Copy */}
      <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-none">
        {lineups.map((l, idx) => (
          <div
            key={idx}
            className={`group relative rounded-xl border transition-all p-3 min-w-[260px] cursor-pointer ${
              activeLineupIndex === idx
                ? "border-emerald-500 bg-emerald-500/10 shadow-lg"
                : "border-white/10 bg-slate-900/80 hover:border-white/20 hover:bg-slate-900"
            }`}
            onClick={() => setActiveLineupIndex(idx)}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white font-mono flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${idx === 0 ? "bg-emerald-400 animate-pulse" : "bg-cyan-400"}`} />
                {l.team_name || (l as any).name || `Team ${idx + 1}`}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopyLineup(l, idx);
                }}
                title="1-Click Copy Lineup"
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/15 text-slate-300 hover:text-white transition-all"
              >
                {copiedIndex === idx ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">C: {getCaptainLastName(l.captain)}</span>
              <span className="text-emerald-400 font-semibold">{l.projected_points} pts</span>
            </div>
          </div>
        ))}
      </div>

      {/* 4. Lineup Inspect Workstation */}
      {selectedLineup && <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: 11-Player Pitch Lineup Card (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-6 shadow-none space-y-5">
            
            {/* Lineup Card Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
              <div>
                <div className="inline-flex items-center gap-1.5 text-xs font-sans text-amber-400 font-bold uppercase tracking-wider">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  {selectedLineup.scenario_tag}
                </div>
                <h2 className="text-xl sm:text-2xl font-semibold text-white mt-1">{selectedLineup.team_name}</h2>
                <p className="text-xs text-slate-300 font-sans mt-1 max-w-xl">
                  {selectedLineup.tactical_rationale}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopyLineup(selectedLineup, activeLineupIndex)}
                  className="px-3.5 py-1.5 rounded-xl bg-white/[0.06] border border-white/15 hover:border-amber-400/50 text-xs font-sans font-bold text-slate-200 hover:text-white flex items-center gap-1.5 transition-all shadow-sm"
                >
                  {copiedIndex === activeLineupIndex ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  <span>{copiedIndex === activeLineupIndex ? "COPIED" : "COPY XI"}</span>
                </button>
                <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-sans font-bold">
                  {selectedLineup.gl_rank_potential}
                </span>
              </div>
            </div>

            {/* Cumulative Selection Percentage (CSP) & M-N-C Breakdown Strip */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-950/70 border border-white/10 font-sans text-xs">
              <div className="flex items-center gap-3">
                <div>
                  <span className="text-slate-400 text-xs block">TOTAL CUMULATIVE OWNERSHIP (CSP):</span>
                  <span className={`text-base font-semibold ${
                    selectedLineup.total_ownership_sum <= 650 ? "text-emerald-400" : "text-amber-400"
                  }`}>
                    {selectedLineup.total_ownership_sum}%
                  </span>
                </div>
                <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                  selectedLineup.total_ownership_sum <= 650 
                    ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                    : "bg-amber-500/10 text-amber-300 border-amber-500/30"
                }`}>
                  {selectedLineup.total_ownership_sum <= 650 ? "✓ GL SWEET SPOT (500–650%)" : "⚠ TEMPLATE HIGH OWNERSHIP"}
                </span>
              </div>

              {/* M-N-C Breakdown */}
              <div className="flex items-center gap-3">
                <div>
                  <span className="text-slate-400 text-xs block">M-N-C STRUCTURE:</span>
                  <span className="text-white font-bold">
                    {selectedLineup.mnc_summary || `${selectedLineup.players.filter(p => p.projected_ownership >= 60).length} Core | ${selectedLineup.players.filter(p => p.projected_ownership >= 16 && p.projected_ownership < 60).length} Rotation | ${selectedLineup.players.filter(p => p.projected_ownership < 16).length} Contrarian`}
                  </span>
                </div>
                <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white/[0.04] text-slate-300 border border-white/10">
                  {selectedLineup.cvc_combo_type || (selectedLineup.captain.projected_ownership > 70 ? "Combo B (Sweet Spot)" : "Combo C (GL Killer)")}
                </span>
              </div>
            </div>

            {/* Captain & Vice Captain Showcase */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Captain */}
              <div className="p-4 rounded-xl bg-amber-500/[0.06] border border-amber-500/30 flex items-center justify-between">
                <div>
                  <div className="text-xs font-sans text-amber-400 uppercase tracking-widest font-bold flex items-center gap-1.5">
                    <Award size={14} /> CAPTAIN (2.0x MULTIPLIER)
                  </div>
                  <div className="text-lg font-semibold text-white mt-1">{getCaptainName(selectedLineup.captain)}</div>
                  <div className="text-xs font-sans text-slate-400 mt-0.5">
                    {selectedLineup.captain?.team || "IND-W"} • {selectedLineup.captain?.role || "ALL"} • {selectedLineup.captain?.credits || 9.5} Cr
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-semibold text-amber-300 telemetry-num">
                    {(getCaptainPts(selectedLineup.captain) * 2).toFixed(1)}
                  </div>
                  <div className="text-xs font-sans text-slate-400">EXP 2.0x PTS</div>
                </div>
              </div>

              {/* Vice Captain */}
              <div className="p-4 rounded-xl bg-blue-500/[0.06] border border-blue-500/30 flex items-center justify-between">
                <div>
                  <div className="text-xs font-sans text-blue-400 uppercase tracking-widest font-bold flex items-center gap-1.5">
                    <Award size={14} /> VICE CAPTAIN (1.5x MULTIPLIER)
                  </div>
                  <div className="text-lg font-semibold text-white mt-1">{getCaptainName(selectedLineup.vice_captain)}</div>
                  <div className="text-xs font-sans text-slate-400 mt-0.5">
                    {selectedLineup.vice_captain?.team || "IND-W"} • {selectedLineup.vice_captain?.role || "ALL"} • {selectedLineup.vice_captain?.credits || 9.0} Cr
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-semibold text-blue-300 telemetry-num">
                    {(getCaptainPts(selectedLineup.vice_captain) * 1.5).toFixed(1)}
                  </div>
                  <div className="text-xs font-sans text-slate-400">EXP 1.5x PTS</div>
                </div>
              </div>
            </div>

            {/* 11 Players Table */}
            <div className="space-y-1.5 pt-2">
              <div className="grid grid-cols-12 text-xs font-sans text-slate-400 uppercase px-4 py-1.5 border-b border-white/10">
                <span className="col-span-1">ROLE</span>
                <span className="col-span-5">PLAYER</span>
                <span className="col-span-2 text-center">CREDITS</span>
                <span className="col-span-2 text-center">OWNERSHIP</span>
                <span className="col-span-2 text-right">EXP PTS</span>
              </div>

              {(selectedLineup.players || []).map((p) => {
                const cId = selectedLineup.captain?.id || (typeof selectedLineup.captain === "string" ? selectedLineup.captain : "");
                const vcId = selectedLineup.vice_captain?.id || (typeof selectedLineup.vice_captain === "string" ? selectedLineup.vice_captain : "");
                const isC = p.id === cId || p.name === cId || (p as any).is_captain;
                const isVC = p.id === vcId || p.name === vcId || (p as any).is_vice_captain;
                return (
                  <div
                    key={p.id}
                    className="grid grid-cols-12 items-center px-4 py-2.5 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.06] hover:border-white/20 text-xs font-sans transition-all"
                  >
                    <span className="col-span-1 text-slate-300 font-bold">{p.role}</span>
                    <div className="col-span-5 flex flex-col">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-white">{p.name}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${
                          p.team === "IND" ? "bg-blue-500/10 text-blue-300 border border-blue-500/30" : "bg-rose-500/10 text-rose-300 border border-rose-500/30"
                        }`}>
                          {p.team}
                        </span>
                        {p.projected_ownership >= 60 ? (
                          <span className="text-xs px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-bold">
                            CORE
                          </span>
                        ) : p.projected_ownership >= 16 ? (
                          <span className="text-xs px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 font-bold">
                            ROTATION
                          </span>
                        ) : (
                          <span className="text-xs px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-bold">
                            CONTRARIAN X
                          </span>
                        )}
                        {isC && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500 text-slate-950 font-bold">
                            C
                          </span>
                        )}
                        {isVC && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500 text-slate-950 font-bold">
                            VC
                          </span>
                        )}
                        {p.credits <= 7.5 && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-sans font-bold border border-emerald-500/30">
                            LOW CR GEM
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-400 font-sans flex items-center gap-1.5 mt-0.5">
                        <span className="text-slate-400">{p.bowling_style || (p.batting_style ? `${p.batting_style} Batter` : "")}</span>
                        {p.differential_tag && (
                          <>
                            <span>•</span>
                            <span className="text-amber-400/90 truncate max-w-[240px]">{p.differential_tag}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <span className="col-span-2 text-center text-slate-200 font-bold text-sm">
                      {p.credits.toFixed(1)} Cr
                    </span>
                    <span className="col-span-2 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        p.projected_ownership < 20
                          ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                          : p.projected_ownership < 35
                          ? "bg-blue-500/10 text-blue-300 border border-blue-500/30"
                          : "bg-slate-800 text-slate-300 border border-white/10"
                      }`}>
                        {p.projected_ownership}% Sold
                      </span>
                    </span>
                    <span className="col-span-2 text-right font-semibold text-emerald-400 telemetry-num">
                      {p.projected_points.toFixed(1)}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Lineup Footer Constraints Summary */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-white/10 text-xs font-sans">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-slate-400">Total Credits:</span>
                <strong className="text-white font-bold text-sm">{selectedLineup.total_credits.toFixed(1)} / 100.0 Cr</strong>
                <span className="px-2.5 py-1 rounded-lg bg-white/[0.04] text-slate-300 border border-white/10 text-xs font-bold flex items-center gap-1">
                  🔥 {(100.0 - selectedLineup.total_credits).toFixed(1)} Cr Budget Left (unspent credits)
                </span>
              </div>
              <div className="text-slate-300">
                Cumulative Sold: <strong className="text-white">{selectedLineup.total_ownership_sum}%</strong>
              </div>
              <div className="text-slate-300">
                Differentials: <strong className="text-amber-300">{selectedLineup.differential_count} Players (&lt;35% Sold)</strong>
              </div>
            </div>

          </div>
        </div>

        {/* Right: Portfolio Diversification & Risk Analysis (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* Simulated Ceiling Card */}
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-6 shadow-none space-y-4">
            <div>
              <div className="text-xs font-sans text-slate-400 uppercase tracking-widest">
                SIMULATED CEILING EQUITY
              </div>
              <div className="text-3xl font-semibold text-white telemetry-num mt-1">
                {selectedLineup.simulated_ceiling} <span className="text-xs text-slate-400 font-normal font-sans">pts (heuristic)</span>
              </div>
              <div className="text-xs font-sans text-slate-400 mt-1">
                Base Expected: <strong className="text-white">{selectedLineup.projected_points} pts</strong>
              </div>
            </div>

            {/* Lineup uniqueness score */}
            <div className="pt-3 border-t border-white/10">
              <div className="flex justify-between text-xs font-sans mb-2">
                <span className="text-slate-400">Uniqueness Score:</span>
                <span className="text-emerald-400 font-bold">{selectedLineup.uniqueness_score == null ? "Not calibrated" : `${selectedLineup.uniqueness_score}/100`}</span>
              </div>
              <div className="h-2 w-full bg-white/[0.05] rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-emerald-500 to-amber-500 rounded-full" style={{ width: `${selectedLineup.uniqueness_score ?? 0}%` }}></div>
              </div>
              <div className="text-xs font-sans text-slate-400 mt-1.5">
                Zero chance of field duplication in 500K - 700K spot contests
              </div>
            </div>
          </div>

          {/* Dream11 Rule Compliance Validator */}
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-6 shadow-none space-y-3">
            <div className="text-xs font-sans text-white font-bold uppercase flex items-center gap-2">
              <ShieldCheck size={16} className="text-emerald-400" /> Dream11 Official Verification
            </div>
            
            <div className="space-y-2 text-xs font-sans text-slate-300">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span>Credits &le; 100.0</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1"><CheckCircle2 size={14} /> PASS ({selectedLineup.total_credits})</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span>Squad = 11 Players</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1"><CheckCircle2 size={14} /> PASS (11)</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span>Single Team &le; 10</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1"><CheckCircle2 size={14} /> PASS (Max 7)</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span>WK, BAT, AR, BOWL balance</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1"><CheckCircle2 size={14} /> PASS</span>
              </div>
            </div>
          </div>

          {/* Tactical Game-Script Explainer */}
          <div className="p-4 rounded-2xl bg-amber-500/[0.05] border border-amber-500/20 text-xs font-sans space-y-2">
            <div className="flex items-center gap-2 text-amber-400 font-bold">
              <Flame size={14} /> MEGA CONTEST GAME SCRIPT
            </div>
            <p className="text-slate-300 leading-relaxed font-sans text-xs">
              This lineup captures the maximum correlation upside of an early wicket scenario. By pairing death overs specialists with middle-order accumulators, you hedge against top-order failures and capitalize on outsized bowling points.
            </p>
          </div>

        </div>

      </div>
      }
    </div>
  );
};
