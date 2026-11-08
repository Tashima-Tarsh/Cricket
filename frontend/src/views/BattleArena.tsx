import React from "react";
import { Swords, MapPin } from "lucide-react";
import type { HeadToHeadBattle, BallTrajectory } from "../types";
import { useMatchContext } from "../context/MatchContext";
import { Stadium3D } from "../components/Stadium3D";

interface Props { battles: HeadToHeadBattle[]; trajectories: BallTrajectory[]; }

export const BattleArena: React.FC<Props> = ({battles,trajectories}) => {
  const {currentMatch,currentPlayers,venuePlayers} = useMatchContext();
  const [filter,setFilter] = React.useState("ALL");
  const home = currentMatch.teams.home.code, away=currentMatch.teams.away.code;
  const byName=new Map(currentPlayers.map(p=>[p.name,p]));
  const realBattles=battles.filter(b => {
    const batter=byName.get(b.batter_name),bowler=byName.get(b.bowler_name);
    return Boolean(batter && bowler && batter.team !== bowler.team && b.balls > 0);
  });
  const filtered=realBattles.filter(b=>filter==="ALL" || byName.get(b.batter_name)?.team===filter);
  const [chosen,setChosen] = React.useState(0);
  const active=filtered[Math.min(chosen,Math.max(0,filtered.length-1))];
  React.useEffect(()=>{setChosen(0);setFilter("ALL");},[currentMatch.id]);
  return <div className="space-y-5">
    <header className="bg-slate-900/80 border border-white/10 rounded-2xl p-6 space-y-2">
      <h1 className="text-2xl font-bold text-white flex gap-2 items-center"><Swords size={24}/> Opposition battle analysis</h1>
      <p className="text-slate-300">{currentMatch.name} · {home} vs {away}</p>
      <p className="text-amber-300 text-xs">Only observed cross-team head-to-head deliveries. No synthetic strike rates, tracking, or predicted wicket probability.</p>
    </header>
    <div className="flex flex-wrap gap-2">
      {[["ALL","All batting sides"],[home,`${home} batters`],[away,`${away} batters`]].map(([key,label])=>
        <button key={key} type="button" onClick={()=>{setFilter(key);setChosen(0);}}
          className={`px-4 py-2 rounded-lg text-xs ${filter===key?"bg-emerald-700 text-white":"bg-slate-800 text-slate-300"}`}>{label} ({key==="ALL"?realBattles.length:realBattles.filter(b=>byName.get(b.batter_name)?.team===key).length})</button>)}
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <section className="lg:col-span-1 border border-white/10 rounded-xl bg-slate-900/70 p-4 space-y-2 max-h-96 overflow-y-auto">
        <h2 className="text-slate-300 text-xs">Select observed encounter</h2>
        {filtered.map((b,i)=><button key={`${b.batter_id}-${b.bowler_id}-${i}`} onClick={()=>setChosen(i)} className={`w-full text-left text-xs p-3 rounded ${chosen===i?"bg-emerald-900 text-white":"bg-slate-800/80 text-slate-300"}`}>
          {b.batter_name} vs {b.bowler_name} · {b.balls} balls
        </button>)}
        {!filtered.length&&<p className="text-slate-400 text-xs">No records for this batting side.</p>}
      </section>
      <section className="lg:col-span-2 border border-white/10 rounded-xl bg-slate-900/70 p-5 space-y-4">
        {active ? <>
          <h2 className="font-bold text-white">{active.batter_name} vs {active.bowler_name}</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[["Balls",active.balls],["Runs",active.runs],["Dismissals",active.dismissals],["Strike rate",active.strike_rate.toFixed(1)]].map(([k,v])=>
              <div key={k} className="bg-slate-800 p-3 rounded"><p className="text-slate-400 text-xs">{k}</p><p className="text-white text-lg font-bold">{v}</p></div>)}
          </div>
          <p className="text-slate-400 text-xs">Sample: {active.balls} recorded balls. Small samples are not stable predictive evidence.</p>
        </> : <p className="text-slate-400">No observed opposition encounters for this fixture.</p>}
      </section>
    </div>
    <section className="border border-white/10 rounded-xl bg-slate-900/70 p-5 space-y-3">
      <h2 className="text-white font-bold flex items-center gap-2"><MapPin size={16}/> Venue data: {currentMatch.venue.name}</h2>
      <p className="text-slate-300 text-sm">{venuePlayers.length} venue-player records. Other stadiums' data is not substituted.</p>
      <p className="text-slate-400 text-xs">{trajectories.length ? `${trajectories.length} source-supplied trajectories` : "No recorded delivery trajectories from a verified provider."}</p>
      <Stadium3D className="h-80" />
    </section>
  </div>;
};
