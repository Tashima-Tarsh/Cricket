import React from "react";
import { Compass, Database, MapPin, Swords } from "lucide-react";
import { useMatchContext } from "../context/MatchContext";
import { Stadium3D } from "../components/Stadium3D";

export const PitchLab: React.FC = () => {
  const { currentMatch, currentBattles, currentPlayers, venuePlayers, navigateToWorkspace } = useMatchContext();
  const [phase, setPhase] = React.useState<"All" | "Powerplay" | "Middle" | "Death">("All");
  const venue = currentMatch.venue;
  const details: Array<[string, string]> = [
    ["Surface notes", venue.pitch_nature || "Not observed"],
    ["Soil type", venue.soil_type || "Not observed"],
    ["Average first innings", venue.avg_first_innings > 0 ? String(venue.avg_first_innings) : "Not available"],
    ["Average second innings", venue.avg_second_innings > 0 ? String(venue.avg_second_innings) : "Not available"],
    ["Pace wicket share", venue.pace_wicket_pct > 0 ? `${venue.pace_wicket_pct}%` : "Not available"],
    ["Spin wicket share", venue.spin_wicket_pct > 0 ? `${venue.spin_wicket_pct}%` : "Not available"],
  ];
  const validNames = new Set(currentPlayers.map(p => p.name));
  const battles = currentBattles.filter(b => validNames.has(b.batter_name) && validNames.has(b.bowler_name));
  return <div className="space-y-5">
    <header className="bg-slate-900/80 border border-white/10 rounded-2xl p-6 space-y-2">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2"><Compass size={24} /> Venue & pitch intelligence</h1>
      <p className="text-slate-300 flex items-center gap-2"><MapPin size={16}/>{venue.name || "No venue supplied"} · {venue.city || "City not supplied"}</p>
      <p className="text-amber-300 text-xs">Venue details reflect the selected fixture's supplied metadata, not measured live pitch sensors. A missing sample is shown as unavailable.</p>
    </header>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {details.map(([label,value]) => <div key={label} className="rounded-xl border border-white/10 bg-slate-900/70 p-4">
        <p className="text-slate-400 text-xs">{label}</p>
        <p className="text-white font-medium mt-2">{value}</p>
      </div>)}
    </div>
    <section className="border border-white/10 bg-slate-900/70 rounded-2xl p-5 space-y-3">
      <h2 className="text-white font-bold">Recorded venue boundaries</h2>
      {Object.entries(venue.boundaries || {}).length
        ? <div className="flex flex-wrap gap-2">{Object.entries(venue.boundaries).map(([side,metres]) =>
            <span key={side} className="rounded border border-white/10 text-slate-300 text-xs px-2 py-1">{side.replaceAll("_"," ")}: {metres ? `${metres} m` : "unavailable"}</span>)}</div>
        : <p className="text-slate-400 text-sm">No measured dimensions supplied.</p>}
      <p className="text-slate-400 text-xs">Dimensions are user/provider-supplied only; no stadium measurements have been independently confirmed.</p>
    </section>
    <section className="border border-white/10 bg-slate-900/70 rounded-2xl p-5 space-y-3">
      <h2 className="text-white font-bold flex items-center gap-2"><Swords size={18}/> Observed batter–bowler encounters</h2>
      <p className="text-slate-400 text-sm">For the current two-team pool only. No guessed speeds, dismissal risks, or fielding prescriptions.</p>
      <label className="text-slate-300 text-xs">Match phase filter: <select className="bg-slate-800 border border-white/20 rounded p-1 ml-2" value={phase} onChange={e=>setPhase(e.target.value as typeof phase)}>
        {["All","Powerplay","Middle","Death"].map(s=><option key={s}>{s}</option>)}
      </select></label>
      <p className="text-amber-300 text-xs">{phase === "All" ? "All observed records" : `${phase} filter requires phase-labelled deliveries; aggregate results are withheld.`}</p>
      {phase === "All" && battles.length ? <div className="overflow-x-auto"><table className="w-full text-left text-xs text-slate-300">
        <thead><tr className="text-slate-400 border-b border-white/10">{["Batter","Bowler","Balls","Runs","Dismissals","Strike rate"].map(h=><th className="p-2" key={h}>{h}</th>)}</tr></thead>
        <tbody>{battles.slice(0,40).map((b,i)=><tr key={`${b.batter_id}-${b.bowler_id}-${i}`} className="border-b border-white/5">
          <td className="p-2">{b.batter_name}</td><td className="p-2">{b.bowler_name}</td><td className="p-2">{b.balls}</td>
          <td className="p-2">{b.runs}</td><td className="p-2">{b.dismissals}</td><td className="p-2">{b.strike_rate.toFixed(1)}</td>
        </tr>)}</tbody></table></div> : <p className="text-slate-400 text-sm">No phase-matched, observed encounters available.</p>}
      <button type="button" onClick={()=>navigateToWorkspace("battle-arena")} className="bg-cyan-700 text-white px-4 py-2 rounded-lg">Open Battle Arena</button>
    </section>
    <section className="border border-white/10 bg-slate-900/70 rounded-2xl p-5 space-y-2">
      <h2 className="text-white font-bold flex items-center gap-2"><Database size={18}/> Pitch visualization</h2>
      <p className="text-slate-400 text-sm">{venuePlayers.length} recorded venue-player entries for this selected fixture. The diagram is not ball-tracking telemetry.</p>
      <Stadium3D className="w-full h-96" />
    </section>
  </div>;
};
