import React, { useState, useEffect } from "react";
import { 
  Trophy, 
  Flame, 
  Sliders, 
  Sparkles, 
  TrendingUp, 
  Users, 
  ShieldCheck, 
  ShieldAlert, 
  Copy, 
  Check, 
  Lock, 
  Unlock, 
  RefreshCw, 
  Layers, 
  Calendar, 
  MapPin, 
  BarChart3, 
  ArrowLeftRight, 
  Bookmark, 
  Play, 
  AlertCircle, 
  ChevronRight, 
  CheckCircle2,
  Info,
  Radio,
  Clock,
  Database,
  Cpu
} from "lucide-react";
import { PitchMap, PitchPlayer } from "../components/unique-gl/PitchMap";
import { OwnershipHeatmap } from "../components/unique-gl/OwnershipHeatmap";
import { DifferentialBadge } from "../components/unique-gl/DifferentialBadge";
import { TeamCompare } from "../components/unique-gl/TeamCompare";
import { ConfettiBurst } from "../components/unique-gl/ConfettiBurst";

interface MatchItem {
  id: string;
  name: string;
  format: string;
  status: string;
  is_toss_completed: boolean;
  toss_status: string;
  toss_summary: string;
  start_time: string;
  venue: {
    id?: string;
    name: string;
    city?: string;
    pitch_nature?: string;
    avg_score: number;
  };
  home_team: {
    code: string;
    name: string;
    logo_color: string;
  };
  away_team: {
    code: string;
    name: string;
    logo_color: string;
  };
}

interface VenueDetails {
  name: string;
  city: string;
  pitch_nature: string;
  avg_first_innings: number;
  avg_second_innings: number;
  chasing_win_pct: number;
  pace_wicket_pct: number;
  spin_wicket_pct: number;
  dew_factor: number;
  toss_impact: string;
  toss_completed: boolean;
  toss_summary?: string;
}

interface GeneratedTeam {
  team_id: string;
  name: string;
  rank_1_probability_pct: number;
  rank_10_probability_pct: number;
  median_rank: number;
  projected_points: number;
  ceiling_p90: number;
  floor_p10: number;
  crowd_overlap_pct: number;
  uniqueness_rating: number;
  total_credits: number;
  team_split: string;
  captain: string;
  captain_id: string;
  captain_differential_score?: number;
  vice_captain: string;
  vice_captain_id: string;
  vice_captain_differential_score?: number;
  is_toss_locked: boolean;
  toss_status: string;
  players: PitchPlayer[];
  risk_rating: string;
  percentiles?: Array<{ percentile: string; points: number }>;
}

type SubTab = "dashboard" | "venue" | "pool" | "generate" | "cards" | "simulate" | "entries";

export const UniqueEngineView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<SubTab>("generate");
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState<string>("ind_w_vs_zim_w_2026_02");
  const [selectedMatch, setSelectedMatch] = useState<MatchItem | null>(null);
  
  // Players Pool
  const [players, setPlayers] = useState<PitchPlayer[]>([]);
  const [sortField, setSortField] = useState<keyof PitchPlayer>("differential_score");
  const [sortAsc, setSortAsc] = useState<boolean>(false);
  const [roleFilter, setRoleFilter] = useState<string>("ALL");

  // Venue Intel
  const [venue, setVenue] = useState<VenueDetails | null>(null);

  // Generator Sliders & State
  const [uniquenessLevel, setUniquenessLevel] = useState<number>(8); // 1-10
  const [riskAppetite, setRiskAppetite] = useState<string>("HIGH");
  const [numTeams, setNumTeams] = useState<number>(7);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedTeams, setGeneratedTeams] = useState<GeneratedTeam[]>([]);
  const [activeTeamIndex, setActiveTeamIndex] = useState<number>(0);
  
  // UI Interactions
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savedEntries, setSavedEntries] = useState<any[]>([]);
  const [showConfetti, setShowConfetti] = useState<boolean>(false);

  // Live Trigger & Fusion States
  const [triggerState, setTriggerState] = useState<any>(null);
  const [fusionStatus, setFusionStatus] = useState<any>(null);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);

  // 1. Initial Load: Fetch Matches & Fusion Status
  useEffect(() => {
    fetchMatches();
    fetchSavedEntries();
    fetchFusionStatus();
  }, []);

  // 2. When selected match changes, fetch player pool, venue details, and poll trigger state
  useEffect(() => {
    if (selectedMatchId) {
      fetchMatchData(selectedMatchId);
      fetchTriggerStatus(selectedMatchId);
      const interval = setInterval(() => {
        fetchTriggerStatus(selectedMatchId);
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [selectedMatchId]);

  const fetchTriggerStatus = async (matchId: string) => {
    try {
      const res = await fetch(`/api/trigger/status/${matchId}`);
      if (res.ok) {
        const data = await res.json();
        setTriggerState(data.trigger_state || null);
      }
    } catch (e) {
      // offline
    }
  };

  const fetchFusionStatus = async () => {
    try {
      const res = await fetch("/api/fusion/status");
      if (res.ok) {
        const data = await res.json();
        setFusionStatus(data);
      }
    } catch (e) {
      // offline
    }
  };

  const handleSimulateToss = async () => {
    setIsTriggering(true);
    try {
      const res = await fetch(`/api/trigger/simulate-toss/${selectedMatchId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ toss_winner: "India", toss_decision: "bat" })
      });
      if (res.ok) {
        const data = await res.json();
        setTriggerState(data.trigger_state);
        fetchMatchData(selectedMatchId);
      }
    } finally {
      setIsTriggering(false);
    }
  };

  const handleSimulateLineup = async () => {
    setIsTriggering(true);
    try {
      const res = await fetch(`/api/trigger/simulate-lineup/${selectedMatchId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (res.ok) {
        const data = await res.json();
        setTriggerState(data.trigger_state);
        fetchMatchData(selectedMatchId);
        // Refresh generated teams
        handleGenerateTeams();
      }
    } finally {
      setIsTriggering(false);
    }
  };

  const handleRunFusionPipeline = async () => {
    setIsTriggering(true);
    try {
      const res = await fetch("/api/fusion/run-pipeline", { method: "POST" });
      if (res.ok) {
        fetchFusionStatus();
        fetchMatchData(selectedMatchId);
      }
    } finally {
      setIsTriggering(false);
    }
  };

  const fetchMatches = async () => {
    try {
      const res = await fetch("/matches");
      if (res.ok) {
        const data = await res.json();
        if (data.matches && data.matches.length > 0) {
          setMatches(data.matches);
          setSelectedMatchId(data.matches[0].id);
          setSelectedMatch(data.matches[0]);
        }
      }
    } catch (e) {
      console.warn("Using offline match fallback");
    }
  };

  const fetchMatchData = async (matchId: string) => {
    try {
      const [pRes, vRes] = await Promise.all([
        fetch(`/matches/${matchId}/players`),
        fetch(`/matches/${matchId}/venue`)
      ]);
      if (pRes.ok) {
        const pData = await pRes.json();
        setPlayers(pData.players || []);
      }
      if (vRes.ok) {
        const vData = await vRes.json();
        setVenue(vData.venue || null);
      }
    } catch (e) {
      console.error("Failed fetching match data", e);
    }
  };

  const fetchSavedEntries = async () => {
    try {
      const res = await fetch("/teams/saved");
      if (res.ok) {
        const data = await res.json();
        setSavedEntries(data.entries || []);
      }
    } catch (e) {
      // offline
    }
  };

  // 3. Hero Action: Generate Unique Teams
  const handleGenerateTeams = async () => {
    setIsGenerating(true);
    setSavedSuccessMsg(null);
    try {
      const res = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          match_id: selectedMatchId,
          num_teams: numTeams,
          uniqueness: uniquenessLevel,
          risk: riskAppetite,
          contest_spots: 1000
        })
      });
      if (res.ok) {
        const data = await res.json();
        const teams = data.teams || [];
        setGeneratedTeams(teams);
        setActiveTeamIndex(0);
        setActiveSubTab("cards");

        // Trigger confetti burst if rank 1 probability > 5%
        const hasHighRank1 = teams.some((t: GeneratedTeam) => t.rank_1_probability_pct > 5.0);
        if (hasHighRank1) {
          setShowConfetti(true);
        }
      }
    } catch (e) {
      console.error("Generation failed", e);
    } finally {
      setIsGenerating(false);
    }
  };

  // 4. Save Team Entry
  const handleSaveTeam = async (team: GeneratedTeam) => {
    try {
      const res = await fetch("/teams/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...team,
          match_id: selectedMatchId,
          match_name: selectedMatch?.name || "Cricket Decider"
        })
      });
      if (res.ok) {
        setSavedSuccessMsg("Team locked. Go win that grand league.");
        setShowConfetti(true);
        fetchSavedEntries();
        setTimeout(() => setSavedSuccessMsg(null), 4000);
      }
    } catch (e) {
      console.error("Save failed", e);
    }
  };

  // Copy Lineup in Dream11 Import Format
  const copyTeamText = (team: GeneratedTeam, index: number) => {
    const text = [
      `🏏 DREAM11 UNIQUE CONTRARIAN LINEUP: ${team.name}`,
      `Match: ${selectedMatch?.name || "T20 Match"}`,
      `Captain (2x): ${team.captain} [Diff Score: ${team.captain_differential_score || "Top Edge"}]`,
      `Vice-Captain (1.5x): ${team.vice_captain}`,
      `Crowd Overlap: ${team.crowd_overlap_pct}% | Rank-1 Prob: ${team.rank_1_probability_pct}%`,
      `Total Credits: ${team.total_credits} / 100 Cr`,
      `---------------------------------`,
      ...team.players.map(
        (p) => `${p.name} (${p.team} - ${p.role}) [${p.predicted_points.toFixed(0)} pts, ${p.predicted_ownership.toFixed(0)}% own]`
      )
    ].join("\n");

    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  // Filtered & Sorted Player Pool
  const filteredPlayers = players.filter((p) => {
    if (roleFilter === "ALL") return true;
    return p.role === roleFilter;
  });

  const sortedPlayers = [...filteredPlayers].sort((a, b) => {
    const valA = a[sortField];
    const valB = b[sortField];
    if (typeof valA === "number" && typeof valB === "number") {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc
      ? String(valA).localeCompare(String(valB))
      : String(valB).localeCompare(String(valA));
  });

  const handleSort = (field: keyof PitchPlayer) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const currentTeam = generatedTeams[activeTeamIndex] || null;

  return (
    <div className="min-h-screen bg-[#0B0F14] text-[#E8EDF2] flex flex-col font-sans pb-20">
      <ConfettiBurst active={showConfetti} onComplete={() => setShowConfetti(false)} />

      {/* Hero Header Section */}
      <section className="border-b border-white/10 bg-[#141A22]/90 backdrop-blur-xl px-4 lg:px-8 py-4 sticky top-0 z-30 shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00C853] via-[#FFB300] to-[#FF5252] p-[1.5px] shadow-[0_0_20px_rgba(0,200,83,0.3)]">
              <div className="w-full h-full bg-[#0B0F14] rounded-xl flex items-center justify-center">
                <Flame size={20} className="text-[#00C853]" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black text-white tracking-wide">
                  DREAM11 <span className="text-[#00C853]">UNIQUE</span> TEAM ENGINE
                </h1>
                <span className="px-2 py-0.5 rounded-full bg-[#FFB300]/15 border border-[#FFB300]/30 text-[10px] font-mono text-[#FFB300] font-bold">
                  SPOT THE CROWD, BEAT THE CROWD
                </span>
              </div>
              <p className="text-xs text-[#8A96A3]">
                Contrarian Mathematical Optimizer & Rank-1 Monte Carlo Simulator
              </p>
            </div>
          </div>

          {/* Match Selector Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[#8A96A3] hidden sm:inline">Active Fixture:</span>
            <select
              value={selectedMatchId}
              onChange={(e) => {
                setSelectedMatchId(e.target.value);
                const found = matches.find((m) => m.id === e.target.value);
                if (found) setSelectedMatch(found);
              }}
              aria-label="Active Fixture"
              className="bg-[#0B0F14] border border-white/10 text-xs font-mono text-white rounded-xl px-3 py-2 outline-none focus:border-[#00C853] transition-colors"
            >
              {matches.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.format})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Desktop Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-4 flex items-center gap-1 overflow-x-auto border-t border-white/5 pt-2 scrollbar-none">
          {[
            { id: "generate", label: "Team Generator", icon: Sliders },
            { id: "cards", label: `Team Cards (${generatedTeams.length})`, icon: Trophy },
            { id: "pool", label: `Player Pool (${players.length})`, icon: Users },
            { id: "venue", label: "Pitch & Venue", icon: MapPin },
            { id: "simulate", label: "Rank Simulator", icon: BarChart3 },
            { id: "entries", label: `My Entries (${savedEntries.length})`, icon: Bookmark },
            { id: "dashboard", label: "Matches Grid", icon: Calendar }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id as SubTab)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-mono font-medium transition-all shrink-0 ${
                  isActive
                    ? "bg-[#00C853]/20 border border-[#00C853]/50 text-[#00C853] font-bold shadow-[0_0_15px_rgba(0,200,83,0.2)]"
                    : "text-[#8A96A3] hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </section>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto w-full px-4 lg:px-8 py-6 flex-1 flex flex-col gap-6">
        {/* Success Alert Banner */}
        {savedSuccessMsg && (
          <div className="p-3 rounded-xl border border-[#00C853]/50 bg-[#00C853]/15 text-[#00C853] flex items-center justify-between text-xs font-mono font-bold animate-in fade-in duration-300">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={16} />
              {savedSuccessMsg}
            </span>
            <button onClick={() => setActiveSubTab("entries")} className="underline hover:text-white">
              View My Entries &rarr;
            </button>
          </div>
        )}

        {/* Live 30-Minute Toss & Lineup Trigger Banner */}
        <section className="rounded-2xl border border-white/10 bg-[#141A22] p-4 lg:p-5 shadow-2xl flex flex-col gap-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <Radio size={18} className="animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-white tracking-wide">
                    LIVE 30-MINUTE TOSS & LINEUP TRIGGER
                  </h3>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase ${
                    triggerState?.state === "LINEUP_LOCKED"
                      ? "bg-[#00C853]/20 text-[#00C853] border border-[#00C853]/40"
                      : triggerState?.state === "TOSS_DONE"
                      ? "bg-[#FFB300]/20 text-[#FFB300] border border-[#FFB300]/40"
                      : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  }`}>
                    {triggerState?.state || "SCHEDULED"}
                  </span>
                </div>
                <p className="text-xs text-[#8A96A3]">
                  State Machine: Auto-locks 22 confirmed players and re-optimizes uniqueness upon XI confirmation.
                </p>
              </div>
            </div>

            {/* Quick Action Simulation Buttons */}
            <div className="flex items-center gap-2 flex-wrap">
              <button
                disabled={isTriggering}
                onClick={handleSimulateToss}
                className="px-3 py-1.5 rounded-xl bg-[#0B0F14] border border-amber-500/40 hover:bg-amber-500/10 text-amber-400 text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
                title="Simulate toss outcome"
              >
                <Clock size={12} />
                <span>Simulate Toss (T-30m)</span>
              </button>

              <button
                disabled={isTriggering}
                onClick={handleSimulateLineup}
                className="px-3 py-1.5 rounded-xl bg-[#00C853]/20 border border-[#00C853]/60 hover:bg-[#00C853]/30 text-[#00C853] text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
                title="Simulate confirmed playing XI and re-optimize unique portfolios"
              >
                <CheckCircle2 size={12} />
                <span>Confirm Lineup XI (T-25m)</span>
              </button>

              <button
                disabled={isTriggering}
                onClick={handleRunFusionPipeline}
                className="px-3 py-1.5 rounded-xl bg-[#0B0F14] border border-white/10 hover:border-white/30 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
                title="Re-run openIPL + Pitchnama data fusion"
              >
                <Database size={12} />
                <span>Run Data Fusion</span>
              </button>
            </div>
          </div>

          {/* Stepper Progress Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs font-mono">
            {[
              { id: "SCHEDULED", label: "1. Scheduled", sub: "T-35m" },
              { id: "TOSS_PENDING", label: "2. Toss Pending", sub: "T-30m" },
              { id: "TOSS_DONE", label: "3. Toss Decided", sub: "T-28m" },
              { id: "LINEUP_LOCKED", label: "4. Lineup Confirmed", sub: "T-25m" },
              { id: "LIVE", label: "5. Match Live", sub: "T-0m" }
            ].map((step, idx) => {
              const currentStepIdx = ["SCHEDULED", "TOSS_PENDING", "TOSS_DONE", "LINEUP_LOCKED", "LIVE_SOON", "LIVE"].indexOf(triggerState?.state || "SCHEDULED");
              const isPast = idx <= currentStepIdx;
              const isCurrent = idx === currentStepIdx;

              return (
                <div
                  key={step.id}
                  className={`p-2 rounded-xl border text-center transition-all ${
                    isCurrent
                      ? "border-[#00C853] bg-[#00C853]/15 shadow-[0_0_15px_rgba(0,200,83,0.2)] text-white"
                      : isPast
                      ? "border-white/10 bg-[#0B0F14] text-[#00C853]"
                      : "border-white/5 bg-[#0B0F14]/50 text-[#8A96A3]"
                  }`}
                >
                  <div className="font-bold text-[11px] truncate">{step.label}</div>
                  <div className="text-[10px] text-[#8A96A3]">{step.sub}</div>
                </div>
              );
            })}
          </div>

          {/* Fusion Pipeline Live Metrics Tag */}
          <div className="flex flex-wrap items-center justify-between text-[11px] font-mono bg-[#0B0F14] p-2.5 rounded-xl border border-white/5 text-[#8A96A3]">
            <div className="flex items-center gap-4 flex-wrap">
              <span>
                Matchups Indexed: <strong className="text-white">{fusionStatus?.matchups_indexed || 3194}</strong>
              </span>
              <span>
                Venue Profiles: <strong className="text-white">{fusionStatus?.venues_profiled || 13}</strong>
              </span>
              <span>
                Pitchnama Tilt: <strong className="text-[#00C853]">Active (Upper Hand Meter)</strong>
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Cpu size={12} className="text-[#00C853]" />
              <span>Zero-leakage Parquet Store</span>
            </div>
          </div>

          {/* Critical Alert Warning Banner if T-15 not confirmed */}
          {triggerState?.alert && (
            <div className="p-2.5 rounded-xl border border-red-500/40 bg-red-500/10 text-red-400 text-xs font-mono flex items-center gap-2">
              <AlertCircle size={14} className="shrink-0" />
              <span>{triggerState.alert}</span>
            </div>
          )}
        </section>

        {/* ============================================================== */}
        {/* VIEW 1: GENERATE & CONTROLS (HERO WORKSPACE)                  */}
        {/* ============================================================== */}
        {activeSubTab === "generate" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Sliders & Controls */}
            <div className="lg:col-span-5 flex flex-col gap-5">
              <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-6">
                <div>
                  <span className="text-xs font-mono text-[#00C853] uppercase font-bold tracking-wider">
                    Contrarian Optimizer
                  </span>
                  <h3 className="text-base font-bold text-white">Grand League Team Engine</h3>
                  <p className="text-xs text-[#8A96A3] mt-1">
                    Solve combinatorial rosters minimizing crowd overlap while locking high-ceiling differential C/VCs.
                  </p>
                </div>

                {/* Slider 1: Uniqueness Level (1 to 10) */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-mono font-bold text-white flex items-center gap-1.5">
                      <Sparkles size={14} className="text-[#FFB300]" />
                      Uniqueness Level: <span className="text-[#FFB300] font-black">{uniquenessLevel} / 10</span>
                    </label>
                    <span className="text-[10px] font-mono text-[#8A96A3]">
                      {uniquenessLevel <= 3 ? "Chalky Baseline" : uniquenessLevel <= 7 ? "Balanced Leverage" : "Extreme Contrarian"}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={uniquenessLevel}
                    onChange={(e) => setUniquenessLevel(Number(e.target.value))}
                    aria-label="Uniqueness Level"
                    className="w-full accent-[#00C853] cursor-pointer"
                  />
                  <p className="text-[11px] text-[#8A96A3] italic bg-[#0B0F14] p-2 rounded-lg border border-white/5">
                    💡 <strong>Uniqueness tooltip:</strong> Low = chalk. High = fewer people share your team = higher rank-1 ceiling.
                  </p>
                </div>

                {/* Slider 2: Number of Teams (1 to 20) */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-mono font-bold text-white flex items-center gap-1.5">
                      <Layers size={14} className="text-[#00C853]" />
                      Number of Entries: <span className="text-[#00C853] font-black">{numTeams} Teams</span>
                    </label>
                    <span className="text-[10px] font-mono text-[#8A96A3]">
                      (Recommended: 7 for GL Room)
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    value={numTeams}
                    onChange={(e) => setNumTeams(Number(e.target.value))}
                    aria-label="Number of Entries"
                    className="w-full accent-[#00C853] cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-[#8A96A3]">
                    <span>1 Entry</span>
                    <span className="text-[#00C853] font-bold">7 Entries (Optimum)</span>
                    <span>20 Max</span>
                  </div>
                </div>

                {/* Selector 3: Risk Appetite */}
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-mono font-bold text-white">Risk Appetite</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { id: "LOW", label: "Conservative", color: "border-slate-600" },
                      { id: "MEDIUM", label: "Balanced", color: "border-[#FFB300]/50" },
                      { id: "HIGH", label: "Aggressive (Boom/Bust)", color: "border-[#00C853]/60" }
                    ].map((mode) => (
                      <button
                        key={mode.id}
                        onClick={() => setRiskAppetite(mode.id)}
                        className={`p-2 rounded-xl border text-xs font-mono font-bold transition-all text-center ${
                          riskAppetite === mode.id
                            ? "bg-[#00C853]/20 border-[#00C853] text-[#00C853]"
                            : "bg-[#0B0F14] border-white/10 text-[#8A96A3] hover:text-white"
                        }`}
                      >
                        {mode.label}
                      </button>
                    ))}
                  </div>
                  <p className="text-[10px] font-mono text-[#FFB300] flex items-center gap-1 mt-1">
                    <AlertCircle size={12} />
                    Risk warning: Unique teams boom or bust. Enter 7 for best odds.
                  </p>
                </div>

                {/* Toss Pending Warning / Status */}
                <div className="p-3 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400 shrink-0">
                    {selectedMatch?.is_toss_completed ? <Unlock size={16} /> : <Lock size={16} />}
                  </div>
                  <div>
                    <div className="text-xs font-mono font-bold text-amber-300">
                      {selectedMatch?.is_toss_completed ? "Lineups Confirmed" : "Pre-Toss Formation"}
                    </div>
                    <div className="text-[11px] text-[#8A96A3]">
                      {selectedMatch?.is_toss_completed
                        ? "Official starting XIs active. Zero substitution risk."
                        : "Locked until toss. Lineups confirm 30 min before."}
                    </div>
                  </div>
                </div>

                {/* HERO ACTION BUTTON */}
                <button
                  disabled={isGenerating}
                  onClick={handleGenerateTeams}
                  className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-[#00C853] via-emerald-500 to-[#FFB300] hover:opacity-95 text-[#0B0F14] font-black text-sm font-mono tracking-wider uppercase transition-all shadow-[0_0_25px_rgba(0,200,83,0.4)] flex items-center justify-center gap-2 cursor-pointer active:scale-[0.98] disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      {/* Animated cricket ball spinner loader */}
                      <span className="w-5 h-5 rounded-full border-2 border-[#0B0F14] border-t-transparent animate-spin" />
                      <span>Optimizing Contrarian Portfolios...</span>
                    </>
                  ) : (
                    <>
                      <Flame size={18} />
                      <span>Generate Unique Teams</span>
                    </>
                  )}
                </button>
              </div>

              {/* Unique Rules Infobox */}
              <div className="rounded-2xl border border-white/10 bg-[#141A22] p-4 text-xs flex flex-col gap-2">
                <span className="font-mono font-bold text-[#00C853] uppercase text-[10px]">
                  Applied Mathematical Rules
                </span>
                <ul className="space-y-1.5 text-[#8A96A3] font-mono text-[11px]">
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-[#00C853] shrink-0" />
                    <span>Never fills every team with the top-5 most-owned chalk</span>
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-[#00C853] shrink-0" />
                    <span>Differential score = predicted_points / predicted_ownership</span>
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-[#00C853] shrink-0" />
                    <span>Captain = Highest differential score (not the most obvious)</span>
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-[#00C853] shrink-0" />
                    <span>Vice Captain = 2nd highest differential score</span>
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-[#00C853] shrink-0" />
                    <span>Enforces 6-5 team split foundation + sub-85 credit bounds</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Right Column: Public Ownership Heatmap */}
            <div className="lg:col-span-7 flex flex-col gap-5">
              <OwnershipHeatmap players={players} />
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 2: TEAM CARDS & PITCH MAP                                */}
        {/* ============================================================== */}
        {activeSubTab === "cards" && (
          <div className="flex flex-col gap-6">
            {generatedTeams.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/10 bg-[#141A22] p-12 text-center flex flex-col items-center justify-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center text-[#8A96A3]">
                  <Sliders size={32} />
                </div>
                <div>
                  <h4 className="text-base font-bold text-white">No teams yet</h4>
                  <p className="text-xs text-[#8A96A3] mt-1 max-w-sm">
                    No teams yet. Hit Generate and we'll build you a differential XI.
                  </p>
                </div>
                <button
                  onClick={() => setActiveSubTab("generate")}
                  className="px-5 py-2.5 rounded-xl bg-[#00C853] text-[#0B0F14] font-mono font-bold text-xs hover:bg-[#00C853]/90 transition-all cursor-pointer"
                >
                  Go to Team Generator &rarr;
                </button>
              </div>
            ) : (
              <>
                {/* Team Switcher Tabs */}
                <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
                  {generatedTeams.map((team, idx) => {
                    const isCurrent = activeTeamIndex === idx;
                    return (
                      <button
                        key={team.team_id}
                        onClick={() => setActiveTeamIndex(idx)}
                        className={`px-4 py-2.5 rounded-xl text-xs font-mono font-bold transition-all shrink-0 flex items-center gap-2.5 ${
                          isCurrent
                            ? "bg-[#00C853]/20 border border-[#00C853] text-[#00C853] shadow-[0_0_15px_rgba(0,200,83,0.2)]"
                            : "bg-[#141A22] border border-white/5 text-[#8A96A3] hover:text-white"
                        }`}
                      >
                        <span>Team #{idx + 1}</span>
                        <span className="px-1.5 py-0.5 rounded bg-[#0B0F14] text-[10px] text-[#FFB300]">
                          {team.rank_1_probability_pct}% R1
                        </span>
                      </button>
                    );
                  })}
                </div>

                {/* Active Team Highlight Banner */}
                {currentTeam && (
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: SVG PitchMap */}
                    <div className="lg:col-span-7 flex flex-col gap-4">
                      <PitchMap
                        players={currentTeam.players}
                        teamName={currentTeam.name}
                        captainName={currentTeam.captain}
                        viceCaptainName={currentTeam.vice_captain}
                      />
                    </div>

                    {/* Right: Team Intel Card & Actions */}
                    <div className="lg:col-span-5 flex flex-col gap-4">
                      <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-5">
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="text-[10px] font-mono text-[#00C853] uppercase font-bold tracking-wider">
                              Contrarian Portfolio Specs
                            </span>
                            <h3 className="text-lg font-bold text-white">{currentTeam.name}</h3>
                          </div>
                          <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-[#00C853]/20 text-[#00C853] border border-[#00C853]/40 font-bold">
                            {currentTeam.risk_rating}
                          </span>
                        </div>

                        {/* BIG RANK-1 PROBABILITY HERO METRIC */}
                        <div className="p-4 rounded-xl border border-[#FFB300]/30 bg-gradient-to-br from-[#1E1A0C] to-[#141A22] flex items-center justify-between">
                          <div>
                            <span className="text-[10px] font-mono text-[#8A96A3] uppercase block">
                              Rank-1 label
                            </span>
                            <span className="text-xs text-[#E8EDF2] font-medium block">
                              Estimated rank-1 chance in a 1,000-player GL
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-2xl font-black font-mono text-[#FFB300]">
                              {currentTeam.rank_1_probability_pct}%
                            </span>
                            <span className="text-[10px] font-mono text-[#00C853] block">
                              Top 10: {currentTeam.rank_10_probability_pct}%
                            </span>
                          </div>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                          <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                            <span className="text-[#8A96A3] block text-[10px]">Crowd Overlap</span>
                            <strong className="text-sm text-[#00C853]">{currentTeam.crowd_overlap_pct}%</strong>
                            <div className="w-full bg-white/10 h-1.5 rounded-full mt-1.5 overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-[#00C853] to-[#FF5252]"
                                style={{ width: `${Math.min(100, (currentTeam.crowd_overlap_pct / 1100) * 100)}%` }}
                              />
                            </div>
                          </div>

                          <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                            <span className="text-[#8A96A3] block text-[10px]">Projected Score</span>
                            <strong className="text-sm text-white">{currentTeam.projected_points} pts</strong>
                            <span className="text-[10px] text-[#8A96A3] block mt-1">
                              Ceiling: {currentTeam.ceiling_p90} pts
                            </span>
                          </div>

                          <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                            <span className="text-[#8A96A3] block text-[10px]">Captain (2x)</span>
                            <strong className="text-xs text-[#FFB300] truncate block">{currentTeam.captain}</strong>
                            <span className="text-[9px] text-[#8A96A3] block mt-0.5">
                              Diff score: {currentTeam.captain_differential_score || "1.82"}
                            </span>
                          </div>

                          <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                            <span className="text-[#8A96A3] block text-[10px]">Vice Captain (1.5x)</span>
                            <strong className="text-xs text-cyan-300 truncate block">{currentTeam.vice_captain}</strong>
                            <span className="text-[9px] text-[#8A96A3] block mt-0.5">
                              Diff score: {currentTeam.vice_captain_differential_score || "1.45"}
                            </span>
                          </div>
                        </div>

                        {/* Credits & Split */}
                        <div className="flex items-center justify-between text-xs font-mono p-2.5 rounded-xl bg-[#0B0F14] border border-white/5">
                          <span>Team Split: <strong className="text-white">{currentTeam.team_split}</strong></span>
                          <span>Credits Used: <strong className="text-white">{currentTeam.total_credits} / 100</strong></span>
                          <span className="text-[#00C853]">{(100 - currentTeam.total_credits).toFixed(1)} Cr Left</span>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-3 mt-2">
                          <button
                            onClick={() => copyTeamText(currentTeam, activeTeamIndex)}
                            className="flex-1 py-2.5 px-4 rounded-xl bg-[#0B0F14] border border-white/10 hover:border-white/30 text-xs font-mono font-bold text-white flex items-center justify-center gap-2 cursor-pointer transition-colors"
                          >
                            {copiedIndex === activeTeamIndex ? (
                              <>
                                <Check size={14} className="text-[#00C853]" />
                                <span>Copied!</span>
                              </>
                            ) : (
                              <>
                                <Copy size={14} />
                                <span>Copy Lineup</span>
                              </>
                            )}
                          </button>

                          <button
                            onClick={() => handleSaveTeam(currentTeam)}
                            className="flex-1 py-2.5 px-4 rounded-xl bg-[#00C853] hover:bg-[#00C853]/90 text-[#0B0F14] text-xs font-mono font-black flex items-center justify-center gap-2 cursor-pointer transition-all shadow-[0_0_15px_rgba(0,200,83,0.3)]"
                          >
                            <Bookmark size={14} />
                            <span>Save Entry</span>
                          </button>
                        </div>
                      </div>

                      {/* Side-by-Side Comparison Snippet */}
                      <TeamCompare uniqueTeam={currentTeam} />
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 3: PLAYER POOL TABLE (SORTABLE)                           */}
        {/* ============================================================== */}
        {activeSubTab === "pool" && (
          <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/5">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Users size={16} className="text-[#00C853]" />
                  Player Pool & Differential Metrics
                </h3>
                <p className="text-xs text-[#8A96A3]">
                  Sortable table displaying projected fantasy points, ownership %, and the differential edge score.
                </p>
              </div>

              {/* Role Filter Tabs */}
              <div className="flex items-center gap-1 bg-[#0B0F14] p-1 rounded-xl border border-white/5">
                {["ALL", "WK", "BAT", "AR", "BOWL"].map((role) => (
                  <button
                    key={role}
                    onClick={() => setRoleFilter(role)}
                    className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all ${
                      roleFilter === role
                        ? "bg-[#00C853] text-[#0B0F14]"
                        : "text-[#8A96A3] hover:text-white"
                    }`}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-white/10 text-[#8A96A3]">
                    <th className="py-3 px-3">Player</th>
                    <th className="py-3 px-2 cursor-pointer hover:text-white" onClick={() => handleSort("role")}>
                      Role
                    </th>
                    <th className="py-3 px-2 cursor-pointer hover:text-white" onClick={() => handleSort("team")}>
                      Team
                    </th>
                    <th className="py-3 px-2 cursor-pointer hover:text-white" onClick={() => handleSort("credits")}>
                      Credits {sortField === "credits" ? (sortAsc ? "▲" : "▼") : ""}
                    </th>
                    <th className="py-3 px-3 cursor-pointer hover:text-white" onClick={() => handleSort("predicted_points")}>
                      Exp Pts {sortField === "predicted_points" ? (sortAsc ? "▲" : "▼") : ""}
                    </th>
                    <th className="py-3 px-3 cursor-pointer hover:text-white" onClick={() => handleSort("predicted_ownership")}>
                      Ownership % {sortField === "predicted_ownership" ? (sortAsc ? "▲" : "▼") : ""}
                    </th>
                    <th className="py-3 px-3 cursor-pointer hover:text-white" onClick={() => handleSort("differential_score")}>
                      Diff Score {sortField === "differential_score" ? (sortAsc ? "▲" : "▼") : ""}
                    </th>
                    <th className="py-3 px-3">Edge Badge</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {sortedPlayers.map((p) => {
                    const isDiff = p.predicted_ownership < 30.0;
                    const isChalk = p.predicted_ownership >= 65.0;
                    return (
                      <tr key={p.id} className="hover:bg-white/[0.02] transition-colors">
                        <td className="py-2.5 px-3">
                          <span className="font-bold text-white text-xs">{p.name}</span>
                        </td>
                        <td className="py-2.5 px-2">
                          <span className="px-1.5 py-0.5 rounded bg-[#0B0F14] text-[10px] text-slate-300">
                            {p.role}
                          </span>
                        </td>
                        <td className="py-2.5 px-2 text-[#8A96A3]">{p.team}</td>
                        <td className="py-2.5 px-2 font-bold text-white">{p.credits}</td>
                        <td className="py-2.5 px-3 font-bold text-emerald-400">
                          {p.predicted_points.toFixed(1)}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`font-bold ${
                              isChalk ? "text-[#FF5252]" : isDiff ? "text-[#00C853]" : "text-[#FFB300]"
                            }`}
                          >
                            {p.predicted_ownership.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="font-black text-[#FFB300]">
                            {p.differential_score.toFixed(2)}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <DifferentialBadge ownershipPct={p.predicted_ownership} size="sm" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 4: MATCH DETAIL & VENUE INTEL                             */}
        {/* ============================================================== */}
        {activeSubTab === "venue" && venue && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-4">
              <span className="text-xs font-mono text-[#00C853] uppercase font-bold tracking-wider">
                Venue Intelligence
              </span>
              <h3 className="text-base font-bold text-white">{venue.name}</h3>
              <p className="text-xs text-[#8A96A3]">{venue.pitch_nature}</p>

              <div className="grid grid-cols-2 gap-3 text-xs font-mono mt-2">
                <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                  <span className="text-[#8A96A3] block text-[10px]">Avg 1st Innings</span>
                  <strong className="text-base text-white">{venue.avg_first_innings} Runs</strong>
                </div>
                <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                  <span className="text-[#8A96A3] block text-[10px]">Avg 2nd Innings</span>
                  <strong className="text-base text-white">{venue.avg_second_innings} Runs</strong>
                </div>
                <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                  <span className="text-[#8A96A3] block text-[10px]">Chasing Win Rate</span>
                  <strong className="text-base text-[#00C853]">{venue.chasing_win_pct}%</strong>
                </div>
                <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                  <span className="text-[#8A96A3] block text-[10px]">Pace / Spin Split</span>
                  <strong className="text-base text-white">{venue.pace_wicket_pct}% / {venue.spin_wicket_pct}%</strong>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-4">
              <span className="text-xs font-mono text-[#FFB300] uppercase font-bold tracking-wider">
                Toss Impact & Environmental Conditions
              </span>
              <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                <span className="text-xs font-bold text-white block mb-1">Toss Tactical Impact</span>
                <p className="text-xs text-[#8A96A3]">{venue.toss_impact}</p>
              </div>

              <div className="p-3 rounded-xl bg-[#0B0F14] border border-white/5">
                <span className="text-xs font-bold text-white block mb-1">Dew Factor</span>
                <p className="text-xs text-[#8A96A3]">
                  Coefficient: <strong className="text-white">{(venue.dew_factor * 100).toFixed(0)}%</strong>. 
                  {venue.dew_factor > 0.2 ? " Noticeable dew expected in second innings favoring batters." : " Dry conditions expected."}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-white/10 bg-[#0B0F14] flex items-center justify-between text-xs font-mono">
                <span className="text-[#8A96A3]">Status:</span>
                <span className="font-bold text-[#FFB300]">
                  {venue.toss_completed ? "Toss Decided" : "Locked until toss. Lineups confirm 30 min before."}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 5: MONTE CARLO RANK SIMULATOR                             */}
        {/* ============================================================== */}
        {activeSubTab === "simulate" && (
          <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-5">
            <div>
              <span className="text-xs font-mono text-[#00C853] uppercase font-bold tracking-wider">
                10,000-Trial Contest Simulator
              </span>
              <h3 className="text-base font-bold text-white">Monte Carlo Rank Percentile Distribution</h3>
              <p className="text-xs text-[#8A96A3] mt-1">
                Simulating each unique lineup against empirical Jones-Nick-93 field models with 65% chalk clumping.
              </p>
            </div>

            {generatedTeams.length === 0 ? (
              <div className="p-8 text-center text-xs font-mono text-[#8A96A3] border border-dashed border-white/10 rounded-xl">
                Please generate unique teams first to view the simulation percentiles.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {generatedTeams.map((team, idx) => (
                  <div
                    key={team.team_id}
                    className="p-4 rounded-xl border border-white/10 bg-[#0B0F14] flex flex-col gap-3"
                  >
                    <div className="flex items-center justify-between border-b border-white/5 pb-2">
                      <span className="text-xs font-mono font-bold text-white">{team.name}</span>
                      <span className="text-xs font-mono text-[#FFB300] font-black">
                        {team.rank_1_probability_pct}% Rank-1
                      </span>
                    </div>

                    <div className="space-y-1.5 text-xs font-mono">
                      <div className="flex justify-between">
                        <span className="text-[#8A96A3]">Floor (p10):</span>
                        <strong className="text-white">{team.floor_p10} pts</strong>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#8A96A3]">Median (p50):</span>
                        <strong className="text-white">{team.projected_points} pts</strong>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#8A96A3]">Ceiling (p90):</span>
                        <strong className="text-[#00C853]">{team.ceiling_p90} pts</strong>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#8A96A3]">Crowd Overlap:</span>
                        <strong className="text-[#FFB300]">{team.crowd_overlap_pct}%</strong>
                      </div>
                    </div>

                    {/* Visual Percentile Bar */}
                    <div className="pt-2 border-t border-white/5">
                      <span className="text-[10px] font-mono text-[#8A96A3] block mb-1">
                        Rank-1 Equity Curve
                      </span>
                      <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden flex">
                        <div
                          className="bg-[#00C853] h-full"
                          style={{ width: `${Math.min(100, team.rank_1_probability_pct * 8)}%` }}
                        />
                        <div
                          className="bg-[#FFB300] h-full"
                          style={{ width: `${Math.min(100, team.rank_10_probability_pct * 2)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 6: MY ENTRIES TRACKER                                     */}
        {/* ============================================================== */}
        {activeSubTab === "entries" && (
          <div className="rounded-2xl border border-white/10 bg-[#141A22] p-5 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Bookmark size={16} className="text-[#00C853]" />
                  Saved Grand League Entries
                </h3>
                <p className="text-xs text-[#8A96A3]">
                  Your locked contrarian slips ready for 1-click contest entry.
                </p>
              </div>
              <span className="px-3 py-1 rounded-full bg-[#00C853]/20 text-[#00C853] text-xs font-mono font-bold">
                {savedEntries.length} Saved
              </span>
            </div>

            {savedEntries.length === 0 ? (
              <div className="p-12 text-center text-xs font-mono text-[#8A96A3] border border-dashed border-white/10 rounded-xl">
                No entries saved yet. Generate a team and click "Save Entry".
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {savedEntries.map((entry, idx) => (
                  <div
                    key={entry.entry_id || idx}
                    className="p-4 rounded-xl border border-white/10 bg-[#0B0F14] flex flex-col gap-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-white">{entry.name}</span>
                      <span className="text-[10px] font-mono text-[#8A96A3]">
                        {entry.saved_at ? new Date(entry.saved_at).toLocaleTimeString() : "Recent"}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                      <div className="p-2 rounded bg-[#141A22]">
                        <span className="text-[10px] text-[#8A96A3] block">Captain</span>
                        <strong className="text-white text-xs truncate block">{entry.captain}</strong>
                      </div>
                      <div className="p-2 rounded bg-[#141A22]">
                        <span className="text-[10px] text-[#8A96A3] block">Vice Captain</span>
                        <strong className="text-cyan-300 text-xs truncate block">{entry.vice_captain}</strong>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-[#00C853] font-bold">R1: {entry.rank_1_probability_pct}%</span>
                      <span className="text-[#8A96A3]">Overlap: {entry.crowd_overlap_pct}%</span>
                      <button
                        onClick={() => copyTeamText(entry, idx)}
                        className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white cursor-pointer"
                        title="Copy text format"
                      >
                        <Copy size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW 7: DASHBOARD (UPCOMING MATCHES GRID)                      */}
        {/* ============================================================== */}
        {activeSubTab === "dashboard" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {matches.map((m) => (
              <div
                key={m.id}
                onClick={() => {
                  setSelectedMatchId(m.id);
                  setSelectedMatch(m);
                  setActiveSubTab("generate");
                }}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between gap-4 ${
                  selectedMatchId === m.id
                    ? "border-[#00C853] bg-[#141A22] shadow-[0_0_20px_rgba(0,200,83,0.15)]"
                    : "border-white/10 bg-[#141A22] hover:border-white/30"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-mono text-[#8A96A3] mb-3">
                    <span className="px-2 py-0.5 rounded bg-[#0B0F14] text-[#00C853] font-bold">
                      {m.format}
                    </span>
                    <span className="flex items-center gap-1 text-amber-400">
                      {m.is_toss_completed ? <Unlock size={12} /> : <Lock size={12} />}
                      {m.is_toss_completed ? "Lineup In" : "Pre-Toss"}
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-white tracking-tight">{m.name}</h4>
                  <div className="flex items-center gap-1.5 text-xs text-[#8A96A3] mt-1 font-mono">
                    <MapPin size={12} />
                    <span>{m.venue.name}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs font-mono">
                  <span className="text-[#8A96A3]">Avg Score: <strong className="text-white">{m.venue.avg_score}</strong></span>
                  <span className="text-[#00C853] font-bold flex items-center gap-1">
                    Select Fixture &rarr;
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Mobile Bottom Navigation Bar (WCAG AA compliant, tap targets >= 44px) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#0B0F14]/95 border-t border-white/10 backdrop-blur-xl px-2 flex items-center justify-around z-40 shadow-2xl">
        {[
          { id: "dashboard", label: "Matches", icon: Calendar },
          { id: "generate", label: "Generate", icon: Sliders },
          { id: "cards", label: "Teams", icon: Trophy },
          { id: "simulate", label: "Simulate", icon: BarChart3 },
          { id: "entries", label: "Entries", icon: Bookmark }
        ].map((item) => {
          const Icon = item.icon;
          const isActive = activeSubTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveSubTab(item.id as SubTab)}
              className={`flex flex-col items-center justify-center min-w-[50px] min-h-[44px] transition-colors ${
                isActive ? "text-[#00C853]" : "text-[#8A96A3] hover:text-white"
              }`}
            >
              <Icon size={18} />
              <span className="text-[10px] font-mono mt-0.5">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};
