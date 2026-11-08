import React, { useState, useEffect } from "react";
import { BarChart3, RefreshCw, Shield, MapPin, Clock, Flame } from "lucide-react";

interface PhaseData {
  phase: string;
  avg_runs: number;
  avg_wickets: number;
  run_rate: number;
  tactical_note: string;
}

interface VenueRecord {
  venue: string;
  avg_first_innings: number;
  chase_win_pct: string;
  pace_wkt_share: string;
}

interface DeepDiveData {
  team: string;
  overall_avg_score: number;
  death_overs_economy: number;
  powerplay_avg_runs: number;
  phases: PhaseData[];
  venue_records: VenueRecord[];
}

export const TeamDeepDiveOracle: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<string>("Chennai Super Kings");
  const [data, setData] = useState<DeepDiveData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [teams, setTeams] = useState<string[]>([
    "Chennai Super Kings",
    "Mumbai Indians",
    "Royal Challengers Bengaluru",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Punjab Kings",
    "Rajasthan Royals",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
    "Lucknow Super Giants"
  ]);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await fetch("/api/oracle/teams");
        if (res.ok) {
          const json = await res.json();
          if (json.teams && Array.isArray(json.teams)) {
            setTeams(json.teams);
          }
        }
      } catch {
        // Fallback already populated
      }
    };
    void fetchTeams();
  }, []);

  const fetchDeepDive = async (team: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/oracle/team-phase/${encodeURIComponent(team)}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      setData(json.deep_dive);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load team analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchDeepDive(selectedTeam);
  }, [selectedTeam]);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <section className="rounded-2xl border border-white/10 bg-slate-900/90 p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
          <BarChart3 size={160} className="text-purple-400" />
        </div>
        <div className="space-y-3 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-purple-500/20 px-2.5 py-1 text-xs font-mono font-bold tracking-wider text-purple-300 border border-purple-500/30">
              THENITISHKR-SPORTS // TEAM DEEP DIVE
            </span>
            <span className="rounded bg-emerald-500/10 px-2.5 py-1 text-xs font-mono text-emerald-400 border border-emerald-500/20">
              PHASE-BY-PHASE PROFILES
            </span>
            <span className="rounded bg-amber-500/10 px-2.5 py-1 text-xs font-mono text-amber-300 border border-amber-500/20">
              DEATH OVERS ECONOMY
            </span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                <span>📊</span> Team Phase & Death Overs Intelligence
              </h1>
              <p className="text-sm text-slate-300 mt-1 max-w-2xl">
                Phase-by-phase run scoring, wicket attrition rates, and death overs bowling economy benchmarks across domestic and international venues.
              </p>
            </div>

            {/* Team Dropdown Selector */}
            <div className="flex items-center gap-2">
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="bg-slate-950 border border-white/20 rounded-xl px-4 py-2.5 text-white font-mono text-xs focus:outline-none focus:border-purple-500"
              >
                {teams.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Highlights */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-xl border border-purple-500/30 bg-purple-500/5 p-4 space-y-1">
            <div className="flex items-center justify-between text-purple-400">
              <span className="text-xs font-mono uppercase font-bold">Avg 1st Innings</span>
              <Shield size={18} />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {data.overall_avg_score} runs
            </div>
            <div className="text-[11px] text-purple-300/70 font-mono">Full 20-over projection</div>
          </div>

          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 space-y-1">
            <div className="flex items-center justify-between text-emerald-400">
              <span className="text-xs font-mono uppercase font-bold">Powerplay (1-6)</span>
              <Flame size={18} />
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {data.powerplay_avg_runs} runs
            </div>
            <div className="text-[11px] text-emerald-300/70 font-mono">
              RR: {(data.powerplay_avg_runs / 6).toFixed(2)} rpo
            </div>
          </div>

          <div className="rounded-xl border border-rose-500/30 bg-rose-500/5 p-4 space-y-1">
            <div className="flex items-center justify-between text-rose-400">
              <span className="text-xs font-mono uppercase font-bold">Death Econ (16-20)</span>
              <Clock size={18} />
            </div>
            <div className="text-2xl font-bold font-mono text-rose-300">
              {data.death_overs_economy} rpo
            </div>
            <div className="text-[11px] text-rose-300/70 font-mono">Bowling pressure index</div>
          </div>

          <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-4 space-y-1">
            <div className="flex items-center justify-between text-blue-400">
              <span className="text-xs font-mono uppercase font-bold">Middle Phase (7-15)</span>
              <BarChart3 size={18} />
            </div>
            <div className="text-2xl font-bold font-mono text-blue-300">
              {data.phases[1]?.avg_runs || 80} runs
            </div>
            <div className="text-[11px] text-blue-300/70 font-mono">Spin rotation control</div>
          </div>
        </div>
      )}

      {/* Phase Breakdown Cards */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 font-mono text-sm space-y-3">
          <RefreshCw size={24} className="animate-spin mx-auto text-purple-400" />
          <p>Extracting phase ball-by-ball benchmarks for {selectedTeam}...</p>
        </div>
      ) : error ? (
        <div className="p-8 text-center text-amber-400 font-mono text-sm space-y-2">
          <p>⚠️ {error}</p>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {data.phases.map((ph, idx) => {
            const isPowerplay = idx === 0;
            const isDeath = idx === 2;
            const accentColor = isPowerplay
              ? "emerald"
              : isDeath
              ? "rose"
              : "blue";

            return (
              <div
                key={idx}
                className="rounded-2xl border border-white/10 bg-slate-900/90 p-5 space-y-4 shadow-xl hover:border-white/20 transition"
              >
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <h3 className="font-bold text-base text-white tracking-tight">{ph.phase}</h3>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                      isPowerplay
                        ? "bg-emerald-500/20 text-emerald-300"
                        : isDeath
                        ? "bg-rose-500/20 text-rose-300"
                        : "bg-blue-500/20 text-blue-300"
                    }`}
                  >
                    Overs {isPowerplay ? "1-6" : isDeath ? "16-20" : "7-15"}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center font-mono">
                  <div className="rounded-lg bg-slate-950/70 p-2.5 border border-white/5">
                    <span className="text-[10px] text-slate-500 uppercase block">Avg Runs</span>
                    <span className="text-base font-bold text-white">{ph.avg_runs}</span>
                  </div>
                  <div className="rounded-lg bg-slate-950/70 p-2.5 border border-white/5">
                    <span className="text-[10px] text-slate-500 uppercase block">Run Rate</span>
                    <span className={`text-base font-bold text-${accentColor}-400`}>
                      {ph.run_rate}
                    </span>
                  </div>
                  <div className="rounded-lg bg-slate-950/70 p-2.5 border border-white/5">
                    <span className="text-[10px] text-slate-500 uppercase block">Wickets Lost</span>
                    <span className="text-base font-bold text-slate-300">{ph.avg_wickets}</span>
                  </div>
                </div>

                {/* Visual Run Rate Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] font-mono text-slate-400">
                    <span>Scoring Intensity</span>
                    <span>{ph.run_rate} rpo</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-950 overflow-hidden border border-white/5">
                    <div
                      className={`h-full rounded-full ${
                        isPowerplay
                          ? "bg-emerald-500"
                          : isDeath
                          ? "bg-rose-500"
                          : "bg-blue-500"
                      }`}
                      style={{ width: `${Math.min(100, ph.run_rate * 7.5)}%` }}
                    />
                  </div>
                </div>

                <p className="text-xs text-slate-400 bg-slate-950/40 p-3 rounded-lg border border-white/5 font-sans leading-relaxed">
                  💡 {ph.tactical_note}
                </p>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* Venue Performance Table */}
      {data && (
        <section className="rounded-2xl border border-white/10 bg-slate-900/90 overflow-hidden shadow-xl">
          <div className="p-4 border-b border-white/10 flex items-center justify-between bg-slate-950/40">
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <MapPin size={16} className="text-purple-400" />
              <span>Historical Ground Records & Pitch Bias</span>
            </h2>
            <span className="text-xs font-mono text-slate-400">
              Source: Cricsheet / THENITISHKR-SPORTS Archive
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-white/10 bg-slate-950/70 text-slate-400 uppercase text-[11px]">
                  <th className="py-3 px-4">Venue</th>
                  <th className="py-3 px-4 text-center">Avg 1st Innings</th>
                  <th className="py-3 px-4 text-center">Chasing Win Rate</th>
                  <th className="py-3 px-4 text-center">Pace Wicket Share</th>
                  <th className="py-3 px-4 text-right">Conditions Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                {data.venue_records.map((vr, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-bold text-white text-sm">
                      {vr.venue}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-purple-300">
                      {vr.avg_first_innings}
                    </td>
                    <td className="py-3.5 px-4 text-center font-semibold text-emerald-400">
                      {vr.chase_win_pct}
                    </td>
                    <td className="py-3.5 px-4 text-center text-slate-300">
                      {vr.pace_wkt_share}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold border border-white/10">
                        {parseInt(vr.pace_wkt_share) > 60 ? "Pace & Bounce" : "Balanced / Spin Turn"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
};
