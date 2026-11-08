import React from "react";
import { Activity, Database, MapPin, ShieldCheck, Swords, Target, Trophy } from "lucide-react";
import type { MatchInfo, Player, HeadToHeadBattle, WorkspaceTab } from "../types";
import { useMatchContext } from "../context/MatchContext";

interface Props {
  match: MatchInfo;
  players: Player[];
  battles: HeadToHeadBattle[];
  onNavigate: (tab: WorkspaceTab) => void;
}

export const CommandCenter: React.FC<Props> = ({ match, players, battles, onNavigate }) => {
  const { currentLineups, venuePlayers, currentProviders, activeOvers, setActiveOvers, stateStatus, lastUpdated } = useMatchContext();
  const [tossFeed, setTossFeed] = React.useState<Record<string, unknown> | null>(null);
  const [feedError, setFeedError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const refreshToss = React.useCallback(async () => {
    if (!match.id) return;
    setLoading(true);
    setFeedError(null);
    try {
      const res = await fetch(`/api/live/toss-feed?match_id=${encodeURIComponent(match.id)}`);
      if (!res.ok) throw new Error(`Feed not available (HTTP ${res.status})`);
      const payload = await res.json();
      const feed = payload.feed;
      setTossFeed(feed && typeof feed === "object" ? feed : null);
    } catch (err) {
      setFeedError(err instanceof Error ? err.message : "Toss telemetry unavailable");
      setTossFeed(null);
    } finally {
      setLoading(false);
    }
  }, [match.id]);

  const getOptional = (value: unknown): string =>
    typeof value === "string" && value.trim() ? value : "Not available";
  const verifiedXI = players.filter(p => p.is_confirmed_xi).length;
  const venue = match.venue;
  const labeledBattles = battles.filter(b =>
    players.some(p => p.name === b.batter_name) &&
    players.some(p => p.name === b.bowler_name));
  const panels = [
    { title: "Players in selected fixture", value: String(players.length), label: `${verifiedXI} user-attested in XI`, icon: <ShieldCheck size={18} /> },
    { title: "Observed head-to-head records", value: String(labeledBattles.length), label: "Only records supported by local archive", icon: <Swords size={18} /> },
    { title: "Venue player records", value: String(venuePlayers.length), label: "No invented venue observations", icon: <Database size={18} /> },
    { title: "Generated portfolios", value: String(currentLineups.length), label: "Research output; not a win forecast", icon: <Trophy size={18} /> }
  ];

  return <div className="space-y-5">
    <section className="rounded-2xl bg-slate-900/90 border border-white/10 p-6 space-y-4">
      <div className="flex flex-wrap gap-2 text-xs font-mono text-amber-300">
        <span className="border border-amber-400/30 rounded px-2 py-1">USER-ATTESTED FIXTURE · NOT PROVIDER VERIFIED</span>
        <span className="border border-white/10 rounded px-2 py-1">{stateStatus.toUpperCase()}</span>
      </div>
      <h1 className="text-white font-extrabold text-3xl">{match.name}</h1>
      <p className="text-slate-300">{match.teams.home.name} vs {match.teams.away.name} · {match.format}</p>
      <p className="text-slate-300 flex items-center gap-2"><MapPin size={16} />{venue?.name || "Venue not supplied"}</p>
      <p className="text-slate-300">Toss: {match.toss?.statement || "Not attested"}</p>
      <p className="text-xs text-slate-400">Last local snapshot: {lastUpdated ? new Date(lastUpdated).toLocaleString() : "Not loaded"}. Provenance does not independently verify announced teams, surface or form.</p>
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={() => onNavigate("fantasy-lab")} className="px-4 py-2 rounded-lg bg-emerald-500 text-slate-950 font-bold">Optimize lineups</button>
        <button type="button" onClick={() => onNavigate("battle-arena")} className="px-4 py-2 rounded-lg border border-white/20 text-white">View recorded battles</button>
        <button type="button" onClick={() => onNavigate("providers")} className="px-4 py-2 rounded-lg border border-white/20 text-white">Inspect providers</button>
      </div>
    </section>
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
      {panels.map(p => <section key={p.title} className="bg-slate-900/70 rounded-xl border border-white/10 p-5 space-y-2">
        <div className="flex justify-between text-slate-400 text-xs">{p.title}{p.icon}</div>
        <div className="text-white text-3xl font-bold">{p.value}</div>
        <p className="text-slate-400 text-xs">{p.label}</p>
      </section>)}
    </div>
    <section className="bg-slate-900/70 rounded-xl border border-white/10 p-5 space-y-4">
      <div className="flex flex-wrap justify-between gap-3">
        <h2 className="text-white font-bold flex items-center gap-2"><Activity size={18} /> Toss feed — separate from manual XI</h2>
        <button type="button" onClick={() => void refreshToss()} disabled={loading} className="rounded border border-white/20 text-cyan-300 text-xs px-3 py-2 disabled:opacity-50">
          {loading ? "Checking..." : "Check source"}
        </button>
      </div>
      <p className="text-slate-300 text-sm">Source statement: {getOptional(tossFeed?.toss_statement)}</p>
      {feedError && <p role="alert" className="text-amber-300 text-sm">{feedError}</p>}
      {!tossFeed && <p className="text-sm text-slate-400">No verified live telemetry is connected to this view.</p>}
      <div className="flex items-center gap-3 text-xs text-slate-400">
        <Target size={16} /> Overs scenario
        <select aria-label="Scenario overs" value={activeOvers} onChange={e => setActiveOvers(Number(e.target.value))}
          className="bg-slate-800 text-white rounded border border-white/10 px-2 py-1">
          {[20, 18, 15, 12, 10, 8, 5].map(o => <option key={o} value={o}>{o} overs</option>)}
        </select>
        <span>Scenario only, not official reduction</span>
      </div>
    </section>
    <section className="bg-slate-900/70 rounded-xl border border-white/10 p-5 space-y-2">
      <h2 className="text-white font-bold">Configured provider connections</h2>
      {currentProviders.length
        ? currentProviders.map(p => <p key={p.id} className="text-sm text-slate-300">{p.name}: {p.status}</p>)
        : <p className="text-slate-400 text-sm">No provider status available.</p>}
    </section>
  </div>;
};
