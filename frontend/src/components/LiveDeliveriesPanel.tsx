"use client";
import React, { useEffect, useState, useCallback } from "react";
import { ChevronRight, Clock, Database, RefreshCw, Activity } from "lucide-react";
import { DeliveryRecord } from "../types";

interface LiveDeliveriesPanelProps {
  matchId: string;
  limit?: number;
}

const DELIVERY_OUTCOME_COLOR: Record<string, string> = {
  "Dot": "text-slate-400",
  "1 Run": "text-emerald-300",
  "2 Runs": "text-cyan-300",
  "Boundary 4": "text-blue-300",
  "Six": "text-amber-300",
  "Wicket": "text-rose-400",
};

export const LiveDeliveriesPanel: React.FC<LiveDeliveriesPanelProps> = ({
  matchId,
  limit = 40,
}: LiveDeliveriesPanelProps) => {
  const [deliveries, setDeliveries] = useState<DeliveryRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFetched, setLastFetched] = useState<string | null>(null);

  const fetchDeliveries = useCallback(async () => {
    if (!matchId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/duckdb/deliveries?match_id=${encodeURIComponent(matchId)}&limit=${limit}`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(`Deliveries request failed (${res.status}).`);
      const data = await res.json();
      const rows: DeliveryRecord[] = Array.isArray(data.deliveries) ? data.deliveries : [];
      setDeliveries(rows);
      setLastFetched(new Date().toISOString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load live ball-by-ball data.");
      console.warn("LiveDeliveriesPanel fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, [matchId, limit]);

  useEffect(() => {
    void fetchDeliveries();
    const handler = (e: CustomEvent) => {
      if ((e.detail as any)?.matchId === matchId) {
        void fetchDeliveries();
      }
    };
    window.addEventListener("cricket-data-refreshed", handler as EventListener);
    return () => window.removeEventListener("cricket-data-refreshed", handler as EventListener);
  }, [matchId, limit, fetchDeliveries]);

  const inningsMap: Record<number, string> = { 1: "1st Innings", 2: "2nd Innings" };

  const deliveryOutcome = (d: DeliveryRecord): string => {
    if (d.is_wicket) return "Wicket";
    if (d.runs_total >= 6) return "Six";
    if (d.runs_total === 4) return "Boundary 4";
    if (d.runs_total >= 1) return `${d.runs_total} Run${d.runs_total > 1 ? "s" : ""}`;
    return "Dot";
  };

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/80 p-5 shadow-xl backdrop-blur-xl flex flex-col h-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <Database size={16} className="text-cyan-400 shrink-0" />
          <div>
            <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider font-bold">
              Live Ball-by-Ball — DuckDB Archive
            </div>
            <div className="text-[10px] text-slate-400 font-sans">
              Real deliveries, no synthetic fabrication
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
            error ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
          }`}>
            {loading ? "Fetching…" : error ? "Offline" : `Live • ${deliveries.length} deliveries`}
          </span>
          <button
            onClick={() => void fetchDeliveries()}
            disabled={loading}
            className="p-1.5 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-all shrink-0"
            title="Refresh deliveries"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          {lastFetched && (
            <span className="text-[10px] text-slate-500 font-mono">
              {new Date(lastFetched).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {error && (
        <p role="alert" className="mb-3 p-3 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono">
          {error}
        </p>
      )}

      <div className="relative flex-1 min-h-[260px] overflow-x-auto overflow-y-auto border border-white/5 rounded-xl bg-slate-950/50">
        {loading && deliveries.length === 0 && (
          <div className="p-8 text-center text-slate-400 text-xs font-mono">
            <Activity className="animate-spin w-5 h-5 mx-auto mb-2" />
            Loading real ball-by-ball data…
          </div>
        )}
        {!loading && deliveries.length === 0 && !error && (
          <div className="p-8 text-center text-slate-500 text-xs font-mono">
            No deliveries indexed for this match yet.
          </div>
        )}
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-slate-950/40 text-slate-400 font-mono uppercase tracking-wider">
              <th className="py-2 px-3 w-16">Over.Ball</th>
              <th className="py-2 px-3">Bowler → Batter</th>
              <th className="py-2 px-3 w-20 text-center">Phase</th>
              <th className="py-2 px-3 w-16 text-center">Runs</th>
              <th className="py-2 px-3 w-20 text-center">Outcome</th>
              <th className="py-2 px-3 w-24 text-center">Wicket</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {deliveries.slice().reverse().map((d) => {
              const phaseColor: Record<string, string> = {
                Powerplay: "text-emerald-300",
                Middle: "text-cyan-300",
                Death: "text-amber-300",
              };
              return (
                <tr
                  key={`${d.match_id}-${d.innings}-${d.over}-${d.ball}`}
                  className="hover:bg-white/5 transition-colors group"
                >
                  <td className="py-2 px-3 font-mono text-slate-300">
                    {d.over}.{d.ball}
                  </td>
                  <td className="py-2 px-3 flex items-center gap-2">
                    <span className="text-[10px] font-bold text-slate-400 truncate max-w-[70px]">
                      {d.bowler}
                    </span>
                    <span className="text-[10px] text-white font-bold truncate max-w-[90px]">
                      {d.batter}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-center">
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold border ${phaseColor[d.phase] || "text-slate-400"} border-current`}>
                      {d.phase}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-center font-mono font-bold">
                    <span className={`text-white ${d.runs_total >= 4 ? "text-amber-300" : "text-slate-300"}`}>
                      {d.runs_total}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-center">
                    <span className={`text-[10px] font-bold ${DELIVERY_OUTCOME_COLOR[deliveryOutcome(d)] || "text-slate-400"}`}>
                      {deliveryOutcome(d)}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-center">
                    {d.is_wicket ? (
                      <span className="text-rose-400 font-mono font-bold text-xs">{d.wicket_type || "Wicket"}</span>
                    ) : (
                      <span className="text-slate-500 text-[10px]">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="absolute bottom-1 left-1 text-[10px] text-slate-500 font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-white/5 backdrop-blur">
          Source: Cricsheet ball-by-ball archive (DuckDB)
        </div>
      </div>
    </section>
  );
};
