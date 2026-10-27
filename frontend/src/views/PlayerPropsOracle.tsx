import React, { useState, useEffect } from "react";
import { Target, RefreshCw, Filter, ArrowUp, ArrowDown, User, ShieldAlert, CheckCircle2 } from "lucide-react";

interface PlayerProp {
  player: string;
  team: string;
  role: string;
  market: string;
  projection: number;
  dk_line: number;
  edge: number;
  confidence: "High" | "Medium" | "Low";
  recommendation: "OVER" | "UNDER";
  rivalry_note: string;
}

interface OraclePropsResponse {
  status: string;
  platform: string;
  count: number;
  props: PlayerProp[];
}

export const PlayerPropsOracle: React.FC = () => {
  const [data, setData] = useState<OraclePropsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>("All");
  const [confFilter, setConfFilter] = useState<string>("All");
  const [recFilter, setRecFilter] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const fetchProps = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/oracle/player-props");
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json: OraclePropsResponse = await res.json();
      setData(json);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load player props");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchProps();
  }, []);

  const props = data?.props || [];
  const filtered = props.filter((p) => {
    if (roleFilter !== "All" && p.role !== roleFilter) return false;
    if (confFilter !== "All" && p.confidence !== confFilter) return false;
    if (recFilter !== "All" && p.recommendation !== recFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      if (!p.player.toLowerCase().includes(q) && !p.team.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const highConfCount = props.filter((p) => p.confidence === "High").length;
  const overCount = props.filter((p) => p.recommendation === "OVER").length;
  const underCount = props.filter((p) => p.recommendation === "UNDER").length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <section className="rounded-2xl border border-white/10 bg-slate-900/90 p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
          <Target size={160} className="text-cyan-400" />
        </div>
        <div className="space-y-3 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-cyan-500/20 px-2.5 py-1 text-xs font-mono font-bold tracking-wider text-cyan-400 border border-cyan-500/30">
              THENITISHKR-SPORTS // PROPS ENGINE
            </span>
            <span className="rounded bg-emerald-500/10 px-2.5 py-1 text-xs font-mono text-emerald-400 border border-emerald-500/20">
              BATTER RUNS & BOWLER WICKETS
            </span>
            <span className="rounded bg-purple-500/10 px-2.5 py-1 text-xs font-mono text-purple-300 border border-purple-500/20">
              CALIBRATED EDGES
            </span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                <span>🎯</span> Player Props vs Market Lines
              </h1>
              <p className="text-sm text-slate-300 mt-1 max-w-2xl">
                Algorithmic projection comparison against standard DraftKings lines for batters and bowlers. Pinpoints exploitable edges with statistical confidence tiers and micro head-to-head tactical notes.
              </p>
            </div>
            <button
              onClick={() => void fetchProps()}
              disabled={loading}
              className="self-start md:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-white/10 transition active:scale-95 disabled:opacity-50"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              <span>Refresh Props</span>
            </button>
          </div>
        </div>
      </section>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-cyan-400">
            <span className="text-xs font-mono uppercase font-bold">Total Props</span>
            <User size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {props.length}
          </div>
          <div className="text-[11px] text-cyan-300/70 font-mono">Active match roster</div>
        </div>

        <div className="rounded-xl border border-rose-500/30 bg-rose-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-rose-400">
            <span className="text-xs font-mono uppercase font-bold">High Confidence</span>
            <ShieldAlert size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400">
            {highConfCount}
          </div>
          <div className="text-[11px] text-rose-300/70 font-mono">Edge &gt;= 6.0 runs / 0.6 wkts</div>
        </div>

        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-xs font-mono uppercase font-bold">Over Targets</span>
            <ArrowUp size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {overCount}
          </div>
          <div className="text-[11px] text-emerald-300/70 font-mono">Model exceeds book line</div>
        </div>

        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-xs font-mono uppercase font-bold">Under Targets</span>
            <ArrowDown size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300">
            {underCount}
          </div>
          <div className="text-[11px] text-amber-300/70 font-mono">Book line is inflated</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="rounded-xl border border-white/10 bg-slate-900/60 p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <Filter size={14} />
            <span>Filters:</span>
          </div>

          {/* Role Filter */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10">
            {["All", "Batter", "Bowler", "All-Rounder"].map((r) => (
              <button
                key={r}
                onClick={() => setRoleFilter(r)}
                className={`px-3 py-1 rounded text-xs font-mono transition ${
                  roleFilter === r
                    ? "bg-cyan-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          {/* Recommendation Filter */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10">
            {["All", "OVER", "UNDER"].map((rec) => (
              <button
                key={rec}
                onClick={() => setRecFilter(rec)}
                className={`px-3 py-1 rounded text-xs font-mono transition ${
                  recFilter === rec
                    ? rec === "OVER"
                      ? "bg-emerald-500 text-slate-950 font-bold"
                      : rec === "UNDER"
                      ? "bg-amber-500 text-slate-950 font-bold"
                      : "bg-purple-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {rec}
              </button>
            ))}
          </div>

          {/* Confidence Filter */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10">
            {["All", "High", "Medium", "Low"].map((c) => (
              <button
                key={c}
                onClick={() => setConfFilter(c)}
                className={`px-3 py-1 rounded text-xs font-mono transition ${
                  confFilter === c
                    ? "bg-slate-700 text-white font-bold"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input */}
        <div>
          <input
            type="text"
            placeholder="Search player or team..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500 w-52"
          />
        </div>
      </div>

      {/* Props Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 font-mono text-sm space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p>Calculating projections and DraftKings line deltas...</p>
        </div>
      ) : error ? (
        <div className="p-8 text-center text-amber-400 font-mono text-sm space-y-2">
          <p>⚠️ {error}</p>
          <button
            onClick={() => void fetchProps()}
            className="px-3 py-1.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs"
          >
            Retry
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center text-slate-400 font-mono text-sm space-y-2 bg-slate-900/50 rounded-xl border border-white/10">
          <p className="text-base font-semibold text-slate-300">No props match the active filters.</p>
          <p className="text-xs text-slate-500">Try loosening your search query or selecting &quot;All&quot;.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p, idx) => {
            const isOver = p.recommendation === "OVER";
            const isHighConf = p.confidence === "High";
            return (
              <div
                key={idx}
                className="rounded-xl border border-white/10 bg-slate-900/90 p-5 space-y-3 hover:border-white/20 transition shadow-lg relative overflow-hidden"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">{p.player}</h3>
                    <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 mt-0.5">
                      <span>{p.team}</span>
                      <span>•</span>
                      <span className="text-cyan-400">{p.role}</span>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono font-bold uppercase tracking-wider ${
                      isOver
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                    }`}
                  >
                    {isOver ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                    {p.recommendation}
                  </span>
                </div>

                <div className="rounded-lg bg-slate-950/70 border border-white/5 p-3 grid grid-cols-3 gap-2 text-center font-mono">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Model Proj</span>
                    <span className="text-sm font-bold text-slate-200">
                      {p.projection} {p.market === "Runs Scored" ? "r" : "w"}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">DK Line</span>
                    <span className="text-sm font-bold text-slate-400">{p.dk_line}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Edge Delta</span>
                    <span className={`text-sm font-bold ${isOver ? "text-emerald-400" : "text-amber-400"}`}>
                      {p.edge > 0 ? `+${p.edge}` : p.edge}
                    </span>
                  </div>
                </div>

                <div className="space-y-1.5 pt-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">{p.market}</span>
                    <span
                      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        isHighConf
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : p.confidence === "Medium"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          : "bg-slate-800 text-slate-400 border border-white/5"
                      }`}
                    >
                      <CheckCircle2 size={10} />
                      {p.confidence} Confidence
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 bg-slate-950/40 p-2 rounded border border-white/5 font-sans leading-relaxed">
                    💡 {p.rivalry_note}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
