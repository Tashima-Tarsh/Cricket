import React, { useState, useMemo, useEffect } from "react";
import { useMatchContext } from "../context/MatchContext";
import { Player, Lineup, RoleType } from "../types";
import {
  Sliders,
  Trophy,
  Shield,
  Zap,
  CheckCircle2,
  Copy,
  Download,
  Plus,
  Trash2,
  Lock,
  Ban,
  Percent,
  Sparkles,
  RefreshCw,
  Layers,
  Activity,
  AlertCircle
} from "lucide-react";

export const MatchStudio: React.FC = () => {
  const { currentMatch, currentPlayers, activeOvers, setActiveOvers } = useMatchContext();

  // Match Information State
  const [matchTitle, setMatchTitle] = useState(currentMatch.name || "India Women vs Zimbabwe Women, 2nd ODI (Vadodara)");
  const [matchFormat, setMatchFormat] = useState(
    currentMatch.format?.toLowerCase().includes("odi") || currentMatch.format?.toLowerCase().includes("one day")
      ? "ODI"
      : currentMatch.format?.toLowerCase().includes("t10")
      ? "T10"
      : currentMatch.format?.toLowerCase().includes("test")
      ? "Test"
      : "ODI"
  );
  const [homeTeam, setHomeTeam] = useState(currentMatch.teams.home.code || "IND-W");
  const [awayTeam, setAwayTeam] = useState(currentMatch.teams.away.code || "ZIM-W");
  const [venueName, setVenueName] = useState(currentMatch.venue.name || "BCA Stadium, Kotambi, Vadodara");
  const [pitchNature, setPitchNature] = useState<string>(currentMatch.venue.pitch_nature || "Dry Turner");
  const [overs, setOvers] = useState<number>(activeOvers && activeOvers > 0 ? activeOvers : 50);
  const [tossWinner, setTossWinner] = useState<string>(currentMatch.toss.winner || "ZIM-W");
  const [tossDecision, setTossDecision] = useState<"bat" | "bowl">(currentMatch.toss.choice || "bat");

  // Roster State
  const [roster, setRoster] = useState<Player[]>(currentPlayers || []);
  const [lockedIds, setLockedIds] = useState<Set<string>>(new Set());
  const [excludedIds, setExcludedIds] = useState<Set<string>>(new Set());
  const [exposureCaps, setExposureCaps] = useState<Record<string, number>>({});

  // Live Toss Feed State
  const [liveTossData, setLiveTossData] = useState<any>(null);
  const [isFetchingToss, setIsFetchingToss] = useState<boolean>(false);

  // Sync state when context loads
  useEffect(() => {
    if (currentPlayers && currentPlayers.length > 0) {
      setRoster(currentPlayers);
    }
  }, [currentPlayers]);

  useEffect(() => {
    if (currentMatch) {
      setMatchTitle(currentMatch.name || "India Women vs Zimbabwe Women, 2nd ODI (Vadodara)");
      const fmt =
        currentMatch.format?.toLowerCase().includes("odi") || currentMatch.format?.toLowerCase().includes("one day")
          ? "ODI"
          : currentMatch.format?.toLowerCase().includes("t10")
          ? "T10"
          : currentMatch.format?.toLowerCase().includes("test")
          ? "Test"
          : "ODI";
      setMatchFormat(fmt);
      setHomeTeam(currentMatch.teams.home.code || "IND-W");
      setAwayTeam(currentMatch.teams.away.code || "ZIM-W");
      setVenueName(currentMatch.venue.name || "BCA Stadium, Kotambi, Vadodara");
      setPitchNature(currentMatch.venue.pitch_nature || "Dry Turner");
      setTossWinner(currentMatch.toss.winner || "ZIM-W");
      setTossDecision(currentMatch.toss.choice || "bat");
      if (fmt === "ODI" && (!activeOvers || activeOvers === 20)) {
        setOvers(50);
        setActiveOvers(50);
      }
    }
  }, [currentMatch]);

  // Fetch live toss data
  const fetchLiveToss = async () => {
    setIsFetchingToss(true);
    try {
      const matchId = currentMatch.id || "ind_w_vs_zim_w_2026_02";
      const res = await fetch(`/api/live/toss-feed?match_id=${encodeURIComponent(matchId)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.feed) {
          setLiveTossData(data.feed);
        }
      }
    } catch (e) {
      console.warn("Could not retrieve live toss feed", e);
    } finally {
      setIsFetchingToss(false);
    }
  };

  useEffect(() => {
    void fetchLiveToss();
  }, [currentMatch.id]);

  const handleFormatChange = (fmt: string) => {
    setMatchFormat(fmt);
    let targetOvers = 50;
    if (fmt === "ODI") targetOvers = 50;
    else if (fmt === "T10") targetOvers = 10;
    else if (fmt === "Test") targetOvers = 90;
    else targetOvers = 20;
    setOvers(targetOvers);
    setActiveOvers(targetOvers);
  };

  const applyScenarioA = () => {
    // Scenario A: Zimbabwe Bats First -> India bowls first & chases
    setTossWinner("ZIM-W");
    setTossDecision("bat");
    const deepti = roster.find((p) => p.name.toLowerCase().includes("deepti") || p.id.includes("deepti"));
    const mandhana = roster.find((p) => p.name.toLowerCase().includes("mandhana") || p.id.includes("mandhana"));
    const charani = roster.find((p) => p.name.toLowerCase().includes("charani") || p.id.includes("charani"));
    const verma = roster.find((p) => p.name.toLowerCase().includes("verma") || p.id.includes("verma"));

    if (deepti) setPreferredC(deepti.id);
    else if (mandhana) setPreferredC(mandhana.id);

    if (charani) setPreferredVC(charani.id);
    else if (verma) setPreferredVC(verma.id);

    const newLocks = new Set<string>();
    if (deepti) newLocks.add(deepti.id);
    if (charani) newLocks.add(charani.id);
    if (mandhana) newLocks.add(mandhana.id);
    setLockedIds(newLocks);
    setExcludedIds(new Set());
    setSolveStatusMessage("Loaded Scenario A: ZIM Bats 1st, IND Bowls/Chases (Spin choke + Top 3 chase).");
  };

  const applyScenarioB = () => {
    // Scenario B: India Bats First -> Sets 280-320 total
    setTossWinner("IND-W");
    setTossDecision("bat");
    const mandhana = roster.find((p) => p.name.toLowerCase().includes("mandhana") || p.id.includes("mandhana"));
    const rawal = roster.find((p) => p.name.toLowerCase().includes("rawal") || p.id.includes("rawal"));
    const verma = roster.find((p) => p.name.toLowerCase().includes("verma") || p.id.includes("verma"));

    if (mandhana) setPreferredC(mandhana.id);
    if (rawal) setPreferredVC(rawal.id);
    else if (verma) setPreferredVC(verma.id);

    const newLocks = new Set<string>();
    if (mandhana) newLocks.add(mandhana.id);
    if (rawal) newLocks.add(rawal.id);
    if (verma) newLocks.add(verma.id);
    setLockedIds(newLocks);
    setExcludedIds(new Set());
    setSolveStatusMessage("Loaded Scenario B: IND Bats 1st (Setting 280-320+ Total, Mandhana/Rawal anchor).");
  };

  const applyLiveToss = () => {
    if (liveTossData) {
      if (liveTossData.toss_winner) {
        const tw = liveTossData.toss_winner.toLowerCase().includes("india") ? "IND-W" : "ZIM-W";
        setTossWinner(tw);
      }
      if (liveTossData.toss_choice) {
        setTossDecision(liveTossData.toss_choice.toLowerCase().includes("bat") ? "bat" : "bowl");
      }
      setSolveStatusMessage(`Applied official toss: ${liveTossData.toss_statement || "Toss synced"}`);
    }
  };

  // C / VC Selection State
  const [preferredC, setPreferredC] = useState<string>("AUTO");
  const [preferredVC, setPreferredVC] = useState<string>("AUTO");
  const [allowChalkCVC, setAllowChalkCVC] = useState<boolean>(false);

  // Credit Band & Optimization Settings
  const [creditStrategy, setCreditStrategy] = useState<"79-85" | "87-89" | "90-95" | "custom">("79-85");
  const [customMinCredits, setCustomMinCredits] = useState<number>(78.0);
  const [customMaxCredits, setCustomMaxCredits] = useState<number>(86.0);
  const [numTeams, setNumTeams] = useState<number>(10);
  const [maxOverlap, setMaxOverlap] = useState<number>(8);
  const [minDifferentials, setMinDifferentials] = useState<number>(2);
  const [riskMode, setRiskMode] = useState<"BALANCED" | "HIGH_CEILING" | "DIFFERENTIAL_HEAVY">("HIGH_CEILING");
  const [useCopula, setUseCopula] = useState<boolean>(true);

  // Solver Status & Results
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [solvedLineups, setSolvedLineups] = useState<Lineup[]>([]);
  const [solveStatusMessage, setSolveStatusMessage] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // New Player Form State
  const [newPlayerName, setNewPlayerName] = useState("");
  const [newPlayerTeam, setNewPlayerTeam] = useState(homeTeam);
  const [newPlayerRole, setNewPlayerRole] = useState<RoleType>("BAT");
  const [newPlayerCredits, setNewPlayerCredits] = useState(8.5);
  const [newPlayerOwn, setNewPlayerOwn] = useState(35.0);

  // Update teams if changed
  const teamsList = useMemo(() => {
    const list = Array.from(new Set(roster.map((p) => p.team).filter(Boolean)));
    return list.length >= 2 ? list : [homeTeam, awayTeam];
  }, [roster, homeTeam, awayTeam]);

  // Lock / Exclude Handlers
  const toggleLock = (id: string) => {
    setLockedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        setExcludedIds((e) => { const ne = new Set(e); ne.delete(id); return ne; });
      }
      return next;
    });
  };

  const toggleExclude = (id: string) => {
    setExcludedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        setLockedIds((l) => { const nl = new Set(l); nl.delete(id); return nl; });
      }
      return next;
    });
  };

  const updatePlayerField = (id: string, field: keyof Player, value: any) => {
    setRoster((prev) =>
      prev.map((p) => (p.id === id ? { ...p, [field]: value } : p))
    );
  };

  const addCustomPlayer = () => {
    if (!newPlayerName.trim()) return;
    const newId = `custom_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    const created: Player = {
      id: newId,
      name: newPlayerName.trim(),
      team: newPlayerTeam,
      role: newPlayerRole,
      credits: Number(newPlayerCredits),
      batting_style: "RHB",
      batting_order: 5,
      expected_overs: newPlayerRole === "BOWL" || newPlayerRole === "AR" ? 3.0 : 0.0,
      projected_ownership: Number(newPlayerOwn),
      projected_points: Number(newPlayerCredits) * 5.0,
      ceiling_score: Number(newPlayerCredits) * 9.0,
      floor_score: 10.0,
      is_confirmed_xi: true,
      stats: {
        matches: 10,
        runs: 200,
        balls_faced: 140,
        strike_rate: 142.8,
        batting_avg: 28.5,
        wickets: newPlayerRole === "BOWL" ? 12 : 0,
        overs_bowled: newPlayerRole === "BOWL" ? 35 : 0,
        economy: 7.4,
        bowling_sr: 17.5,
        dot_ball_pct: 42.0,
        boundary_pct: 18.0,
        recent_scores: [35, 42, 18, 55],
        recent_wickets: [2, 1, 3, 0],
        recent_fantasy_pts: [45, 60, 30, 75],
        avg_fantasy_pts: Number(newPlayerCredits) * 5.0,
        ceiling_pts: Number(newPlayerCredits) * 9.0,
        floor_pts: 10.0
      }
    };
    setRoster((prev) => [...prev, created]);
    setNewPlayerName("");
  };

  const deletePlayer = (id: string) => {
    setRoster((prev) => prev.filter((p) => p.id !== id));
    setLockedIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
    setExcludedIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
  };

  // Solve Action
  const handleSolveLineups = async () => {
    setIsSolving(true);
    setSolveStatusMessage(null);
    try {
      const minCr = creditStrategy === "custom" ? customMinCredits : (creditStrategy === "79-85" ? 79.0 : creditStrategy === "87-89" ? 87.0 : 90.0);
      const maxCr = creditStrategy === "custom" ? customMaxCredits : (creditStrategy === "79-85" ? 85.0 : creditStrategy === "87-89" ? 89.0 : 95.0);

      const params = new URLSearchParams({
        teams: String(numTeams),
        max_overlap: String(maxOverlap),
        spots: "700000",
        credit_strategy: creditStrategy === "custom" ? "custom" : creditStrategy,
        min_credits: String(minCr),
        max_credits: String(maxCr),
        risk: riskMode,
        match_id: currentMatch.id,
        overs: String(overs)
      });

      if (preferredC && preferredC !== "AUTO") params.set("captain", preferredC);
      if (preferredVC && preferredVC !== "AUTO") params.set("vice_captain", preferredVC);
      if (lockedIds.size > 0) params.set("locked", Array.from(lockedIds).join(","));
      if (excludedIds.size > 0) params.set("excluded", Array.from(excludedIds).join(","));

      const exposureEntries = Object.entries(exposureCaps).filter(([_, v]) => v < 100);
      if (exposureEntries.length > 0) {
        params.set("exposure", exposureEntries.map(([k, v]) => `${k}:${v}`).join(","));
      }

      const res = await fetch(`/api/ortools/optimize?${params.toString()}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Solver failed to find feasible lineup under given constraints.");
      }
      const data = await res.json();
      if (Array.isArray(data.lineups)) {
        setSolvedLineups(data.lineups);
        setSolveStatusMessage(`Successfully generated ${data.lineups.length} Grand League lineups (${useCopula ? "Copula Correlated" : "Vectorized"}).`);
      }
    } catch (e: any) {
      setSolveStatusMessage(`Optimization Notice: ${e.message || "Lineup generation could not converge."}`);
    } finally {
      setIsSolving(false);
    }
  };

  const copyLineupText = (lineup: Lineup, index: number) => {
    const cName = lineup.captain?.name || "Captain";
    const vcName = lineup.vice_captain?.name || "Vice Captain";
    const playersStr = (lineup.players || []).map((p) => p.name).join(", ");
    const text = `🏆 STRIKE//OS ${lineup.team_name || `Lineup #${index + 1}`}\n👑 C: ${cName} (2x)\n⚡ VC: ${vcName} (1.5x)\nXI: ${playersStr}\nTotal Credits: ${lineup.total_credits}/100 | Proj Points: ${lineup.projected_points}`;
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    });
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Tactical Control */}
      <div className="rounded-2xl border border-stone-300 bg-white p-6 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-stone-200">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-stone-100 text-stone-900 border border-stone-300">
              <Sliders size={24} />
            </div>
            <div>
              <div className="text-xs font-mono text-stone-500 font-bold uppercase tracking-wider">
                TACTICAL CONTROL STUDIO &bull; ICC 270973 MATCH CENTER
              </div>
              <h1 className="text-2xl font-bold text-stone-900 tracking-tight">
                Match Setup, Roster & C/VC Strategy Center
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSolveLineups}
              disabled={isSolving}
              className="px-6 py-2.5 rounded-xl bg-stone-900 hover:bg-stone-800 text-white font-mono text-xs font-bold flex items-center gap-2 shadow transition-all"
            >
              {isSolving ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
              <span>{isSolving ? "SOLVING CP-SAT..." : "GENERATE LINEUPS"}</span>
            </button>
          </div>
        </div>

        {/* Live Toss Telemetry & Pre-Toss Scenarios Quick-Action Bar */}
        <div className="p-4 rounded-xl bg-stone-50 border border-stone-300 space-y-3 font-mono text-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-stone-200 pb-2.5">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${
                liveTossData?.is_toss_done ? "bg-emerald-600 text-white" : "bg-amber-500 text-stone-900"
              }`}>
                {liveTossData?.is_toss_done ? "TOSS CONCLUDED" : "PRE-TOSS PROVISIONAL"}
              </span>
              <span className="text-stone-700 font-bold">
                {liveTossData?.toss_statement || "Toss scheduled 30 min before match start (13:30 IST)."}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchLiveToss}
                disabled={isFetchingToss}
                className="px-2.5 py-1 rounded bg-white border border-stone-300 hover:bg-stone-100 text-stone-700 flex items-center gap-1 text-[11px] font-bold"
              >
                <RefreshCw size={12} className={isFetchingToss ? "animate-spin" : ""} />
                <span>{isFetchingToss ? "Checking..." : "Refresh Toss Feed"}</span>
              </button>
              {liveTossData?.is_toss_done && (
                <button
                  onClick={applyLiveToss}
                  className="px-2.5 py-1 rounded bg-emerald-700 hover:bg-emerald-800 text-white flex items-center gap-1 text-[11px] font-bold"
                >
                  <CheckCircle2 size={12} />
                  <span>Sync Toss to Studio</span>
                </button>
              )}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
            <div className="text-[11px] text-stone-600">
              <span className="font-bold text-stone-800">Venue:</span> {venueName} &bull;{" "}
              <span className="font-bold text-stone-800">Pitch:</span> {pitchNature} &bull;{" "}
              <span className="font-bold text-stone-800">Format:</span> {matchFormat} ({overs} Ov)
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase font-bold text-stone-500">Pre-Toss Scenarios:</span>
              <button
                onClick={applyScenarioA}
                className="px-2.5 py-1 rounded bg-emerald-100 hover:bg-emerald-200 text-emerald-900 border border-emerald-300 font-bold text-[11px] transition-colors"
                title="Zimbabwe Bats 1st, India Bowls First & Chases"
              >
                🟢 Scenario A (ZIM Bats 1st)
              </button>
              <button
                onClick={applyScenarioB}
                className="px-2.5 py-1 rounded bg-blue-100 hover:bg-blue-200 text-blue-900 border border-blue-300 font-bold text-[11px] transition-colors"
                title="India Bats 1st, Sets 280-320 Total"
              >
                🔵 Scenario B (IND Bats 1st)
              </button>
            </div>
          </div>
        </div>

        {solveStatusMessage && (
          <div className="p-3.5 rounded-xl bg-stone-100 text-stone-800 text-xs font-mono border border-stone-300 flex items-center gap-2">
            <AlertCircle size={16} className="text-stone-700" />
            <span>{solveStatusMessage}</span>
          </div>
        )}
      </div>

      {/* 2. Grid: Match Details & Optimization Settings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Match & Conditions Setup */}
        <div className="rounded-2xl border border-stone-300 bg-white p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-stone-900 font-mono uppercase tracking-wide flex items-center gap-2 pb-2 border-b border-stone-200">
            <Activity size={16} /> 1. Match & Pitch Telemetry
          </h2>
          <div className="space-y-3 text-xs font-mono">
            <div>
              <label className="text-stone-600 block mb-1">Match Title</label>
              <input
                type="text"
                value={matchTitle}
                onChange={(e) => setMatchTitle(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900 font-bold focus:outline-none focus:border-stone-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-stone-600 block mb-1">Home Team</label>
                <input
                  type="text"
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value.toUpperCase())}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900 font-bold"
                />
              </div>
              <div>
                <label className="text-stone-600 block mb-1">Away Team</label>
                <input
                  type="text"
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value.toUpperCase())}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900 font-bold"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-stone-600 block mb-1">Format</label>
                <select
                  value={matchFormat}
                  onChange={(e) => handleFormatChange(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value="ODI">One-Day 50 Overs (ODI)</option>
                  <option value="T20">T20 International (20 Ov)</option>
                  <option value="WT20">Women's T20 (4 Outfielders)</option>
                  <option value="T10">T10 Sprint (10 Ov)</option>
                  <option value="Test">Test Match (90 Ov/day)</option>
                </select>
              </div>
              <div>
                <label className="text-stone-600 block mb-1">Pitch Profile</label>
                <select
                  value={pitchNature}
                  onChange={(e) => setPitchNature(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value="Dry Turner">Dry Turner (Spin Choke - BCA Vadodara)</option>
                  <option value="Balanced">Balanced Deck</option>
                  <option value="Flat Highway">Flat Highway (Batting Par 280+)</option>
                  <option value="Green Seam">Green Seam (Pace & Bounce)</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-stone-600">Match Length (Weather / DLS):</label>
                <span className="font-bold text-stone-900">{overs} Overs per side</span>
              </div>
              <input
                type="range"
                min="5"
                max={matchFormat === "ODI" ? 50 : matchFormat === "T10" ? 10 : matchFormat === "Test" ? 450 : 20}
                step="1"
                value={overs}
                onChange={(e) => {
                  const ov = Number(e.target.value);
                  setOvers(ov);
                  setActiveOvers(ov);
                }}
                className="w-full accent-stone-900"
              />
              <div className="text-[10px] text-stone-500 mt-1">
                {matchFormat === "ODI" ? (
                  <span>
                    Full 50-over ODI: PP1 (1-10 ov), PP2 (11-40 ov), PP3 (41-50 ov) &bull; Max 10 overs per bowler.
                  </span>
                ) : matchFormat === "Test" ? (
                  <span>Test Match: 90 overs/day, multi-innings, declaration & follow-on rules &bull; No bowler quota.</span>
                ) : matchFormat === "T10" ? (
                  <span>T10 Sprint: PP 1-3 overs &bull; Bowlers max 2 overs each.</span>
                ) : overs < 20 ? (
                  <span>
                    Shortened match: Powerplay {overs <= 9 ? "1.3 - 2.4 ov" : `${Math.round(overs * 0.3)} ov`} &bull; Bowlers max {overs <= 9 ? "2 ov (2+2+1 allocation)" : `${Math.ceil(overs / 5)} ov`}.
                  </span>
                ) : (
                  <span>Full 20-over match: Standard 6-over powerplay &bull; Max 4 overs per bowler.</span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-stone-200">
              <div>
                <label className="text-stone-600 block mb-1">Toss Winner</label>
                <select
                  value={tossWinner}
                  onChange={(e) => setTossWinner(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value={homeTeam}>{homeTeam}</option>
                  <option value={awayTeam}>{awayTeam}</option>
                </select>
              </div>
              <div>
                <label className="text-stone-600 block mb-1">Elected To</label>
                <select
                  value={tossDecision}
                  onChange={(e) => setTossDecision(e.target.value as any)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value="bowl">Bowl First (Chase + Pitch deterioration)</option>
                  <option value="bat">Bat First (Set Total)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: C / VC & Strategy Weights */}
        <div className="rounded-2xl border border-stone-300 bg-white p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-stone-900 font-mono uppercase tracking-wide flex items-center gap-2 pb-2 border-b border-stone-200">
            <Trophy size={16} /> 2. C & VC Assignment Center
          </h2>
          <div className="space-y-3 text-xs font-mono">
            <div>
              <label className="text-stone-600 block mb-1">Preferred Captain (2.0x Points)</label>
              <select
                value={preferredC}
                onChange={(e) => setPreferredC(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-2 text-stone-900 font-bold"
              >
                <option value="AUTO">⚡ AUTO (Optimize for Solitary 1st Rank Ceiling)</option>
                {roster.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.role} • {p.team} • {p.credits} Cr • {p.projected_ownership}% Own)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-stone-600 block mb-1">Preferred Vice-Captain (1.5x Points)</label>
              <select
                value={preferredVC}
                onChange={(e) => setPreferredVC(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-2 text-stone-900 font-bold"
              >
                <option value="AUTO">⚡ AUTO (Optimize Correlation & Score Complement)</option>
                {roster
                  .filter((p) => p.id !== preferredC)
                  .map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.role} • {p.team} • {p.credits} Cr • {p.projected_ownership}% Own)
                    </option>
                  ))}
              </select>
            </div>

            <div className="pt-2 border-t border-stone-200 space-y-2">
              <label className="text-stone-600 block">C / VC Combinatorics Matrix</label>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="chalkCVC"
                  checked={allowChalkCVC}
                  onChange={(e) => setAllowChalkCVC(e.target.checked)}
                  className="rounded border-stone-300 accent-stone-900"
                />
                <label htmlFor="chalkCVC" className="text-stone-700 cursor-pointer">
                  Allow #1 Chalk C with #2 Chalk VC (Standard safe pair)
                </label>
              </div>
              <p className="text-[10px] text-stone-500">
                Leaving unchecked enforces contrarian separation to avoid massive duplicate collisions.
              </p>
            </div>

            <div className="pt-2 border-t border-stone-200">
              <label className="text-stone-600 block mb-1">Contest Type & Risk Calibration</label>
              <select
                value={riskMode}
                onChange={(e) => setRiskMode(e.target.value as any)}
                className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
              >
                <option value="HIGH_CEILING">Mega Contest (500k - 700k+ Spots • Max 99th Percentile)</option>
                <option value="DIFFERENTIAL_HEAVY">Ultra Contrarian (4+ Differentials • Solo Winner)</option>
                <option value="BALANCED">Mini-GL / Medium Field (10k - 50k Spots)</option>
              </select>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-stone-200">
              <span className="text-stone-600">Gaussian Copula Simulation:</span>
              <button
                type="button"
                onClick={() => setUseCopula(!useCopula)}
                className={`px-2.5 py-1 rounded text-[11px] font-bold ${
                  useCopula ? "bg-stone-900 text-white" : "bg-stone-200 text-stone-600"
                }`}
              >
                {useCopula ? "COPULA ACTIVE" : "STANDARD MC"}
              </button>
            </div>
          </div>
        </div>

        {/* Card 3: Credit Percentage & Portfolio Constraints */}
        <div className="rounded-2xl border border-stone-300 bg-white p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-stone-900 font-mono uppercase tracking-wide flex items-center gap-2 pb-2 border-b border-stone-200">
            <Percent size={16} /> 3. Credit Band & Portfolio Rules
          </h2>
          <div className="space-y-3 text-xs font-mono">
            <div>
              <label className="text-stone-600 block mb-1">Credit Allocation Strategy</label>
              <select
                value={creditStrategy}
                onChange={(e) => setCreditStrategy(e.target.value as any)}
                className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-2 text-stone-900 font-bold"
              >
                <option value="79-85">79.0 – 85.0 Cr (Leaves 15+ Cr Unspent, 0 Collisions)</option>
                <option value="87-89">87.0 – 89.0 Cr (Balanced High Ceiling)</option>
                <option value="90-95">90.0 – 95.0 Cr (Standard Full Budget)</option>
                <option value="custom">Custom Credit Min & Max Range</option>
              </select>
            </div>

            {creditStrategy === "custom" && (
              <div className="p-3 rounded-lg bg-stone-50 border border-stone-300 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-stone-600">Min Credits:</span>
                  <span className="font-bold text-stone-900">{customMinCredits} Cr</span>
                </div>
                <input
                  type="range"
                  min="65.0"
                  max="95.0"
                  step="0.5"
                  value={customMinCredits}
                  onChange={(e) => setCustomMinCredits(Number(e.target.value))}
                  className="w-full accent-stone-900"
                />

                <div className="flex justify-between items-center">
                  <span className="text-stone-600">Max Credits:</span>
                  <span className="font-bold text-stone-900">{customMaxCredits} Cr</span>
                </div>
                <input
                  type="range"
                  min="75.0"
                  max="100.0"
                  step="0.5"
                  value={customMaxCredits}
                  onChange={(e) => setCustomMaxCredits(Number(e.target.value))}
                  className="w-full accent-stone-900"
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-stone-600 block mb-1">Number of Teams</label>
                <select
                  value={numTeams}
                  onChange={(e) => setNumTeams(Number(e.target.value))}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value={1}>1 Team (Solo)</option>
                  <option value={5}>5 Teams</option>
                  <option value={10}>10 Teams</option>
                  <option value={20}>20 Teams (Full GPP Portfolio)</option>
                </select>
              </div>
              <div>
                <label className="text-stone-600 block mb-1">Max Overlap</label>
                <select
                  value={maxOverlap}
                  onChange={(e) => setMaxOverlap(Number(e.target.value))}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 text-stone-900"
                >
                  <option value={6}>6 Players (Max Diversity)</option>
                  <option value={7}>7 Players</option>
                  <option value={8}>8 Players (Standard)</option>
                  <option value={9}>9 Players</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-stone-600">Sub-35% Differentials per Team:</label>
                <span className="font-bold text-stone-900">{minDifferentials} Players</span>
              </div>
              <input
                type="range"
                min="0"
                max="4"
                step="1"
                value={minDifferentials}
                onChange={(e) => setMinDifferentials(Number(e.target.value))}
                className="w-full accent-stone-900"
              />
            </div>

            <div className="pt-2 border-t border-stone-200 flex items-center justify-between text-stone-600">
              <span>Active Squad Size:</span>
              <span className="font-bold text-stone-900">{roster.length} Players</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Interactive Roster Manager & Syndicate Exposure Table */}
      <div className="rounded-2xl border border-stone-300 bg-white p-6 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-stone-200">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-stone-100 border border-stone-300 text-stone-900">
              <Layers size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-stone-900 font-mono uppercase tracking-wide">
                4. Match Player Pool & Syndicate Exposure Deck
              </h2>
              <p className="text-xs text-stone-500 font-mono">
                Edit credits, adjust projected ownership percentages, or lock / ban players for the CP-SAT optimizer.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-stone-600">
              Locked: <strong className="text-emerald-700">{lockedIds.size}</strong> &bull; Banned: <strong className="text-rose-700">{excludedIds.size}</strong>
            </span>
          </div>
        </div>

        {/* Quick Add Player Strip */}
        <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 grid grid-cols-1 sm:grid-cols-6 gap-2 text-xs font-mono items-center">
          <div className="sm:col-span-2">
            <input
              type="text"
              placeholder="Player Name (e.g. V. Kohli)"
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              className="w-full bg-white border border-stone-300 rounded px-2.5 py-1.5 text-stone-900"
            />
          </div>
          <div>
            <select
              value={newPlayerTeam}
              onChange={(e) => setNewPlayerTeam(e.target.value)}
              className="w-full bg-white border border-stone-300 rounded px-2 py-1.5 text-stone-900"
            >
              {teamsList.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={newPlayerRole}
              onChange={(e) => setNewPlayerRole(e.target.value as any)}
              className="w-full bg-white border border-stone-300 rounded px-2 py-1.5 text-stone-900"
            >
              <option value="BAT">BAT</option>
              <option value="BOWL">BOWL</option>
              <option value="AR">AR</option>
              <option value="WK">WK</option>
            </select>
          </div>
          <div className="flex items-center gap-1">
            <input
              type="number"
              step="0.5"
              min="5"
              max="11"
              value={newPlayerCredits}
              onChange={(e) => setNewPlayerCredits(Number(e.target.value))}
              placeholder="Credits"
              className="w-16 bg-white border border-stone-300 rounded px-2 py-1.5 text-stone-900"
            />
            <span className="text-[11px] text-stone-500">Cr</span>
          </div>
          <div>
            <button
              onClick={addCustomPlayer}
              className="w-full px-3 py-1.5 rounded bg-stone-900 text-white font-bold flex items-center justify-center gap-1 hover:bg-stone-800"
            >
              <Plus size={14} /> ADD
            </button>
          </div>
        </div>

        {/* Players Roster Table */}
        <div className="overflow-x-auto max-h-96 overflow-y-auto border border-stone-200 rounded-xl">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-stone-100 text-stone-700 sticky top-0 border-b border-stone-200">
              <tr>
                <th className="py-2.5 px-3">Player</th>
                <th className="py-2.5 px-2">Team</th>
                <th className="py-2.5 px-2">Role</th>
                <th className="py-2.5 px-2">Credits</th>
                <th className="py-2.5 px-2">Projected Own %</th>
                <th className="py-2.5 px-2">Proj Pts</th>
                <th className="py-2.5 px-3 text-center">Lock / Ban</th>
                <th className="py-2.5 px-2 text-center">Exposure</th>
                <th className="py-2.5 px-2 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-200 text-stone-800">
              {roster.map((p) => {
                const isLocked = lockedIds.has(p.id);
                const isExcluded = excludedIds.has(p.id);
                const exposure = exposureCaps[p.id] ?? 100;

                return (
                  <tr
                    key={p.id}
                    className={`transition-colors ${
                      isLocked ? "bg-emerald-50" : isExcluded ? "bg-rose-50 opacity-60" : "hover:bg-stone-50"
                    }`}
                  >
                    <td className="py-2 px-3 font-bold text-stone-900">{p.name}</td>
                    <td className="py-2 px-2">
                      <span className="px-1.5 py-0.5 rounded bg-stone-100 text-stone-800 border border-stone-200 font-bold">
                        {p.team}
                      </span>
                    </td>
                    <td className="py-2 px-2 font-bold">{p.role}</td>
                    <td className="py-2 px-2">
                      <input
                        type="number"
                        step="0.5"
                        min="5.0"
                        max="11.0"
                        value={p.credits}
                        onChange={(e) => updatePlayerField(p.id, "credits", Number(e.target.value))}
                        className="w-14 bg-white border border-stone-300 rounded px-1.5 py-0.5 text-stone-900"
                      />
                    </td>
                    <td className="py-2 px-2">
                      <input
                        type="number"
                        min="1"
                        max="99"
                        value={p.projected_ownership}
                        onChange={(e) => updatePlayerField(p.id, "projected_ownership", Number(e.target.value))}
                        className="w-14 bg-white border border-stone-300 rounded px-1.5 py-0.5 text-stone-900"
                      />
                      %
                    </td>
                    <td className="py-2 px-2 font-bold text-stone-700">
                      {Math.round(p.projected_points || 40)} pts
                    </td>
                    <td className="py-2 px-3 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          type="button"
                          onClick={() => toggleLock(p.id)}
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            isLocked ? "bg-emerald-600 text-white font-extrabold" : "bg-stone-200 text-stone-700 hover:bg-stone-300"
                          }`}
                        >
                          {isLocked ? "LOCKED" : "LOCK"}
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleExclude(p.id)}
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            isExcluded ? "bg-rose-600 text-white font-extrabold" : "bg-stone-200 text-stone-700 hover:bg-stone-300"
                          }`}
                        >
                          {isExcluded ? "BANNED" : "BAN"}
                        </button>
                      </div>
                    </td>
                    <td className="py-2 px-2 text-center">
                      {!isExcluded && (
                        <div className="flex items-center justify-center gap-1">
                          <input
                            type="range"
                            min="10"
                            max="100"
                            step="10"
                            value={exposure}
                            onChange={(e) => setExposureCaps((prev) => ({ ...prev, [p.id]: Number(e.target.value) }))}
                            className="w-16 accent-stone-900"
                          />
                          <span className="text-[10px] text-stone-600 w-8">{exposure}%</span>
                        </div>
                      )}
                    </td>
                    <td className="py-2 px-2 text-center">
                      <button
                        onClick={() => deletePlayer(p.id)}
                        className="p-1 rounded text-stone-400 hover:text-rose-600"
                        title="Remove player from pool"
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Solved Lineups Showcase */}
      {solvedLineups.length > 0 && (
        <div className="rounded-2xl border border-stone-300 bg-white p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-stone-200">
            <div>
              <div className="text-xs font-mono text-stone-500 font-bold uppercase tracking-wider">
                PORTFOLIO RESULTS
              </div>
              <h2 className="text-lg font-bold text-stone-900 font-mono">
                {solvedLineups.length} Mathematically Solved Grand League Lineups
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <a
                href={`/api/export/csv?format=dream11&teams=${solvedLineups.length}&credit_strategy=${creditStrategy}&match_id=${currentMatch.id}`}
                target="_blank"
                rel="noreferrer"
                className="px-3.5 py-1.5 rounded-lg bg-stone-900 hover:bg-stone-800 text-white text-xs font-mono font-bold flex items-center gap-1.5 shadow"
              >
                <Download size={13} /> DREAM11 CSV
              </a>
              <a
                href={`/api/export/csv?format=my11circle&teams=${solvedLineups.length}&credit_strategy=${creditStrategy}&match_id=${currentMatch.id}`}
                target="_blank"
                rel="noreferrer"
                className="px-3.5 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-xs font-mono font-bold flex items-center gap-1.5"
              >
                <Download size={13} /> MY11CIRCLE CSV
              </a>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {solvedLineups.map((lineup, idx) => {
              const cName = lineup.captain?.name || "Captain";
              const vcName = lineup.vice_captain?.name || "Vice Captain";

              return (
                <div
                  key={idx}
                  className="rounded-xl border border-stone-300 bg-stone-50 p-4 space-y-3 relative hover:shadow transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-stone-900 font-mono">
                        {lineup.team_name || `Lineup #${idx + 1}`}
                      </span>
                      <div className="text-[10px] text-stone-500 font-mono">
                        Credits: {lineup.total_credits} / 100 &bull; Own: {lineup.total_ownership_sum}%
                      </div>
                    </div>
                    <button
                      onClick={() => copyLineupText(lineup, idx)}
                      className="px-2 py-1 rounded bg-white border border-stone-300 text-stone-700 text-[10px] font-mono hover:bg-stone-100 flex items-center gap-1"
                    >
                      <Copy size={12} />
                      <span>{copiedIndex === idx ? "COPIED" : "COPY"}</span>
                    </button>
                  </div>

                  {/* C / VC Pill */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2 rounded bg-amber-50 border border-amber-200 text-amber-900">
                      <span className="text-[10px] font-bold block text-amber-700">👑 CAPTAIN (2.0x):</span>
                      <strong className="truncate block">{cName}</strong>
                    </div>
                    <div className="p-2 rounded bg-cyan-50 border border-cyan-200 text-cyan-900">
                      <span className="text-[10px] font-bold block text-cyan-700">⚡ VICE-CAPTAIN (1.5x):</span>
                      <strong className="truncate block">{vcName}</strong>
                    </div>
                  </div>

                  {/* Player list */}
                  <div className="space-y-1 pt-1 border-t border-stone-200">
                    <div className="text-[10px] text-stone-500 font-mono uppercase">Starting 11:</div>
                    <div className="flex flex-wrap gap-1">
                      {(lineup.players || []).map((p) => (
                        <span
                          key={p.id}
                          className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                            p.id === lineup.captain?.id
                              ? "bg-amber-100 text-amber-900 border-amber-300 font-bold"
                              : p.id === lineup.vice_captain?.id
                              ? "bg-cyan-100 text-cyan-900 border-cyan-300 font-bold"
                              : "bg-white text-stone-800 border-stone-200"
                          }`}
                        >
                          {p.name}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Expected metric */}
                  <div className="pt-2 border-t border-stone-200 flex items-center justify-between text-xs font-mono text-stone-600">
                    <span>Expected Points: <strong className="text-stone-900">{lineup.projected_points}</strong></span>
                    <span>Differentials: <strong className="text-stone-900">{lineup.differential_count}</strong></span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

