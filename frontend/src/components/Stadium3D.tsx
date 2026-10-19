import React, { lazy, Suspense, useState } from "react";
import type { Stadium3DProps } from "./StadiumWebGL";
import { BALL_TRAJECTORIES } from "../data/mockData";
import { useGraphics } from "../hooks/useGraphics";
const WebGL = lazy(() => import("./StadiumWebGL").then(module => ({default: module.StadiumWebGL})));
class GraphicsBoundary extends React.Component<{children: React.ReactNode; fallback: React.ReactNode}, {failed:boolean}> {
  state = {failed:false};
  static getDerivedStateFromError() { return {failed:true}; }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}
export const Stadium3D: React.FC<Stadium3DProps> = props => {
  const {preferences,update} = useGraphics();
  const [selection,setSelection] = useState(props.selectedTrajectory || null);
  const balls = BALL_TRAJECTORIES.filter(ball => (!props.filterPhase || props.filterPhase === "All" || ball.phase === props.filterPhase) && (!props.filterBowlerType || props.filterBowlerType === "All" || (props.filterBowlerType === "Pace" ? ball.speed_kmh >= 125 : ball.speed_kmh < 125)));
  const choose = (ball: typeof balls[number]) => {setSelection(ball); props.onSelectTrajectory?.(ball);};
  const fallback = <div className="p-4 bg-stone-100 h-full overflow-auto"><p className="evidence-note">Illustrative pitch | sample deliveries, not measured tracking data.</p><svg viewBox="0 0 200 280" aria-label="Two-dimensional pitch showing sample delivery impact positions" className="w-full max-h-64"><rect x="45" y="10" width="110" height="260" rx="8" fill="#d9cca9"/><path d="M45 35H155 M45 245H155 M60 10V270 M140 10V270" stroke="#fff" strokeWidth="3"/>{balls.map(ball => <circle key={ball.id} cx={100+ball.pitch_x*25} cy={35+ball.pitch_y*10} r={selection?.id === ball.id ? 7 : 4} fill={selection?.id === ball.id ? "#863f24" : "#365d47"}/>)}</svg><div className="flex flex-wrap gap-2">{balls.map(ball => <button key={ball.id} className="border border-stone-400 px-2" aria-pressed={selection?.id === ball.id} onClick={() => choose(ball)}>{ball.over}.{ball.ball} | {ball.length}</button>)}</div>{selection && <p role="status">{selection.bowler} to {selection.batter}: {selection.length}, {selection.outcome}. Sample speed {selection.speed_kmh} km/h.</p>}</div>;
  return <section className={props.className || "w-full h-full"} style={{minHeight:360}}><div className="flex items-center justify-between gap-2 py-2"><span className="text-xs">Pitch illustration</span><button className="border border-stone-400 px-3" onClick={() => update({mode:preferences.mode === "2D" ? "3D" : "2D"})}>Use {preferences.mode === "2D" ? "3D" : "2D"}</button></div><div style={{height:"calc(100% - 52px)",minHeight:300}}>{preferences.mode === "2D" ? fallback : <GraphicsBoundary fallback={<><p role="alert">3D unavailable. Showing the 2D pitch.</p>{fallback}</>}><Suspense fallback={<p role="status">Loading optional 3D view?</p>}><WebGL {...props} selectedTrajectory={props.selectedTrajectory || selection} onSelectTrajectory={choose}/></Suspense></GraphicsBoundary>}</div></section>;
};
