import React from "react";
import { Download, Search, Database } from "lucide-react";
import type { DeliveryRecord } from "../types";
import { useMatchContext } from "../context/MatchContext";

export const BallByBallLab: React.FC = () => {
  const { currentMatch } = useMatchContext();
  const [deliveries,setDeliveries] = React.useState<DeliveryRecord[]>([]);
  const [loading,setLoading] = React.useState(false);
  const [error,setError] = React.useState<string | null>(null);
  const [phase,setPhase] = React.useState("ALL");
  const [innings,setInnings] = React.useState("ALL");
  const [query,setQuery] = React.useState("");
  React.useEffect(() => {setDeliveries([]);setError(null);},[currentMatch.id]);
  const load = async () => {
    if (!currentMatch.id) return;
    setLoading(true);setError(null);setDeliveries([]);
    try {
      const response = await fetch(`/api/duckdb/deliveries?limit=500&match_id=${encodeURIComponent(currentMatch.id)}`);
      if (!response.ok) throw new Error(`Historical delivery source returned ${response.status}`);
      const result = await response.json();
      if (!Array.isArray(result.deliveries)) throw new Error("Delivery feed lacks verified records");
      // Reject delivery data for any unrelated fixture: no cross-match fallback.
      const records = (result.deliveries as DeliveryRecord[]).filter(d=>d.match_id===currentMatch.id);
      setDeliveries(records);
      if (records.length === 0) setError("No delivery records for this exact fixture. No sample overs will be inserted.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delivery records not available");
    } finally {setLoading(false);}
  };
  const filtered = deliveries.filter(d =>
    (phase==="ALL" || d.phase===phase) &&
    (innings==="ALL" || String(d.innings)===innings) &&
    (!query || [d.batter,d.bowler,d.shot_zone||""].some(s=>s.toLowerCase().includes(query.toLowerCase()))));
  const runs=filtered.reduce((n,d)=>n+d.runs_total,0);
  const wickets=filtered.filter(d=>d.is_wicket).length;
  const dots=filtered.filter(d=>!d.runs_total).length;
  const boundaries=filtered.filter(d=>d.runs_batter>=4).length;
  const escapeCsv=(s:unknown)=>`"${String(s ?? "").replaceAll('"','""')}"`;
  const exportCsv=()=>{
    if(!filtered.length)return;
    const headers=["match_id","innings","over","ball","batter","bowler","runs_batter","runs_extras","runs_total","is_wicket","wicket_type","phase","speed_kmh","shot_zone"] as const;
    const csv=[headers.join(","),...filtered.map(d=>headers.map(k=>escapeCsv(d[k])).join(","))].join("\n");
    const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    const a=document.createElement("a");a.href=url;a.download=`deliveries_${currentMatch.id}.csv`;a.click();URL.revokeObjectURL(url);
  };
  return <div className="space-y-5">
    <header className="bg-slate-900/80 border border-white/10 p-6 rounded-2xl space-y-3">
      <h1 className="text-white text-2xl font-bold flex gap-2 items-center"><Database size={22}/> Ball-by-ball evidence</h1>
      <p className="text-slate-300 text-sm">{currentMatch.name} · Only deliveries returned for this exact fixture ID.</p>
      <p className="text-amber-300 text-xs">Speed and shot coordinates appear only if present in the archival record. This feed is not an official real-time tracking service.</p>
      <button type="button" onClick={()=>void load()} disabled={!currentMatch.id||loading}
        className="bg-emerald-700 text-white rounded-lg px-4 py-2 disabled:opacity-60">{loading?"Checking...":"Load recorded deliveries"}</button>
      {error&&<p role="status" className="text-amber-300 text-sm">{error}</p>}
    </header>
    <div className="flex flex-wrap gap-2 text-sm items-center">
      <select aria-label="Innings filter" value={innings} onChange={e=>setInnings(e.target.value)} className="p-2 bg-slate-800 text-white rounded">
        <option value="ALL">All innings</option><option value="1">Innings 1</option><option value="2">Innings 2</option>
      </select>
      <select aria-label="Phase filter" value={phase} onChange={e=>setPhase(e.target.value)} className="p-2 bg-slate-800 text-white rounded">
        {["ALL","Powerplay","Middle","Death"].map(v=><option key={v}>{v}</option>)}
      </select>
      <label className="flex gap-2 items-center text-slate-300"><Search size={16}/><input aria-label="Find batter or bowler" value={query}
        onChange={e=>setQuery(e.target.value)} className="p-2 bg-slate-800 text-white rounded" placeholder="Batter / bowler"/></label>
      <button type="button" onClick={exportCsv} disabled={!filtered.length} className="p-2 rounded border border-white/20 text-slate-200 disabled:opacity-50 flex items-center gap-2"><Download size={16}/> CSV</button>
    </div>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {[["Recorded deliveries",filtered.length],["Runs",runs],["Wickets",wickets],["Dot deliveries",dots],["Boundaries",boundaries]].map(([key,val])=>
        <div key={key} className="bg-slate-900/70 border border-white/10 rounded-xl p-3"><p className="text-slate-400 text-xs">{key}</p><p className="text-white text-xl font-bold">{val}</p></div>)}
    </div>
    <section className="bg-slate-900/70 border border-white/10 rounded-xl p-4 overflow-x-auto">
      <table className="w-full text-left text-xs text-slate-200"><thead><tr className="text-slate-400 border-b border-white/10">
        {["Ball","Batter","Bowler","Runs","Wicket","Speed","Zone"].map(h=><th className="p-2" key={h}>{h}</th>)}
      </tr></thead><tbody>{filtered.map((d,i)=><tr key={`${d.match_id}-${d.innings}-${d.over}-${d.ball}-${i}`} className="border-b border-white/5">
        <td className="p-2">{d.innings}:{d.over}.{d.ball}</td><td className="p-2">{d.batter}</td><td className="p-2">{d.bowler}</td><td className="p-2">{d.runs_total}</td><td className="p-2">{d.is_wicket?"Yes":"No"}</td>
        <td className="p-2">{d.speed_kmh ?? "–"}</td><td className="p-2">{d.shot_zone || "–"}</td>
      </tr>)}</tbody></table>
      {!filtered.length&&<p className="text-slate-400 py-4 text-sm">No recorded deliveries match these filters.</p>}
    </section>
  </div>;
};
