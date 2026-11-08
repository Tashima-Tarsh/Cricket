import React, { useState, useEffect } from "react";
import { TrendingUp, Award, DollarSign, Percent, RefreshCw, Filter, ShieldCheck, ArrowUpRight, BarChart2 } from "lucide-react";

interface ValueBet {
  match: string;
  bet: string;
  type: string;
  model_prob: number;
  implied_prob: number;
  edge: number;
  dk_odds: string;
  kelly_stake: string;
  tier: "Elite Pick" | "Strong";
}

interface OracleValueResponse {
  status: string;
  platform: string;
  count: number;
  elite_count: number;
  strong_count: number;
  avg_edge_pct: number;
  bets: ValueBet[];
}

export const ValueBetsOracle: React.FC = () => {
  const [data, setData] = useState<OracleValueResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("All");
  const [tierFilter, setTierFilter] = useState<string>("All");
  const [minEdge, setMinEdge] = useState<number>(0.04);

  const fetchBets = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/oracle/value-bets");
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json: OracleValueResponse = await res.json();
      setData(json);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load value bets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchBets();
  }, []);

  const bets = data?.bets || [];
  const filteredBets = bets.filter((b) => {
    if (typeFilter !== "All" && b.type !== typeFilter) return false;
    if (tierFilter !== "All" && b.tier !== tierFilter) return false;
    if (b.edge < minEdge) return false;
    return true;
  });

  const totalKellyStake = filteredBets
    .reduce((sum, b) => sum + parseFloat(b.kelly_stake.replace("%", "") || "0"), 0)
    .toFixed(1);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <section className="rounded-2xl border border-white/10 bg-slate-900/90 p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
          <TrendingUp size={160} className="text-emerald-400" />
        </div>
        <div className="space-y-3 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-emerald-500/20 px-2.5 py-1 text-xs font-mono font-bold tracking-wider text-emerald-400 border border-emerald-500/30">
              THENITISHKR-SPORTS // WICKET ORACLE
            </span>
            <span className="rounded bg-blue-500/10 px-2.5 py-1 text-xs font-mono text-blue-400 border border-blue-500/20">
              25% FRACTIONAL KELLY
            </span>
            <span className="rounded bg-amber-500/10 px-2.5 py-1 text-xs font-mono text-amber-300 border border-amber-500/20">
              DRAFTKINGS MARKET LINES
            </span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                <span>💰</span> Value Bets Engine
              </h1>
              <p className="text-sm text-slate-300 mt-1 max-w-2xl">
                DraftKings-backed moneyline and total match run edges calculated by comparing model win probabilities against market implied probabilities. Stake sizing is constrained by 25% Fractional Kelly.
              </p>
            </div>
            <button
              onClick={() => void fetchBets()}
              disabled={loading}
              className="self-start md:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-white/10 transition active:scale-95 disabled:opacity-50"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              <span>Refresh Odds</span>
            </button>
          </div>
        </div>
      </section>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-xs font-mono uppercase font-bold">Elite Picks</span>
            <Award size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {data?.elite_count ?? 0}
          </div>
          <div className="text-[11px] text-amber-300/70 font-mono">Edge &gt;= 8.0% against book</div>
        </div>

        <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-blue-400">
            <span className="text-xs font-mono uppercase font-bold">Strong Picks</span>
            <ShieldCheck size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {data?.strong_count ?? 0}
          </div>
          <div className="text-[11px] text-blue-300/70 font-mono">Edge &gt;= 4.0% against book</div>
        </div>

        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-xs font-mono uppercase font-bold">Avg Model Edge</span>
            <Percent size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            +{data?.avg_edge_pct ?? 0}%
          </div>
          <div className="text-[11px] text-emerald-300/70 font-mono">Across verified markets</div>
        </div>

        <div className="rounded-xl border border-purple-500/30 bg-purple-500/5 p-4 space-y-1">
          <div className="flex items-center justify-between text-purple-400">
            <span className="text-xs font-mono uppercase font-bold">Filtered Kelly</span>
            <DollarSign size={18} />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300">
            {totalKellyStake}%
          </div>
          <div className="text-[11px] text-purple-300/70 font-mono">Max suggested portfolio stake</div>
        </div>
      </div>

      {/* Interactive Filters Bar */}
      <div className="rounded-xl border border-white/10 bg-slate-900/60 p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <Filter size={14} />
            <span>Filters:</span>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10">
            {["All", "Match Winner", "Total Runs"].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`px-3 py-1 rounded text-xs font-mono transition ${
                  typeFilter === t
                    ? "bg-emerald-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Tier Filter */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10">
            {["All", "Elite Pick", "Strong"].map((t) => (
              <button
                key={t}
                onClick={() => setTierFilter(t)}
                className={`px-3 py-1 rounded text-xs font-mono transition ${
                  tierFilter === t
                    ? "bg-blue-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Min Edge Selector */}
        <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
          <span>Min Edge:</span>
          <select
            value={minEdge}
            onChange={(e) => setMinEdge(parseFloat(e.target.value))}
            className="bg-slate-950 border border-white/10 rounded px-2.5 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-emerald-500"
          >
            <option value={0.02}>&gt;= 2.0%</option>
            <option value={0.04}>&gt;= 4.0% (Default)</option>
            <option value={0.06}>&gt;= 6.0%</option>
            <option value={0.08}>&gt;= 8.0% (Elite)</option>
          </select>
        </div>
      </div>

      {/* Visual Edge Distribution Chart */}
      {filteredBets.length > 0 && (
        <section className="rounded-2xl border border-white/10 bg-slate-900/80 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono font-bold text-slate-200 flex items-center gap-2">
              <BarChart2 size={16} className="text-emerald-400" />
              <span>Model Edge Distribution vs DraftKings (%)</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">
              {filteredBets.length} qualifying opportunities
            </span>
          </div>

          <div className="space-y-2.5 pt-2">
            {filteredBets.map((b, idx) => {
              const edgePct = (b.edge * 100).toFixed(1);
              const barWidth = Math.min(100, Math.max(10, b.edge * 600));
              const isElite = b.tier === "Elite Pick";
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-300 font-semibold truncate max-w-md">
                      {b.bet} <span className="text-slate-500">({b.match})</span>
                    </span>
                    <span className={`font-bold ${isElite ? "text-amber-400" : "text-blue-400"}`}>
                      +{edgePct}% edge
                    </span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-slate-950 overflow-hidden border border-white/5">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isElite
                          ? "bg-gradient-to-r from-amber-500 to-emerald-400"
                          : "bg-gradient-to-r from-blue-600 to-cyan-400"
                      }`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Bets Data Table */}
      <section className="rounded-2xl border border-white/10 bg-slate-900/90 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-slate-950/40">
          <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300">
            Qualifying Opportunities Ledger
          </h2>
          <span className="text-xs font-mono text-emerald-400">
            Kelly Formula: f* = (edge / b) · 0.25
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 font-mono text-sm space-y-3">
            <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto" />
            <p>Scanning DraftKings markets and calculating Kelly Criterion stakes...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-amber-400 font-mono text-sm space-y-2">
            <p>⚠️ {error}</p>
            <button
              onClick={() => void fetchBets()}
              className="px-3 py-1.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs"
            >
              Retry
            </button>
          </div>
        ) : filteredBets.length === 0 ? (
          <div className="p-12 text-center text-slate-400 font-mono text-sm space-y-2">
            <p className="text-base font-semibold text-slate-300">No bets meet the selected criteria.</p>
            <p className="text-xs text-slate-500">Try lowering the minimum edge threshold or clearing filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-white/10 bg-slate-950/70 text-slate-400 uppercase text-[11px]">
                  <th className="py-3 px-4">Tier</th>
                  <th className="py-3 px-4">Bet Pick</th>
                  <th className="py-3 px-4">Fixture</th>
                  <th className="py-3 px-4 text-center">Model Win %</th>
                  <th className="py-3 px-4 text-center">DK Implied %</th>
                  <th className="py-3 px-4 text-center">DK Odds</th>
                  <th className="py-3 px-4 text-center">Edge</th>
                  <th className="py-3 px-4 text-center">Kelly Stake</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-200">
                {filteredBets.map((b, idx) => {
                  const isElite = b.tier === "Elite Pick";
                  return (
                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isElite
                              ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                              : "bg-blue-500/20 text-blue-300 border border-blue-500/40"
                          }`}
                        >
                          {isElite ? "🏆 ELITE" : "⭐ STRONG"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-white text-sm">
                        {b.bet}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">
                        {b.match}
                      </td>
                      <td className="py-3.5 px-4 text-center font-semibold text-emerald-400">
                        {(b.model_prob * 100).toFixed(0)}%
                      </td>
                      <td className="py-3.5 px-4 text-center text-slate-400">
                        {(b.implied_prob * 100).toFixed(0)}%
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-100">
                        {b.dk_odds}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-block px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-bold border border-emerald-500/30">
                          +{(b.edge * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-purple-300">
                        {b.kelly_stake}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(
                              `THENITISHKR-SPORTS Pick: ${b.bet} (${b.match}) | Edge: +${(b.edge * 100).toFixed(1)}% | DK Odds: ${b.dk_odds} | 25% Kelly: ${b.kelly_stake}`
                            );
                            alert("Pick copied to clipboard!");
                          }}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/10 text-[11px] inline-flex items-center gap-1 transition"
                        >
                          <span>Copy</span>
                          <ArrowUpRight size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
