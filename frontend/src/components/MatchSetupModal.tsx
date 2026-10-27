import { useDialog } from "../hooks/useDialog";
import React, { useState, useEffect } from "react";
import { MatchInfo, Player } from "../types";
import { 
  Radio, 
  X, 
  CheckCircle2, 
  RefreshCw, 
  Sliders, 
  Zap, 
  Globe, 
  Database,
  Layers
} from "lucide-react";

interface LiveMatchItem {
  state?: string;
  data_provenance?: string;
  id: string;
  title: string;
  team_home: string;
  team_away: string;
  score_home?: string;
  score_away?: string;
  status: string;
  provider: string;
  details: string;
  pitch_report?: string;
  toss?: string;
  match_date?: string;
  category?: string;
  category_label?: string;
  format?: string;
  venue?: string;
}


interface MatchSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMatch: MatchInfo;
  onApplyMatch: (newMatch: MatchInfo, updatedPlayers?: Player[]) => void;
  players: Player[];
}

export const MatchSetupModal: React.FC<MatchSetupModalProps> = ({
  isOpen,
  onClose,
  currentMatch,
  onApplyMatch,
  players
}) => {
  const dialogRef = useDialog(isOpen, onClose);
  const [adminToken, setAdminToken] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const toXI = (code: string) => players.filter(p => p.team === code).map((p, i) => ({
    name: p.name, role: p.role, credits: p.credits, order: i + 1,
    bat_hand: p.batting_style, bowl_style: p.bowling_style || "Unknown"
  }));
  const [homeXI, setHomeXI] = useState(() => toXI(currentMatch.teams.home.code));
  const [awayXI, setAwayXI] = useState(() => toXI(currentMatch.teams.away.code));
  const [feedError, setFeedError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"series_fixtures" | "live_sync" | "custom_setup">("live_sync");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [liveMatches, setLiveMatches] = useState<LiveMatchItem[]>([]);
  const [seriesFixtures, setSeriesFixtures] = useState<MatchInfo[]>([]);
  const [cricsheetMatches, setCricsheetMatches] = useState<any[]>([]);
  const [isLoadingLive, setIsLoadingLive] = useState<boolean>(false);
  const [isLoadingSeries, setIsLoadingSeries] = useState<boolean>(false);


  // Custom setup form fields
  const [matchName, setMatchName] = useState(currentMatch.name);
  const [teamHomeName, setTeamHomeName] = useState(currentMatch.teams.home.name);
  const [teamHomeCode, setTeamHomeCode] = useState(currentMatch.teams.home.code);
  const [teamAwayName, setTeamAwayName] = useState(currentMatch.teams.away.name);
  const [teamAwayCode, setTeamAwayCode] = useState(currentMatch.teams.away.code);
  const [tossWinner, setTossWinner] = useState(currentMatch.toss.winner);
  const [tossChoice, setTossChoice] = useState<"bat" | "bowl">(currentMatch.toss.choice);
  const [pitchReport, setPitchReport] = useState(currentMatch.venue.pitch_nature);
  const [avgFirstInnings, setAvgFirstInnings] = useState(currentMatch.venue.avg_first_innings);
  const [dewFactor, setDewFactor] = useState(currentMatch.venue.dew_factor);

  const fetchSeriesFixtures = async () => {
    setIsLoadingSeries(true);
    try {
      const [res, cricRes] = await Promise.all([
        fetch("/api/series/fixtures"),
        fetch("/api/cricsheet/matches")
      ]);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.fixtures)) setSeriesFixtures(data.fixtures);
      }
      if (cricRes.ok) {
        const cricData = await cricRes.json();
        if (Array.isArray(cricData.matches)) setCricsheetMatches(cricData.matches);
      }
    } catch {
      // Standby fallback
    } finally {
      setIsLoadingSeries(false);
    }
  };

  const handleLoadCricsheetMatch = async (matchId: string) => {
    // Historical scorecards lack contest prices and verified fantasy roles.
    window.open(`/api/cricsheet/scorecard/${encodeURIComponent(matchId)}`, "_blank", "noopener,noreferrer");
  };

  const fetchLiveMatches = async () => {
    setIsLoadingLive(true); setFeedError(null); setLiveMatches([]);
    try {
      const response = await fetch("/api/live/matches", {signal: AbortSignal.timeout(12000)});
      if (!response.ok) throw new Error(`Live feed unavailable (${response.status}).`);
      const data = await response.json();
      if (Array.isArray(data.matches)) data.matches = data.matches.filter((match: LiveMatchItem) => match.data_provenance !== "HISTORICAL_SIMULATION");
      if (!Array.isArray(data.matches) || !data.matches.length) throw new Error("No live fixtures are available from the feed. No example matches have been substituted.");
      setLiveMatches(data.matches);
    } catch (error) { setFeedError(error instanceof Error ? error.message : "Live feed could not be loaded."); }
    finally { setIsLoadingLive(false); }
  };

  useEffect(() => {
    if (isOpen) {
      setHomeXI(toXI(currentMatch.teams.home.code));
      setAwayXI(toXI(currentMatch.teams.away.code));
      setMatchName(currentMatch.name);
      setTeamHomeName(currentMatch.teams.home.name); setTeamHomeCode(currentMatch.teams.home.code);
      setTeamAwayName(currentMatch.teams.away.name); setTeamAwayCode(currentMatch.teams.away.code);
      setTossWinner(currentMatch.toss.winner); setTossChoice(currentMatch.toss.choice);
      setPitchReport(currentMatch.venue.pitch_nature); setAvgFirstInnings(currentMatch.venue.avg_first_innings);
      setDewFactor(currentMatch.venue.dew_factor); setAdminToken("");
      fetchSeriesFixtures();
      fetchLiveMatches();
    }
  }, [isOpen]);

  // Load a series fixture directly
  const handleLoadSeriesFixture = (fixture: MatchInfo) => {
    onApplyMatch(fixture);
    onClose();
  };

  // Live listings are discovery references only; they cannot be trusted XI imports.
  const handleLoadLiveMatch = (item: LiveMatchItem) => {
    setMatchName(item.title);
    setTeamHomeName(item.team_home || "");
    setTeamAwayName(item.team_away || "");
    setTeamHomeCode("");
    setTeamAwayCode("");
    setHomeXI([]);
    setAwayXI([]);
    setActiveTab("custom_setup");
    setFeedError("A live match reference is not a confirmed XI. Enter both teams, original player roles, credits and complete XIs to continue; no players or prices are generated.");
  };

  // Submit custom match form
  const handleSaveCustomMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    const updatedMatch: MatchInfo = {
      ...currentMatch,
      id: `custom_${Date.now()}`,
      name: matchName,
      teams: {
        home: {
          name: teamHomeName,
          code: teamHomeCode.toUpperCase(),
          score: "0/0",
          overs: "0.0"
        },
        away: {
          name: teamAwayName,
          code: teamAwayCode.toUpperCase(),
          score: "0/0",
          overs: "0.0"
        }
      },
      toss: {
        winner: tossWinner,
        choice: tossChoice,
        statement: `${tossWinner} won the toss and elected to ${tossChoice} first.`
      },
      venue: {
        ...currentMatch.venue,
        avg_first_innings: Number(avgFirstInnings),
        dew_factor: Number(dewFactor),
        pitch_nature: pitchReport
      }
    };

    setIsSaving(true); setFeedError(null);
    try {
      const response = await fetch("/api/match/ingest", {
        method: "POST", signal: AbortSignal.timeout(60000),
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${adminToken}`},
        body: JSON.stringify({...updatedMatch, match_id: updatedMatch.id,
          playing_xi_home: homeXI, playing_xi_away: awayXI})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Fixture validation failed.");
      if (data.match?.id !== updatedMatch.id || data.players?.length !== 22) throw new Error("Server did not confirm this fixture and both playing XIs.");
      onApplyMatch(data.match, data.players);
      setAdminToken("");
      onClose();
    } catch (error) {
      setFeedError(error instanceof Error ? error.message : "Fixture could not be saved.");
    } finally { setIsSaving(false); }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fade-in">
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-label="Match setup" tabIndex={-1} className="bg-[#0b0f19] border border-white/10 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between bg-[#070a11]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Radio size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-wide">
                  MATCH INGESTION & LIVE SYNC STUDIO
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                  LIVE ADAPTER
                </span>
              </div>
              <p className="text-xs text-slate-400 font-sans">
                Browse live references or original archives, then submit real XIs and credits
              </p>
            </div>
          </div>

          <button
            aria-label="Close match setup" onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <X size={20} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-white/10 bg-[#070a11] px-5 pt-2 overflow-x-auto gap-2">
          <button
            onClick={() => setActiveTab("live_sync")}
            className={`pb-2.5 px-3 text-xs font-sans font-bold flex items-center gap-2 transition-all border-b-2 whitespace-nowrap ${
              activeTab === "live_sync"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <Globe size={14} /> AVAILABLE FEED MATCHES [{liveMatches.length}]
          </button>

          <button
            onClick={() => setActiveTab("series_fixtures")}
            className={`pb-2.5 px-3 text-xs font-sans font-bold flex items-center gap-2 transition-all border-b-2 whitespace-nowrap ${
              activeTab === "series_fixtures"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers size={14} /> VERIFIED & ARCHIVED FIXTURES
          </button>

          <button
            onClick={() => setActiveTab("custom_setup")}
            className={`pb-2.5 px-3 text-xs font-sans font-bold flex items-center gap-2 transition-all border-b-2 whitespace-nowrap ${
              activeTab === "custom_setup"
                ? "border-amber-400 text-amber-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sliders size={14} /> CUSTOM MATCH, TOSS & PITCH REPORT
          </button>
        </div>

        <p className="px-5 py-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border-b border-emerald-500/20">
          {activeTab === "live_sync"
            ? "Provider fixtures require a connected playing XI before analysis. No default team will be substituted."
            : "Bundled fixtures are unverified scenarios, not a current schedule. Review both playing XIs before saving a custom fixture."}
        </p>

        {feedError && <p role="alert" className="p-4 text-xs text-rose-400 bg-rose-500/10 border-b border-rose-500/20">{feedError}</p>}
        {isLoadingLive && <p role="status" className="p-4 text-xs text-slate-400 animate-pulse">Loading fixtures...</p>}

        {/* Tab 0: Series Fixtures (Matches 1-5) */}
        {activeTab === "series_fixtures" && (
          <div className="p-5 overflow-y-auto space-y-4 flex-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-sans text-slate-300 uppercase tracking-wider flex items-center gap-1.5 font-bold">
                <Layers size={13} className="text-emerald-400" /> Bundled fixtures [VERIFY REQUIRED]
              </span>
              <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                1-CLICK LOAD & OPTIMIZE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {seriesFixtures.map((f) => (
                <div
                  key={f.id}
                  className={`p-4 rounded-lg bg-slate-900/80 border transition-all flex flex-col justify-between space-y-3 group ${
                    currentMatch.id === f.id
                      ? "border-emerald-500 ring-2 ring-emerald-500/20 shadow-lg bg-emerald-950/20"
                      : "border-white/10 hover:border-emerald-500/50"
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                        f.status.includes("UPCOMING")
                          ? "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                          : f.status.includes("DELAYED")
                          ? "bg-sky-500/15 text-sky-300 border border-sky-500/30"
                          : "bg-slate-800 text-slate-300 border border-white/10"
                      }`}>
                        {f.status}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">{f.venue.city}</span>
                    </div>

                    <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                      {f.name}
                    </h3>

                    <div className="text-xs font-sans text-slate-300">
                      <span className="font-semibold text-slate-200">Venue:</span> {f.venue.name}
                    </div>

                    <div className="p-2.5 rounded bg-slate-950/70 border border-white/5 text-xs font-sans text-slate-300 space-y-1">
                      <div><span className="font-semibold text-emerald-400">Pitch:</span> {f.venue.pitch_nature}</div>
                      <div className="flex gap-4 text-[10px] font-mono text-slate-400">
                        <span>Avg 1st: {f.venue.avg_first_innings}</span>
                        <span>Chasing Win: {f.venue.chasing_win_pct}%</span>
                        <span>Pace: {f.venue.pace_wicket_pct}%</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleLoadSeriesFixture(f)}
                    className={`w-full py-2 rounded text-xs font-sans font-bold flex items-center justify-center gap-2 transition-all ${
                      currentMatch.id === f.id
                        ? "bg-emerald-600 text-white shadow"
                        : "bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-white border border-white/10"
                    }`}
                  >
                    <Zap size={14} /> {currentMatch.id === f.id ? "ACTIVE MATCH" : "LOAD THIS FIXTURE & OPTIMIZE"}
                  </button>
                </div>
              ))}
            </div>
            {cricsheetMatches.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-sans text-cyan-300 uppercase tracking-wider flex items-center gap-1.5 font-bold">
                    <Database size={13} className="text-cyan-400" /> Cricsheet Verified Historical Matches ({cricsheetMatches.length})
                  </span>
                  <span className="text-[10px] font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                    REAL DELIVERIES & SCORECARDS
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {cricsheetMatches.map((m) => (
                    <div
                      key={m.match_id}
                      className="p-4 rounded-lg bg-slate-900/80 border border-white/10 hover:border-cyan-500/50 transition-all flex flex-col justify-between space-y-3 group"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                            {m.match_type || "T20"} · {m.date}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">{m.city || m.venue}</span>
                        </div>
                        <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                          {m.teams ? m.teams.join(" vs ") : `Match ${m.match_id}`}
                        </h3>
                        <div className="text-xs font-sans text-slate-300">
                          <span className="font-semibold text-slate-200">Venue:</span> {m.venue}
                        </div>
                        <div className="text-xs font-sans text-slate-400">
                          <span className="font-semibold text-slate-300">Winner:</span> {m.winner}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => void handleLoadCricsheetMatch(m.match_id)}
                        disabled={isSaving}
                        className="w-full py-2 rounded text-xs font-sans font-bold flex items-center justify-center gap-2 transition-all bg-slate-800 hover:bg-cyan-600 text-slate-200 hover:text-white border border-white/10 disabled:opacity-50"
                      >
                        <Zap size={14} /> "VIEW ORIGINAL CRICSHEET SCORECARD"
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 1: Live Feed Matches */}
        {activeTab === "live_sync" && (
          <div className="p-5 overflow-y-auto space-y-4 flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <span className="text-xs font-sans text-slate-300 uppercase tracking-wider flex items-center gap-1.5 font-bold">
                  <Database size={13} className="text-emerald-400" /> Live match references ({liveMatches.length} Total)
                </span>
                <span className="text-[11px] text-slate-400">
                  Live references are unverified; configure real XIs and fantasy credits before optimization
                </span>
              </div>

              <button
                onClick={fetchLiveMatches}
                className="text-xs font-sans text-slate-300 hover:text-emerald-400 flex items-center gap-1.5 transition-all self-start sm:self-auto px-3 py-1.5 rounded bg-slate-900 border border-white/10"
              >
                <RefreshCw size={12} className={isLoadingLive ? "animate-spin" : ""} /> Refresh Live Feed
              </button>
            </div>

            {/* Filter and Search Controls */}
            <div className="flex flex-col md:flex-row gap-2.5 items-stretch md:items-center justify-between bg-slate-950/80 p-3 rounded-lg border border-white/10">
              <div className="flex flex-wrap gap-1.5">
                {[
                  { key: "ALL", label: `All Matches (${liveMatches.length})` },
                  { key: "INTERNATIONAL", label: `International (${liveMatches.filter(m => m.category === "INTERNATIONAL").length})` },
                  { key: "RANJI_TROPHY", label: `Ranji Trophy (${liveMatches.filter(m => m.category === "RANJI_TROPHY").length})` },
                  { key: "WOMEN_CRICKET", label: `Women's T20 (${liveMatches.filter(m => m.category === "WOMEN_CRICKET").length})` },
                  { key: "DOMESTIC_LEAGUES", label: `Domestic Leagues (${liveMatches.filter(m => m.category === "DOMESTIC_LEAGUES").length})` }
                ].map(cat => (
                  <button
                    key={cat.key}
                    type="button"
                    onClick={() => setCategoryFilter(cat.key)}
                    className={`px-2.5 py-1 rounded text-[11px] font-sans font-bold transition-all ${
                      categoryFilter === cat.key
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                        : "bg-slate-900/60 text-slate-400 hover:text-white border border-white/5"
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search teams, venues, or players..."
                className="px-3 py-1.5 rounded bg-slate-900 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-full md:w-64"
              />
            </div>

            {/* Live Matches Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {liveMatches
                .filter((m) => {
                  const matchCat = categoryFilter === "ALL" || m.category === categoryFilter;
                  const query = searchQuery.trim().toLowerCase();
                  const matchSearch = !query ||
                    m.title.toLowerCase().includes(query) ||
                    m.team_home.toLowerCase().includes(query) ||
                    m.team_away.toLowerCase().includes(query) ||
                    m.details.toLowerCase().includes(query) ||
                    (m.venue && m.venue.toLowerCase().includes(query));
                  return matchCat && matchSearch;
                })
                .map((m) => (
                <div
                  key={m.id}
                  className={`p-4 rounded-lg bg-slate-900/80 border transition-all flex flex-col justify-between space-y-3 group ${
                    currentMatch.id === m.id
                      ? "border-emerald-500 ring-2 ring-emerald-500/20 shadow-lg bg-emerald-950/20"
                      : "border-white/10 hover:border-emerald-500/50"
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                          m.state === "VERIFIED_LIVE" || m.status === "LIVE NOW"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            : m.state === "COMPLETED_RESULT" || m.status === "RESULT"
                            ? "bg-slate-800 text-slate-300 border border-white/10"
                            : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                        }`}>
                          {m.status}
                        </span>

                        {m.format && (
                          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
                            {m.format}
                          </span>
                        )}

                        {m.data_provenance === "CRICBUZZ_LIVE_FEED" ? (
                          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                            CRICBUZZ LIVE (tarun7r)
                          </span>
                        ) : m.data_provenance === "LIVE_CRICDATA_SDK" ? (
                          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                            Provider-supplied · verification pending
                          </span>
                        ) : m.data_provenance === "VERIFIED_LIVE_RSS" ? (
                          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30">
                            RSS LIVE
                          </span>
                        ) : (
                          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
                            HISTORICAL / SIMULATED
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 truncate max-w-[110px]">{m.category_label || m.provider}</span>
                    </div>

                    <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                      {m.title}
                    </h3>

                    {m.score_home && (
                      <div className="text-xs font-sans text-emerald-400 font-bold">
                        {m.team_home}: {m.score_home} {m.score_away && `• ${m.team_away}: ${m.score_away}`}
                      </div>
                    )}

                    <p className="text-xs font-sans text-slate-300 line-clamp-2">
                      {m.details}
                    </p>

                    {m.toss && (
                      <div className="text-[11px] font-mono text-amber-300 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">
                        {m.toss}
                      </div>
                    )}

                    {m.pitch_report && (
                      <div className="p-2.5 rounded bg-slate-950/70 border border-white/5 text-xs font-sans text-slate-300">
                        <span className="text-emerald-400 font-bold">VENUE / PITCH: </span>
                        {m.pitch_report}
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => handleLoadLiveMatch(m)}
                    className={`w-full py-2 rounded text-xs font-sans font-bold flex items-center justify-center gap-2 transition-all shadow-sm ${
                      currentMatch.id === m.id
                        ? "bg-emerald-600 text-white shadow"
                        : "bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-white border border-white/10"
                    }`}
                  >
                    <Zap size={14} /> "CONFIGURE VERIFIED XI"
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}


        {/* Tab 2: Custom Match Configurator */}
        {activeTab === "custom_setup" && (
          <form onSubmit={handleSaveCustomMatch} className="p-5 overflow-y-auto space-y-4 flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Match Name */}
              <div className="md:col-span-2 space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Match Name / Title</label>
                <input aria-label="Match name"
                  type="text"
                  value={matchName}
                  onChange={(e) => setMatchName(e.target.value)}
                  placeholder="e.g. India vs Australia, 1st T20I"
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              {/* Team 1 Home */}
              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Team 1 (Home) Name & Code</label>
                <div className="flex gap-2">
                  <input aria-label="Team home name"
                    type="text"
                    value={teamHomeName}
                    onChange={(e) => setTeamHomeName(e.target.value)}
                    placeholder="e.g. India"
                    className="flex-1 p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                  <input aria-label="Team home code"
                    type="text"
                    value={teamHomeCode}
                    onChange={(e) => setTeamHomeCode(e.target.value)}
                    placeholder="IND"
                    maxLength={4}
                    className="w-20 p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white text-center uppercase placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
              </div>

              {/* Team 2 Away */}
              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Team 2 (Away) Name & Code</label>
                <div className="flex gap-2">
                  <input aria-label="Team away name"
                    type="text"
                    value={teamAwayName}
                    onChange={(e) => setTeamAwayName(e.target.value)}
                    placeholder="e.g. Australia"
                    className="flex-1 p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                  <input aria-label="Team away code"
                    type="text"
                    value={teamAwayCode}
                    onChange={(e) => setTeamAwayCode(e.target.value)}
                    placeholder="AUS"
                    maxLength={4}
                    className="w-20 p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white text-center uppercase placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
              </div>

              {/* Toss Winner & Choice */}
              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Toss Winner</label>
                <select aria-label="Toss winner"
                  value={tossWinner}
                  onChange={(e) => setTossWinner(e.target.value)}
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value={teamHomeName}>{teamHomeName}</option>
                  <option value={teamAwayName}>{teamAwayName}</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Toss Decision</label>
                <select aria-label="Toss choice"
                  value={tossChoice}
                  onChange={(e) => setTossChoice(e.target.value as "bat" | "bowl")}
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="bat">Elected to Bat First</option>
                  <option value="bowl">Elected to Bowl First (Chasing)</option>
                </select>
              </div>

              {/* Pitch Report Details */}
              <div className="md:col-span-2 space-y-1">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-sans text-slate-300 uppercase">Pitch & Venue Report</label>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setPitchReport("Hard red soil surface with true bounce, high pace carry and significant evening dew.")}
                      className="text-xs font-sans text-emerald-400 hover:underline"
                    >
                      + Red Soil Pace
                    </button>
                    <button
                      type="button"
                      onClick={() => setPitchReport("Dry black soil surface offering significant spin from over 6 onwards. Par score 170.")}
                      className="text-xs font-sans text-emerald-400 hover:underline"
                    >
                      + Black Soil Spin
                    </button>
                  </div>
                </div>
                <textarea aria-label="Pitch report"
                  rows={3}
                  value={pitchReport}
                  onChange={(e) => setPitchReport(e.target.value)}
                  placeholder="Enter pitch conditions, soil type, bounce, dew factor..."
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              {/* Avg Score & Dew factor */}
              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Avg 1st Innings Par Score</label>
                <input aria-label="Avg first innings"
                  type="number"
                  value={avgFirstInnings}
                  onChange={(e) => setAvgFirstInnings(Number(e.target.value))}
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-sans text-slate-300 uppercase">Dew Factor Impact (0.0 to 1.0)</label>
                <input aria-label="Dew factor"
                  type="number"
                  step="0.05"
                  min="0.0"
                  max="1.0"
                  value={dewFactor}
                  onChange={(e) => setDewFactor(Number(e.target.value))}
                  className="w-full p-2.5 rounded bg-slate-950 border border-white/15 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

            </div>

            <div className="space-y-4">
              <p className="text-sm">Confirm all 22 players. Roles, credits and playing conditions are user supplied and require verification.</p>
              {[{label: teamHomeName, xi: homeXI, setXI: setHomeXI}, {label: teamAwayName, xi: awayXI, setXI: setAwayXI}].map(({label, xi, setXI}, side) => (
                <fieldset key={side} className="space-y-2 min-w-0">
                  <legend className="font-bold">{label}: playing XI ({xi.length}/11)</legend>
                  {xi.map((p, index) => <div key={index} className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                    <input aria-label={`${label} player ${index + 1} name`} value={p.name} required onChange={e => setXI(xi.map((q, i) => i === index ? {...q, name:e.target.value} : q))} className="border p-2 min-w-0" />
                    <select aria-label={`${label} player ${index + 1} role`} value={p.role} onChange={e => setXI(xi.map((q, i) => i === index ? {...q, role:e.target.value as Player["role"]} : q))} className="border p-2">
                      {["WK", "BAT", "AR", "BOWL"].map(role => <option key={role}>{role}</option>)}
                    </select>
                    <input aria-label={`${label} player ${index + 1} credits`} type="number" step="0.5" min="0.5" max="20" value={p.credits} required onChange={e => setXI(xi.map((q, i) => i === index ? {...q, credits:Number(e.target.value)} : q))} className="border p-2 min-w-0" />
                    <select aria-label={`${label} player ${index + 1} batting hand`} value={p.bat_hand} onChange={e => setXI(xi.map((q, i) => i === index ? {...q, bat_hand:e.target.value as Player["batting_style"]} : q))} className="border p-2"><option>RHB</option><option>LHB</option></select>
                    <input aria-label={`${label} player ${index + 1} bowling style`} value={p.bowl_style} onChange={e => setXI(xi.map((q, i) => i === index ? {...q, bowl_style:e.target.value} : q))} className="border p-2 min-w-0" />
                  </div>)}
                </fieldset>
              ))}
              <label className="block text-sm">Administrator token
                <input aria-label="Administrator token" type="password" autoComplete="off" value={adminToken} required onChange={e => setAdminToken(e.target.value)} className="block border p-2 w-full" />
              </label>
              <p className="text-xs">Used for this save request only. The server administrator supplies this token.</p>
            </div>

            {/* Submit */}
            <div className="pt-4 border-t border-white/10 flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded bg-slate-800 text-slate-300 text-xs font-sans hover:bg-slate-700 transition-all"
              >
                Cancel
              </button>

              <button
                type="submit" disabled={isSaving || homeXI.length !== 11 || awayXI.length !== 11}
                className="px-6 py-2.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs font-sans flex items-center gap-2 transition-all shadow-md"
              >
                <CheckCircle2 size={16} /> {isSaving ? "SAVING FIXTURE?" : "SAVE & APPLY MATCH"}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
};

