import React, { useState } from "react";
import { X, Database, FileText, Swords } from "lucide-react";
import { useDialog } from "../hooks/useDialog";
import { useMatchContext } from "../context/MatchContext";

interface Props { isOpen: boolean; onClose: () => void; }

export const IntelligenceDrawer: React.FC<Props> = ({ isOpen, onClose }) => {
  const dialogRef = useDialog(isOpen,onClose);
  const { currentMatch, selectedBatter, selectedBowler, selectedPhase, currentBattles, navigateToWorkspace } = useMatchContext();
  const [notes,setNotes] = useState(() => {
    try {return localStorage.getItem("cricket.notes.v1") || "";} catch{return "";}
  });
  const [saveState,setSaveState] = useState("Notes stay in your browser; not on the server.");
  const match = currentBattles.find(b => selectedBatter && selectedBowler &&
    b.batter_name === selectedBatter.name && b.bowler_name === selectedBowler.name);
  if (!isOpen) return null;
  return <div ref={dialogRef} role="dialog" aria-modal="true" aria-label="Analyst notes" tabIndex={-1}
    className="fixed inset-y-0 right-0 w-full max-w-sm z-50 bg-slate-900 border-l border-white/10 shadow-2xl p-5 overflow-y-auto space-y-5">
    <header className="flex justify-between items-center border-b border-white/10 pb-3">
      <h2 className="text-white font-bold">Analyst intelligence</h2>
      <button onClick={onClose} aria-label="Close" className="text-slate-300"><X size={20}/></button>
    </header>
    <p className="text-xs text-amber-300">Only observed matchups and explicitly selected fixture data are displayed. No fixed opposition or verified-live claims.</p>
    <section className="space-y-2 bg-slate-800/60 rounded-xl p-4">
      <h3 className="text-white font-semibold flex items-center gap-2"><Swords size={16}/> Selected matchup</h3>
      <p className="text-slate-300 text-sm">Fixture: {currentMatch.name || "None"} · Phase: {selectedPhase}</p>
      <p className="text-slate-300 text-sm">Batter: {selectedBatter?.name || "Not selected"} · Bowler: {selectedBowler?.name || "Not selected"}</p>
      {match ? <dl className="text-slate-300 text-sm grid grid-cols-2 gap-2">
        <dt>Recorded balls</dt><dd>{match.balls}</dd>
        <dt>Recorded runs</dt><dd>{match.runs}</dd>
        <dt>Dismissals</dt><dd>{match.dismissals}</dd>
        <dt>Strike rate</dt><dd>{match.strike_rate.toFixed(1)}</dd>
      </dl> : <p className="text-slate-400 text-sm">No verified head-to-head deliveries in the selected context.</p>}
      <button type="button" onClick={()=>{navigateToWorkspace("battle-arena");onClose();}} className="bg-emerald-700 rounded px-3 py-2 text-white text-xs">Open matchup workbench</button>
    </section>
    <section className="space-y-2 bg-slate-800/60 rounded-xl p-4">
      <h3 className="text-white font-semibold flex items-center gap-2"><Database size={16}/> Evidence status</h3>
      <p className="text-slate-300 text-sm">{currentBattles.length} available matchup entries. Forecast skill, contest rake and Rank-1 probabilities are not verified by this screen.</p>
    </section>
    <section className="space-y-2">
      <label htmlFor="analyst-notes" className="text-white font-semibold flex gap-2 items-center"><FileText size={16}/> Analyst notes</label>
      <textarea id="analyst-notes" rows={6} className="w-full rounded-lg bg-slate-800 text-white border border-white/20 p-3"
        value={notes} placeholder="Write your own matchup hypotheses"
        onChange={e=>{setNotes(e.target.value);try{localStorage.setItem("cricket.notes.v1",e.target.value);setSaveState("Notes saved locally");}catch{setSaveState("Storage unavailable");}}}/>
      <p role="status" className="text-slate-400 text-xs">{saveState}</p>
    </section>
  </div>;
};
