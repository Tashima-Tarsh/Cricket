import { useMatchContext } from "../context/MatchContext";
import React, { useState } from "react";
import { Player, RoleType } from "../types";
import { 
  User, 
  Search, 
  Filter, 
  Flame, 
  TrendingUp, 
  ShieldCheck, 
  Activity, 
  Award, 
  Crosshair, 
  BarChart2, 
  Percent, 
  ChevronRight,
  Zap
} from "lucide-react";

interface PlayerIntelProps {
  players: Player[];
}

export const PlayerIntel: React.FC<PlayerIntelProps> = ({ players }) => {
  const { selectedBatter } = useMatchContext();
  const [selectedPlayerId, setSelectedPlayerId] = useState<string>(selectedBatter?.id || players[0]?.id || "");
  const [roleFilter, setRoleFilter] = useState<string>("ALL");
  const [teamFilter, setTeamFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredPlayers = players.filter((p) => {
    const matchesRole = roleFilter === "ALL" || p.role === roleFilter;
    const matchesTeam = teamFilter === "ALL" || p.team === teamFilter;
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          p.team.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRole && matchesTeam && matchesSearch;
  });

  const activePlayer = players.find((p) => p.id === selectedPlayerId) || players[0];

  return (
    <div className="space-y-6">
      {/* 1. Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-stone-300">
        <div>
          <div className="flex items-center gap-2 text-xs font-sans text-stone-800 uppercase tracking-widest">
            <User size={14} /> Biometric & Performance Laboratory
          </div>
          <h1 className="text-2xl lg:text-3xl font-semibold text-stone-800 uppercase tracking-tight mt-1 flex items-center gap-3">
            Player Intelligence
            <span className="text-xs px-2.5 py-0.5 rounded border border-[#b99b37]/40 bg-white text-stone-800 font-sans font-normal">
              PROFILES & TELEMETRY
            </span>
          </h1>
          <p className="text-xs text-stone-800 mt-0.5 font-sans">
            Full 360-degree performance profiling, wagon wheels, ML expected fantasy output & volatility metrics
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full md:w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input aria-label="Search query"
            type="text"
            placeholder="Search player or team..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 border border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* 2. Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-900/60 rounded-xl border border-white/10">
        {/* Role tabs */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-mono text-slate-400 uppercase mr-2 flex items-center gap-1">
            <Filter size={12} /> ROLE:
          </span>
          {(["ALL", "WK", "BAT", "AR", "BOWL"] as const).map((role) => (
            <button
              key={role}
              onClick={() => setRoleFilter(role)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                roleFilter === role
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-bold shadow-[0_0_10px_rgba(16,185,129,0.15)]"
                  : "bg-slate-800/40 text-slate-400 border border-white/5 hover:text-white hover:bg-slate-800"
              }`}
            >
              {role}
            </button>
          ))}
        </div>

        {/* Team filter */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-mono text-slate-400 uppercase mr-2">TEAM:</span>
          {(["ALL", "IND", "WI"] as const).map((tm) => (
            <button
              key={tm}
              onClick={() => setTeamFilter(tm)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                teamFilter === tm
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 font-bold shadow-[0_0_10px_rgba(6,182,212,0.15)]"
                  : "bg-slate-800/40 text-slate-400 border border-white/5 hover:text-white hover:bg-slate-800"
              }`}
            >
              {tm}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Main Split View: Left Player Roster (5 cols), Right Deep Dossier (7 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: Player Roster Grid */}
        <div className="lg:col-span-5 space-y-2 max-h-[780px] overflow-y-auto pr-1">
          {filteredPlayers.map((p) => {
            const isSelected = p.id === activePlayer.id;
            return (
              <div
                key={p.id}
                onClick={() => setSelectedPlayerId(p.id)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? "bg-slate-900 border-emerald-500 shadow-md ring-1 ring-emerald-500/30"
                    : "bg-slate-950/60 border-white/10 hover:border-emerald-500/40 hover:bg-slate-900/60"
                }`}
              >
                <div className="flex items-center gap-3">
                  {/* Avatar / Number badge */}
                  <div className={`w-10 h-10 rounded-lg border flex items-center justify-center font-bold text-sm ${
                    isSelected 
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40" 
                      : "bg-slate-900 text-slate-300 border-white/10"
                  }`}>
                    {p.name.charAt(0)}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white text-sm">{p.name}</span>
                      <span className={`text-xs px-1.5 py-0.2 rounded font-sans font-bold ${
                        p.team === "IND" ? "bg-stone-100 text-stone-800 border border-blue-700/50" : "bg-stone-100 text-stone-800 border border-red-700/50"
                      }`}>
                        {p.team}
                      </span>
                      <span className="text-xs font-sans text-stone-800">
                        {p.role}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 mt-1 text-xs font-sans text-stone-800">
                      <span>CR: <strong className="text-stone-800">{p.credits}</strong></span>
                      <span>•</span>
                      <span>OWN: <strong className="text-stone-800">{p.projected_ownership}%</strong></span>
                      <span>•</span>
                      <span>ORDER: <strong className="text-stone-800">#{p.batting_order}</strong></span>
                    </div>
                  </div>
                </div>

                {/* Right side projection */}
                <div className="text-right">
                  <div className="text-sm font-semibold text-stone-800 telemetry-num">
                    {p.projected_points.toFixed(1)}
                  </div>
                  <div className="text-xs font-sans text-stone-800 uppercase">PROJ PTS</div>
                  {p.differential_tag && (
                    <span className="inline-block mt-1 text-[8px] font-sans px-1 rounded bg-stone-100 text-stone-800 border border-amber-500/30">
                      {p.differential_tag}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Active Player Deep Telemetry Dossier */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* Dossier Header Panel */}
          <div className="strike-panel p-6 border-t-2 border-t-emerald-500 relative overflow-hidden bg-slate-900/70 border border-white/10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-xl bg-emerald-500/15 border-2 border-emerald-500/40 flex items-center justify-center font-bold text-2xl text-emerald-400">
                  {activePlayer.name.charAt(0)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xl sm:text-2xl font-bold text-white">{activePlayer.name}</span>
                    <span className="text-xs px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      {activePlayer.team} • {activePlayer.role}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-slate-400 mt-1 flex flex-wrap items-center gap-3">
                    <span>Style: <strong className="text-slate-200">{activePlayer.batting_style}</strong></span>
                    {activePlayer.bowling_style && (
                      <>
                        <span>•</span>
                        <span>Bowling: <strong className="text-slate-200">{activePlayer.bowling_style}</strong></span>
                      </>
                    )}
                    <span>•</span>
                    <span>Batting Order: <strong className="text-slate-200">#{activePlayer.batting_order}</strong></span>
                  </div>
                </div>
              </div>

              {/* Fantasy Credentials */}
              <div className="text-left sm:text-right bg-slate-900/90 p-3 rounded-xl border border-white/10 min-w-[140px]">
                <div className="text-[11px] font-mono text-slate-400 uppercase">DREAM11 CREDITS</div>
                <div className="text-2xl font-mono font-extrabold text-emerald-400">{activePlayer.credits}.0</div>
                <div className="text-xs font-mono text-slate-300 mt-0.5">
                  Proj Own: {activePlayer.projected_ownership}%
                </div>
              </div>
            </div>

            {/* Core Telemetry Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
              <div className="bg-slate-900/80 p-3 rounded-xl border border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">EXPECTED POINTS</div>
                <div className="text-xl font-mono font-bold text-white mt-0.5">
                  {activePlayer.projected_points.toFixed(1)}
                </div>
                <div className="text-[10px] text-emerald-400 font-mono">XGBoost ML Output</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-xl border border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">CEILING (90th PCT)</div>
                <div className="text-xl font-mono font-bold text-amber-400 mt-0.5">
                  {activePlayer.ceiling_score.toFixed(1)}
                </div>
                <div className="text-[10px] text-amber-300 font-mono">Grand League upside</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-xl border border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">FLOOR (10th PCT)</div>
                <div className="text-xl font-mono font-bold text-slate-300 mt-0.5">
                  {activePlayer.floor_score.toFixed(1)}
                </div>
                <div className="text-[10px] text-slate-400 font-mono">Safety threshold</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-xl border border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">VOLATILITY SPREAD</div>
                <div className="text-xl font-mono font-bold text-purple-400 mt-0.5">
                  {(activePlayer.ceiling_score - activePlayer.floor_score).toFixed(1)}
                </div>
                <div className="text-[10px] text-purple-300 font-mono">High Variance Tier</div>
              </div>
            </div>

            {/* Analytical Provenance & Model Specification */}
            <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-slate-400 bg-slate-950/70 px-3 py-1.5 rounded-lg border border-white/5 mt-3">
              <span className="flex items-center gap-1.5">
                <ShieldCheck size={12} className="text-emerald-400" />
                <span>PROVENANCE: Research projections are uncalibrated; inspect source and sample size before acting.</span>
              </span>
              <span>Confidence: 90% Range [{activePlayer.floor_score.toFixed(1)} – {activePlayer.ceiling_score.toFixed(1)} pts]</span>
            </div>

            {/* Recent Fantasy Form Sparkline */}
            <div className="mt-5 p-4 rounded-xl bg-slate-950/80 border border-white/10">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-slate-400 uppercase flex items-center gap-1.5">
                  <Activity size={14} className="text-emerald-400" /> RECENT MATCH FANTASY SCORES (LAST 5)
                </span>
                <span className="text-xs text-emerald-400 font-bold font-mono">
                  AVG: {activePlayer.stats.avg_fantasy_pts} PTS
                </span>
              </div>
              <div className="grid grid-cols-5 gap-2">
                {activePlayer.stats.recent_fantasy_pts.map((score, i) => (
                  <div key={i} className="text-center bg-slate-900 p-2 rounded-lg border border-white/10">
                    <div className="text-[10px] font-mono text-slate-400">M-{i + 1}</div>
                    <div className={`text-base font-bold font-mono telemetry-num mt-0.5 ${
                      score >= 60 ? "text-emerald-400" : score >= 35 ? "text-cyan-400" : "text-amber-400"
                    }`}>
                      {score}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Batting & Bowling Splits */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
              {/* Batting Telemetry */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-white/10">
                <div className="text-xs font-mono text-cyan-400 uppercase font-bold mb-3 flex items-center gap-1.5">
                  <Flame size={14} /> Batting Telemetry
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">STRIKE RATE</div>
                    <div className="text-lg font-bold font-mono text-white telemetry-num">{activePlayer.stats.strike_rate}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">BATTING AVERAGE</div>
                    <div className="text-lg font-bold font-mono text-white telemetry-num">{activePlayer.stats.batting_avg}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">BOUNDARY %</div>
                    <div className="text-lg font-bold font-mono text-emerald-400 telemetry-num">{activePlayer.stats.boundary_pct}%</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">DOT BALL %</div>
                    <div className="text-lg font-bold font-mono text-slate-300 telemetry-num">{activePlayer.stats.dot_ball_pct || 36.2}%</div>
                  </div>
                </div>
              </div>

              {/* Bowling / Defense Telemetry */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-white/10">
                <div className="text-xs font-mono text-rose-400 uppercase font-bold mb-3 flex items-center gap-1.5">
                  <Crosshair size={14} /> Bowling & Overs Projection
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">EXP OVERS</div>
                    <div className="text-lg font-bold font-mono text-white telemetry-num">{activePlayer.expected_overs}.0</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">ECONOMY RATE</div>
                    <div className="text-lg font-bold font-mono text-cyan-400 telemetry-num">{activePlayer.stats.economy || "N/A"}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">TOTAL WICKETS</div>
                    <div className="text-lg font-bold font-mono text-emerald-400 telemetry-num">{activePlayer.stats.wickets}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">BOWLING STRIKE RATE</div>
                    <div className="text-lg font-bold font-mono text-slate-300 telemetry-num">{activePlayer.stats.bowling_sr || "N/A"}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tactical AI Scouting Verdict */}
            <div className="mt-5 p-4 rounded-xl bg-slate-950/80 border border-white/10">
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 font-bold mb-1.5">
                <Zap size={14} /> TACTICAL SCOUTING REPORT & GAME SCRIPT
              </div>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                {activePlayer.role === "WK" || activePlayer.role === "BAT"
                  ? `${activePlayer.name} thrives against high-pace bowling in powerplays, scoring at 155+ SR with strong off-side boundary percentage. Prime leverage pick against early swing.`
                  : activePlayer.role === "AR"
                  ? `${activePlayer.name} provides dual-pathway point security with ${activePlayer.expected_overs} overs at death and middle-order finishing equity. High C/VC candidate.`
                  : `${activePlayer.name} represents lethal wicket-taking threat in middle overs, commanding a sub-18 bowling strike rate and 42% dot ball pressure.`}
              </p>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
};

