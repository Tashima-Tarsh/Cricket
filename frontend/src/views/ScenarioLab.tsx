import React, { useState, useRef } from "react";
import {
  CloudRain,
  TrendingUp,
  ShieldAlert,
  Sliders,
  Compass,
  Layers,
  RotateCcw,
  Zap,
  BarChart3,
  Award,
  Clock,
  Check,
  Copy,
  Sparkles,
  Flame,
  Crosshair
} from "lucide-react";
import { useMatchContext } from "../context/MatchContext";
import { Lineup } from "../types";

interface DLSScenario {
  overs: number;
  powerplayOvers: number;
  maxOverPerBowler: number;
  quotaBreakdown: string;
  projectedParScore: number;
  requiredRunRate: number;
  totalBalls: number;
  top3BallSharePct: number;
  top3Balls: number;
  lowerOrderBalls: number;
  chaseAdvantagePct: number;
  tacticalKey: string;
  fantasyAdjustment: string;
}

export const computeScenario = (overs: number): DLSScenario => {
  const validOvers = Math.max(5, Math.min(20, Math.round(overs || 20)));
  const baseQuota = Math.floor(validOvers / 5);
  const extraBowlers = validOvers % 5;
  const baseBowlers = extraBowlers > 0 ? 5 - extraBowlers : 5;
  const maxQuota = baseQuota + (extraBowlers > 0 ? 1 : 0);
  const quotaBreakdown = extraBowlers > 0
    ? `${extraBowlers} bowlers × ${baseQuota + 1} ov, ${baseBowlers} bowlers × ${baseQuota} ov`
    : `All 5 bowlers × ${baseQuota} ov`;

  let ppOvers = 2;
  if (validOvers >= 19) ppOvers = 6;
  else if (validOvers >= 15) ppOvers = 5;
  else if (validOvers >= 12) ppOvers = 4;
  else if (validOvers >= 9) ppOvers = 3;

  // Continuous standard T20 DLS resource curve (185 par baseline at Chinnaswamy)
  const resPct = (1.0 - Math.exp(-0.065 * validOvers)) / (1.0 - Math.exp(-0.065 * 20));
  const par = Math.round(185 * resPct);
  const rrr = Math.round((par / validOvers) * 100) / 100;
  const chaseEquity = Math.min(76, Math.round((56.4 + (20 - validOvers) * 1.15) * 10) / 10);
  const totalBalls = validOvers * 6;
  const top3Share = Math.min(88, Math.round((58.0 + (20 - validOvers) * 2.0) * 10) / 10);
  const top3Balls = Math.round(totalBalls * (top3Share / 100));
  const lowerBalls = Math.max(0, totalBalls - top3Balls);

  let tacticalKey = "";
  let fantasyAdjustment = "";

  if (validOvers === 20) {
    tacticalKey = "Full 20-over tactical blueprint: Standard pace-spin balance with full 5-bowler 4-over distribution.";
    fantasyAdjustment = "Balanced roster: 4 pacers, 3 top-order anchors, 3 multi-phase all-rounders, 1 strike spinner.";
  } else if (validOvers >= 16) {
    tacticalKey = `${validOvers}-over curtailed game: Powerplay ${ppOvers} overs. ${quotaBreakdown}. Middle overs compressed to ${validOvers - ppOvers - 4} overs. Target ~${par} (${rrr} RPO).`;
    fantasyAdjustment = "Moderate top-3 upgrade. Part-time bowling volume reduced. Lock in designated death seamers.";
  } else if (validOvers >= 12) {
    tacticalKey = `${validOvers}-over shootout: High-pressure ${ppOvers}-over powerplay. ${quotaBreakdown}. Total ${totalBalls} balls. Top-3 face ~${top3Balls} balls (${top3Share}%). Target ~${par} (${rrr} RPO).`;
    fantasyAdjustment = `Strictly prioritize Top-3 batters & frontline strike bowlers. Lower order (No. 6-8) face only ~${lowerBalls} balls combined.`;
  } else if (validOvers >= 8) {
    tacticalKey = `${validOvers}-over sprint: ${ppOvers} overs powerplay. ${quotaBreakdown}. Zero settling time. Target ~${par} (${rrr} RPO). Chasing win equity at ${chaseEquity}%.`;
    fantasyAdjustment = "Eliminate non-bowling middle-order batters entirely. Captain MUST be an aggressive Opener or pace bowler.";
  } else {
    tacticalKey = `${validOvers}-over micro-sprint: Extreme lottery format. ${ppOvers} overs powerplay. Bowlers get 1 over each. Total balls: ${totalBalls}.`;
    fantasyAdjustment = "Max out top 3 batters. Captain high-SR opener (Abhishek/Samson/Hope). Bowlers selected purely on wicket-taking strike rate.";
  }

  return {
    overs: validOvers,
    powerplayOvers: ppOvers,
    maxOverPerBowler: maxQuota,
    quotaBreakdown,
    projectedParScore: par,
    requiredRunRate: rrr,
    totalBalls,
    top3BallSharePct: top3Share,
    top3Balls,
    lowerOrderBalls: lowerBalls,
    chaseAdvantagePct: chaseEquity,
    tacticalKey,
    fantasyAdjustment
  };
};

export const ScenarioLab: React.FC = () => {
  const { currentMatch, selectedTossChoice, setSelectedTossChoice, activeOvers, setActiveOvers } = useMatchContext();
  const selectedOvers = activeOvers || 20;
  const setSelectedOvers = setActiveOvers;
  const [lineupResult, setLineupResult] = useState<{key:string; lineups:Lineup[]} | null>(null);
  const resultKey = `${currentMatch.id}:${selectedOvers}`;
  const latestKey = useRef(resultKey);
  latestKey.current = resultKey;
  const shortenedLineups = lineupResult?.key === resultKey ? lineupResult.lineups : [];
  const [lineupError, setLineupError] = useState("");
  const [isLoadingLineups, setIsLoadingLineups] = useState<boolean>(false);
  const [copiedTeamIdx, setCopiedTeamIdx] = useState<number | null>(null);

  const scenario = computeScenario(selectedOvers);

  // Calculate projected chase win equity based on Chinnaswamy historical venue model
  const calculateWinEquity = () => {
    let base = selectedTossChoice === "bowl" ? 58.5 : 41.5;
    if (selectedOvers < 20) {
      base += (20 - selectedOvers) * 1.1; // Rain reduction boosts chasing side at Chinnaswamy
    }
    return Math.min(88, Math.max(25, Math.round(base * 10) / 10));
  };

  const chaseEquity = calculateWinEquity();
  const defendEquity = Math.round((100 - chaseEquity) * 10) / 10;

  // Score distribution probability buckets for selected scenario
  const getScoreDistributions = () => {
    const par = scenario.projectedParScore;
    return [
      { range: `< ${par - 20}`, prob: 14, label: "Sub-par / Batting Collapse", color: "bg-rose-500" },
      { range: `${par - 19} - ${par - 8}`, prob: 24, label: "Below Par (Defend Vulnerable)", color: "bg-amber-500" },
      { range: `${par - 7} - ${par + 8}`, prob: 36, label: "Par Range (Competitive)", color: "bg-emerald-500" },
      { range: `${par + 9} - ${par + 20}`, prob: 18, label: "Above Par (Advantage Bat 1st)", color: "bg-cyan-500" },
      { range: `> ${par + 20}`, prob: 8, label: "Match-Winning Ceiling", color: "bg-purple-500" },
    ];
  };

  const scoreDist = getScoreDistributions();

  const handleGenerateShortenedLineups = async () => {
    setIsLoadingLineups(true); setLineupError(""); setLineupResult(null);
    const requestKey = resultKey;
    try {
      const params = new URLSearchParams({match_id:currentMatch.id, overs:String(selectedOvers), teams:"5"});
      const res = await fetch(`/api/ortools/optimize?${params}`, {signal:AbortSignal.timeout(60000)});
      const data = await res.json();
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Lineup generation failed.");
      if (!data.lineups?.length) throw new Error("No feasible lineup satisfies these settings.");
      if (latestKey.current === requestKey) setLineupResult({key:requestKey, lineups:data.lineups});
    } catch (err) {
      if (latestKey.current === requestKey) setLineupError(err instanceof Error ? err.message : "Lineup generation failed.");
    } finally {
      setIsLoadingLineups(false);
    }
  };

  const handleCopyRoster = (lineup: Lineup, index: number) => {
    const names = lineup.players.map(p => {
      let suffix = "";
      if (p.id === lineup.captain.id) suffix = " (C)";
      else if (p.id === lineup.vice_captain.id) suffix = " (VC)";
      return `${p.name}${suffix}`;
    }).join(", ");
    navigator.clipboard.writeText(names);
    setCopiedTeamIdx(index);
    setTimeout(() => setCopiedTeamIdx(null), 2000);
  };

  return (
    <div className="space-y-6">
      {lineupError && <p role="alert">{lineupError}</p>}
      <p className="evidence-note">[VERIFY REQUIRED] Illustrative resource curves and assumed win equity. This is not an official or licensed DLS calculator and must not determine match results.</p>
      {/* Top Banner & Control Deck */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-slate-900/80 border border-white/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <CloudRain size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wider text-white flex items-center gap-2">
              RAIN & REDUCED OVERS LAB
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                ILLUSTRATIVE RAIN MODEL
              </span>
            </h1>
            <p className="text-xs text-slate-400 font-sans">
              {currentMatch.venue.name} | Assumed 20-over baseline; no verified weather or pitch observation
            </p>
          </div>
        </div>

        {/* Continuous Dynamic Overs Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-slate-950 p-2.5 rounded-xl border border-white/10 shadow-inner">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase font-bold whitespace-nowrap">OVERS (5–20):</span>

            {/* Direct Number Stepper & Input */}
            <div className="flex items-center bg-slate-900 border border-white/15 rounded-lg overflow-hidden">
              <button
                type="button"
                onClick={() => setSelectedOvers(Math.max(5, selectedOvers - 1))}
                className="px-2.5 py-1 text-slate-300 hover:text-white hover:bg-white/10 font-mono font-bold text-sm"
                title="Decrease 1 over"
              >
                -
              </button>
              <input
                type="number"
                min={5}
                max={20}
                value={selectedOvers}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (!isNaN(val)) setSelectedOvers(Math.max(5, Math.min(20, val)));
                }}
                className="w-12 bg-transparent text-center font-mono font-extrabold text-sm text-amber-400 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setSelectedOvers(Math.min(20, selectedOvers + 1))}
                className="px-2.5 py-1 text-slate-300 hover:text-white hover:bg-white/10 font-mono font-bold text-sm"
                title="Increase 1 over"
              >
                +
              </button>
            </div>

            {/* Continuous Range Slider */}
            <input
              type="range"
              min={5}
              max={20}
              step={1}
              value={selectedOvers}
              onChange={(e) => setSelectedOvers(parseInt(e.target.value, 10))}
              className="w-24 sm:w-32 accent-emerald-500 cursor-pointer"
              title={`Slide to set overs: ${selectedOvers}`}
            />
          </div>

          {/* Quick Scenario Chips */}
          <div className="flex items-center gap-1 overflow-x-auto pt-1 sm:pt-0">
            {[20, 18, 15, 14, 13, 12, 10, 8, 5].map((ov) => (
              <button
                key={ov}
                onClick={() => setSelectedOvers(ov)}
                className={`px-2 py-1 rounded text-[11px] font-mono font-bold transition-all whitespace-nowrap ${
                  selectedOvers === ov
                    ? (ov < 20 ? "bg-amber-500 text-slate-950 font-extrabold shadow" : "bg-emerald-500 text-slate-950 font-extrabold shadow")
                    : "text-slate-400 hover:text-white hover:bg-white/10"
                }`}
              >
                {ov}ov
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid: 3 Analytical Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Panel 1: DLS Target & Parameter Breakdown */}
        <div className="rounded-xl bg-slate-900/80 border border-white/10 p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2 text-white font-bold">
              <CloudRain size={18} className="text-sky-400" />
              <span>Heuristic rain estimates & over constraints</span>
            </div>
            <span className="text-[10px] font-mono text-sky-300 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
              {selectedOvers} Ov Curtailment
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 font-sans text-xs">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono text-slate-400 uppercase">POWERPLAY CAP</div>
              <div className="text-lg font-bold font-mono text-emerald-400">{scenario.powerplayOvers} Overs</div>
              <div className="text-[11px] text-slate-400">Max 2 fielders outside 30y</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono text-slate-400 uppercase">MAX BOWLER QUOTA</div>
              <div className="text-lg font-bold font-mono text-cyan-400">{scenario.maxOverPerBowler} Overs</div>
              <div className="text-[11px] text-slate-400">ICC Clause 13.9.1</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono text-slate-400 uppercase">PROJECTED PAR</div>
              <div className="text-lg font-bold font-mono text-amber-400">{scenario.projectedParScore} Runs</div>
              <div className="text-[11px] text-slate-400">Req RR: {scenario.requiredRunRate} RPO</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono text-slate-400 uppercase">CHASE WIN BIAS</div>
              <div className="text-lg font-bold font-mono text-purple-400">{scenario.chaseAdvantagePct}%</div>
              <div className="text-[11px] text-slate-400">Heuristic chase estimate</div>
            </div>
          </div>

          {/* ICC Quota & Ball-Share Physics Callouts */}
          <div className="p-3 rounded-lg bg-slate-950/80 border border-sky-500/20 space-y-1">
            <div className="text-[10px] font-mono text-sky-400 uppercase font-bold">BOWLER ALLOCATION (ICC 13.9.1)</div>
            <div className="text-xs font-mono text-slate-200 font-semibold">{scenario.quotaBreakdown}</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/80 border border-amber-500/20 space-y-1">
            <div className="text-[10px] font-mono text-amber-400 uppercase font-bold">BALL-SHARE VOLUME DECAY</div>
            <div className="text-xs text-slate-200">
              Total <span className="font-mono font-bold text-white">{scenario.totalBalls} balls</span> • Top-3 face ~<span className="font-mono font-bold text-amber-300">{scenario.top3Balls} balls</span> ({scenario.top3BallSharePct}%) • Lower order (5-8) faces only ~<span className="font-mono font-bold text-rose-400">{scenario.lowerOrderBalls} balls</span>
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 font-bold">
              <Zap size={14} />
              <span>COACH TACTICAL DIRECTIVE</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">
              {scenario.tacticalKey}
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-mono text-amber-400 font-bold">
              <Award size={14} />
              <span>FANTASY CONTEST IMPACT</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">
              {scenario.fantasyAdjustment}
            </p>
          </div>
        </div>

        {/* Panel 2: Toss Decision & Win Equity Curve */}
        <div className="rounded-xl bg-slate-900/80 border border-white/10 p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2 text-white font-bold">
              <Compass size={18} className="text-emerald-400" />
              <span>Toss Decision & Win Equity</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Illustrative rain scenario
            </span>
          </div>

          {/* Interactive Toss Toggle */}
          <div className="space-y-2">
            <div className="text-[10px] font-mono text-slate-400 uppercase">SIMULATE TOSS WINNER CHOICE:</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setSelectedTossChoice("bowl")}
                className={`p-3 rounded-lg border text-xs font-sans font-bold transition-all text-left space-y-1 ${
                  selectedTossChoice === "bowl"
                    ? "bg-emerald-950/50 border-emerald-500 text-emerald-200 ring-1 ring-emerald-500/40"
                    : "bg-slate-950/60 border-white/10 text-slate-400 hover:text-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>BOWL FIRST (Chasing)</span>
                  {selectedTossChoice === "bowl" && <span className="text-[10px] font-mono text-emerald-400">ACTIVE</span>}
                </div>
                <div className="text-[11px] text-slate-400 font-sans font-normal">
                  Chinnaswamy venue advantage + wet ball buffer
                </div>
              </button>

              <button
                onClick={() => setSelectedTossChoice("bat")}
                className={`p-3 rounded-lg border text-xs font-sans font-bold transition-all text-left space-y-1 ${
                  selectedTossChoice === "bat"
                    ? "bg-emerald-950/50 border-emerald-500 text-emerald-200 ring-1 ring-emerald-500/40"
                    : "bg-slate-950/60 border-white/10 text-slate-400 hover:text-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>BAT FIRST (Defending)</span>
                  {selectedTossChoice === "bat" && <span className="text-[10px] font-mono text-emerald-400">ACTIVE</span>}
                </div>
                <div className="text-[11px] text-slate-400 font-sans font-normal">
                  Scoreboard pressure strategy (requires high par)
                </div>
              </button>
            </div>
          </div>

          {/* Win Equity Gauge */}
          <div className="p-4 rounded-lg bg-slate-950/70 border border-white/5 space-y-2.5">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-emerald-400 font-bold">CHASING: {chaseEquity}%</span>
              <span className="text-cyan-400 font-bold">DEFENDING: {defendEquity}%</span>
            </div>

            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex border border-white/10">
              <div
                className="h-full bg-emerald-500 transition-all duration-500"
                style={{ width: `${chaseEquity}%` }}
              />
              <div
                className="h-full bg-cyan-500 transition-all duration-500"
                style={{ width: `${defendEquity}%` }}
              />
            </div>

            <div className="flex justify-between text-[11px] font-mono text-slate-400">
              <span>Assumed chasing bias</span>
              <span>Defend Index: {(defendEquity / 10).toFixed(1)}/10</span>
            </div>
          </div>

          {/* Venue Characteristics */}
          <div className="space-y-2 text-xs font-sans">
            <div className="text-[10px] font-mono text-slate-400 uppercase">VENUE DEW & SEAM DEVIATION:</div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-2 font-mono text-xs">
              <div className="flex justify-between text-slate-300">
                <span>Pace Wicket Proportion:</span>
                <span className="text-emerald-400 font-bold">59.6% (Fast bowlers dominate)</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Spin Economy Index:</span>
                <span className="text-amber-400 font-bold">8.74 rpo (Vulnerable to wet ball)</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Average First Innings (Series):</span>
                <span className="text-white font-bold">151.3 runs</span>
              </div>
            </div>
          </div>
        </div>

        {/* Panel 3: First Innings Projected Score Distribution */}
        <div className="rounded-xl bg-slate-900/80 border border-white/10 p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2 text-white font-bold">
              <BarChart3 size={18} className="text-cyan-400" />
              <span>Score Probability Distribution</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-white/10">
              100,000 Trials
            </span>
          </div>

          <div className="space-y-3 font-sans">
            {scoreDist.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-white font-mono font-bold">{item.range} runs</span>
                  <span className="text-emerald-400 font-mono font-semibold">{item.prob}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} rounded-full transition-all duration-500`}
                    style={{ width: `${item.prob * 2}%` }}
                  />
                </div>
                <div className="text-[11px] text-slate-400 font-sans">{item.label}</div>
              </div>
            ))}
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-mono text-rose-400 font-bold">
              <ShieldAlert size={14} />
              <span>INTERRUPTION TRIGGER RULE</span>
            </div>
            <p className="text-xs text-slate-300 leading-normal font-sans">
              If rain stops play after 5.0 overs of Innings 2, official playing conditions and an authorised DLS calculation are required; this illustration cannot determine the result.
              Death-over specialist bowlers lose points if match is terminated early.
            </p>
          </div>
        </div>

      </div>

      {/* Interactive Optimization Trigger */}
      <div className="p-6 rounded-xl bg-slate-900/90 border border-emerald-500/30 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase font-bold">
            <Sparkles size={16} /> GOOGLE OR-TOOLS CP-SAT SHORTENED FORMAT SOLVER
          </div>
          <h2 className="text-lg font-bold text-white mt-1">
            Optimize 5 Grand League Teams for {selectedOvers}-Over Match
          </h2>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Applies powerplay ball-share decay, bowler quota caps (max {scenario.maxOverPerBowler} ov/bowler), and locks C/VC to top-order power hitters & strike pacers.
          </p>
        </div>

        <button
          onClick={handleGenerateShortenedLineups}
          disabled={isLoadingLineups}
          className="px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs font-mono uppercase tracking-wider flex items-center gap-2 transition-all shadow-lg shrink-0"
        >
          {isLoadingLineups ? (
            <>
              <RotateCcw size={16} className="animate-spin" />
              SOLVING {selectedOvers}-OVER PORTFOLIO...
            </>
          ) : (
            <>
              <Zap size={16} />
              GENERATE {selectedOvers}-OVER GRAND LEAGUE TEAMS
            </>
          )}
        </button>
      </div>

      {/* Generated Shortened-Match Lineups Display */}
      {shortenedLineups.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider font-bold flex items-center gap-2">
              <Award size={14} /> {selectedOvers}-Over Optimized Grand League Lineups (Sweet Spot CSP 500%–650%)
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              5 Mutually Exclusive Match Scripts Generated
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {shortenedLineups.map((lineup, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900/80 border border-white/10 hover:border-emerald-500/50 transition-all flex flex-col justify-between space-y-3 shadow-lg"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-emerald-400 font-bold">{lineup.team_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-white/10 text-slate-300">
                      {lineup.total_credits} Cr
                    </span>
                  </div>

                  {/* C and VC Badges */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-sans">
                    <div className="p-2 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
                      <div className="text-[9px] font-mono text-emerald-400 font-bold uppercase">CAPTAIN (2X)</div>
                      <div className="text-xs font-bold text-white truncate">{lineup.captain.name}</div>
                    </div>
                    <div className="p-2 rounded-lg bg-cyan-950/40 border border-cyan-500/30">
                      <div className="text-[9px] font-mono text-cyan-400 font-bold uppercase">VICE-CAPTAIN (1.5X)</div>
                      <div className="text-xs font-bold text-white truncate">{lineup.vice_captain.name}</div>
                    </div>
                  </div>

                  {/* Metrics Banner */}
                  <div className="flex items-center justify-between text-[11px] font-mono bg-slate-950 p-2 rounded-lg border border-white/5">
                    <div>
                      <span className="text-slate-500">CSP: </span>
                      <span className="text-emerald-400 font-bold">{lineup.csp || lineup.total_ownership_sum}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500">M-N-C: </span>
                      <span className="text-slate-300">{lineup.mnc_summary}</span>
                    </div>
                  </div>

                  {/* Players Roster */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {lineup.players.map((p) => {
                      const isC = p.id === lineup.captain.id;
                      const isVC = p.id === lineup.vice_captain.id;
                      return (
                        <span
                          key={p.id}
                          className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                            isC ? "bg-emerald-600 text-white font-bold"
                            : isVC ? "bg-cyan-600 text-white font-bold"
                            : "bg-slate-950 text-slate-300 border border-white/5"
                          }`}
                        >
                          {p.name.split(" ").pop()}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <button
                  onClick={() => handleCopyRoster(lineup, idx)}
                  className="w-full py-2 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-white text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition-all shadow"
                >
                  {copiedTeamIdx === idx ? (
                    <>
                      <Check size={14} className="text-emerald-400" />
                      COPIED ROSTER FOR DREAM11!
                    </>
                  ) : (
                    <>
                      <Copy size={14} />
                      1-CLICK COPY ROSTER
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

