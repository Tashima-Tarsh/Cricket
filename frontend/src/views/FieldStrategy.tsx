import React, { useState, useEffect, useRef } from "react";
import { useMatchContext } from "../context/MatchContext";
import { FielderPosition, FieldSettingPreset } from "../types";
import {
  Shield,
  RotateCcw,
  Download,
  AlertTriangle,
  CheckCircle2,
  Bookmark,
  Users,
  Swords,
  Maximize2
} from "lucide-react";

const STANDARD_PRESETS: FieldSettingPreset[] = [
  {
    id: "new_ball_swing",
    name: "New-Ball Swing Attack (Overs 1-3)",
    category: "Powerplay",
    description: "2 Slips, attacking point, saving single at mid-off & mid-on. Exploits overcast seam.",
    bowlingStyle: "Fast",
    strikerHand: "RHB",
    fielders: [
      { id: "wk", name: "Wicketkeeper", x: 0, y: 16, isInsideCircle: true, isCatching: true },
      { id: "slip1", name: "1st Slip", x: 4, y: 17, isInsideCircle: true, isCatching: true },
      { id: "slip2", name: "2nd Slip", x: 8, y: 18, isInsideCircle: true, isCatching: true },
      { id: "gully", name: "Gully", x: 15, y: 14, isInsideCircle: true, isCatching: true },
      { id: "point", name: "Point", x: 22, y: 4, isInsideCircle: true, isCatching: false },
      { id: "cover", name: "Cover", x: 18, y: -10, isInsideCircle: true, isCatching: false },
      { id: "mid_off", name: "Mid-Off", x: 8, y: -20, isInsideCircle: true, isCatching: false },
      { id: "mid_on", name: "Mid-On", x: -8, y: -20, isInsideCircle: true, isCatching: false },
      { id: "mid_wicket", name: "Mid-Wicket", x: -20, y: -6, isInsideCircle: true, isCatching: false },
      { id: "fine_leg", name: "Deep Fine Leg", x: -32, y: 28, isInsideCircle: false, isCatching: false },
      { id: "third_man", name: "Deep Third Man", x: 30, y: 28, isInsideCircle: false, isCatching: false }
    ]
  },
  {
    id: "death_yorker_lock",
    name: "Death-Overs Yorker Lock (Overs 16-20)",
    category: "Death",
    description: "5 fielders outside the 30-yard ring on the boundary ropes. Tight off-stump protection.",
    bowlingStyle: "Fast-Medium",
    strikerHand: "RHB",
    fielders: [
      { id: "wk", name: "Wicketkeeper", x: 0, y: 16, isInsideCircle: true, isCatching: false },
      { id: "short_third", name: "Short Third", x: 16, y: 14, isInsideCircle: true, isCatching: false },
      { id: "cover_ring", name: "Extra Cover Ring", x: 16, y: -10, isInsideCircle: true, isCatching: false },
      { id: "point_ring", name: "Backward Point", x: 20, y: 5, isInsideCircle: true, isCatching: false },
      { id: "mid_wicket_ring", name: "Short Mid-Wicket", x: -16, y: -6, isInsideCircle: true, isCatching: false },
      { id: "deep_point", name: "Deep Backward Point", x: 38, y: 12, isInsideCircle: false, isCatching: false },
      { id: "deep_cover", name: "Deep Extra Cover", x: 34, y: -22, isInsideCircle: false, isCatching: false },
      { id: "long_off", name: "Long-Off", x: 12, y: -38, isInsideCircle: false, isCatching: false },
      { id: "long_on", name: "Long-On", x: -12, y: -38, isInsideCircle: false, isCatching: false },
      { id: "deep_mid_wicket", name: "Deep Mid-Wicket", x: -36, y: -18, isInsideCircle: false, isCatching: false },
      { id: "deep_square_leg", name: "Deep Square Leg", x: -38, y: 12, isInsideCircle: false, isCatching: false }
    ]
  },
  {
    id: "short_ball_trap",
    name: "150kph Short-Ball Bouncer Trap",
    category: "Wicket-Taking",
    description: "Mayank Yadav / Shamar Joseph plan: 2 boundary riders on leg-side hook/pull + leg gully.",
    bowlingStyle: "Fast",
    strikerHand: "RHB",
    fielders: [
      { id: "wk", name: "Wicketkeeper", x: 0, y: 18, isInsideCircle: true, isCatching: false },
      { id: "leg_gully", name: "Leg Gully", x: -10, y: 15, isInsideCircle: true, isCatching: true },
      { id: "slip", name: "1st Slip", x: 6, y: 17, isInsideCircle: true, isCatching: true },
      { id: "point", name: "Backward Point", x: 20, y: 8, isInsideCircle: true, isCatching: false },
      { id: "cover", name: "Cover", x: 18, y: -10, isInsideCircle: true, isCatching: false },
      { id: "mid_off", name: "Mid-Off", x: 8, y: -20, isInsideCircle: true, isCatching: false },
      { id: "mid_on", name: "Mid-On", x: -8, y: -20, isInsideCircle: true, isCatching: false },
      { id: "deep_square_leg", name: "Deep Square Leg", x: -40, y: 10, isInsideCircle: false, isCatching: false },
      { id: "deep_mid_wicket", name: "Deep Mid-Wicket", x: -35, y: -22, isInsideCircle: false, isCatching: false },
      { id: "fine_leg", name: "Fine Leg", x: -28, y: 32, isInsideCircle: false, isCatching: false },
      { id: "third_man", name: "Third Man", x: 30, y: 30, isInsideCircle: false, isCatching: false }
    ]
  }
];

export const FieldStrategy: React.FC = () => {
  const { currentMatch, selectedBatter, selectedBowler, selectedPhase, setSelectedPhase } = useMatchContext();
  const [activePreset, setActivePreset] = useState<FieldSettingPreset>(STANDARD_PRESETS[0]);
  const [fielders, setFielders] = useState<FielderPosition[]>(STANDARD_PRESETS[0].fielders);
  const [activeFielderId, setActiveFielderId] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const [saveMessage, setSaveMessage] = useState("");
  const storageKey = `cricket.field.v1.${currentMatch.id}`;
  useEffect(() => {
    setFielders(STANDARD_PRESETS[0].fielders); setIsSaved(false); setSaveMessage("");
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
      if (Array.isArray(saved) && saved.length === STANDARD_PRESETS[0].fielders.length && new Set(saved.map(f => f.id)).size === saved.length && saved.every(f => STANDARD_PRESETS[0].fielders.some(base => base.id === f.id) && Number.isFinite(f.x) && Number.isFinite(f.y) && Math.hypot(f.x,f.y) <= 45)) {
        setFielders(saved.map(f => ({...f,isInsideCircle: Math.hypot(f.x,f.y) <= 23}))); setSaveMessage("Saved field restored from this device.");
      }
    } catch { setSaveMessage("Saved layout could not be restored."); }
  }, [storageKey]);
  const moveFielder = (id: string, x: number, y: number) => {
    const scale = Math.min(1,44 / Math.max(1,Math.hypot(x,y)));
    const nx = Math.round(x*scale*10)/10, ny = Math.round(y*scale*10)/10;
    setFielders(previous => previous.map(f => f.id === id ? {...f,x:nx,y:ny,isInsideCircle:Math.hypot(nx,ny)<=23} : f));
    setIsSaved(false); setSaveMessage("Unsaved changes.");
  };
  // Cricket Law Validation Rules
  const outsideCircleCount = fielders.filter((f) => !f.isInsideCircle).length;
  const legSideCount = fielders.filter((f) => f.x < 0).length;
  const behindSquareLeg = fielders.filter((f) => f.x < 0 && f.y > 0).length;

  const maxOutsidePermitted = selectedPhase === "Powerplay" ? 2 : 5;
  const isOutsideLegal = outsideCircleCount <= maxOutsidePermitted;
  const isBehindSquareLegLegal = behindSquareLeg <= 2;
  const isLegalityPassed = isOutsideLegal && isBehindSquareLegLegal;

  const handleApplyPreset = (preset: FieldSettingPreset) => {
    setActivePreset(preset);
    setFielders(preset.fielders); setIsSaved(false); setSaveMessage("Unsaved preset.");
    if (preset.category === "Powerplay") setSelectedPhase("Powerplay");
    else if (preset.category === "Death") setSelectedPhase("Death");
    else setSelectedPhase("Middle");
  };

  const handleFielderDrag = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!activeFielderId || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const svgWidth = rect.width;
    const svgHeight = rect.height;

    const point = svgRef.current.createSVGPoint();
    point.x = e.clientX; point.y = e.clientY;
    const matrix = svgRef.current.getScreenCTM();
    if (!matrix) return;
    const location = point.matrixTransform(matrix.inverse());
    moveFielder(activeFielderId, location.x, location.y);
  };

  const handleSaveField = () => {
    try { localStorage.setItem(storageKey, JSON.stringify(fielders)); setIsSaved(true); setSaveMessage("Field saved on this device for this match."); }
    catch { setIsSaved(false); setSaveMessage("Could not save: browser storage is unavailable."); }
  };

  return (
    <div className="space-y-6">
      <p role="status">{saveMessage || "Drag fielders with touch or mouse, or use Tab and arrow keys. Save stores this layout on this device."}</p>
      {/* 1. Header Toolbar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-stone-300">
        <div>
          <div className="flex items-center gap-2 text-xs font-sans text-stone-800 uppercase tracking-widest">
            <Shield size={14} /> Tactical Fielding Matrix // Law 28 Rules Engine
          </div>
          <h1 className="text-2xl lg:text-3xl font-semibold text-stone-800 tracking-tight flex items-center gap-3 mt-1">
            Interactive Field Strategy
            <span className="text-xs px-2.5 py-0.5 rounded border border-stone-300 bg-stone-100 text-stone-800 font-sans">
              ICC PLAYING CONDITIONS
            </span>
          </h1>
          <p className="text-xs text-stone-800 font-sans mt-0.5">
            Drag fielders on the pitch. Enforces Powerplay outside-ring limit (&le;{maxOutsidePermitted}) and behind-square leg rules (&le;2).
          </p>
        </div>

        {/* Phase Selector & Save Action */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex bg-white/[0.04] p-1 rounded-xl border border-stone-300 text-xs font-sans">
            {(["Powerplay", "Middle", "Death"] as const).map((p) => (
              <button
                key={p}
                onClick={() => setSelectedPhase(p)}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  selectedPhase === p
                    ? "bg-stone-100 text-stone-800 shadow-md shadow-cyan-500/20"
                    : "text-stone-800 text-stone-800"
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          <button
            onClick={handleSaveField}
            disabled={!isLegalityPassed}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-bold flex items-center gap-2 transition-all ${
              isLegalityPassed
                ? "bg-stone-100 text-stone-800 hover:bg-stone-100 "
                : "bg-stone-100 text-stone-800 cursor-not-allowed border border-stone-300"
            }`}
          >
            {isSaved ? <CheckCircle2 size={14} /> : <Bookmark size={14} />}
            {isSaved ? "SAVED TO DATABASE" : "SAVE FIELD PRESET"}
          </button>
        </div>
      </div>

      {/* 2. Legality Banner */}
      {!isLegalityPassed && (
        <div className="p-4 rounded-xl bg-stone-100 border border-rose-500/30 flex items-center justify-between text-xs font-sans text-stone-800">
          <div className="flex items-center gap-2.5">
            <AlertTriangle size={18} className="text-stone-800 shrink-0" />
            <div>
              <strong className="text-stone-800">ILLEGAL FIELD PLACEMENT (NO-BALL VIOLATION):</strong>{" "}
              {!isOutsideLegal && `Outside 30-yard circle has ${outsideCircleCount} fielders (Max ${maxOutsidePermitted} allowed in ${selectedPhase}). `}
              {!isBehindSquareLegLegal && `Behind square on leg-side has ${behindSquareLeg} fielders (Law 28.4 strictly limits to 2).`}
            </div>
          </div>
          <span className="px-2 py-1 rounded bg-stone-100 text-stone-800 font-bold">ILLEGAL</span>
        </div>
      )}

      {/* 3. Main Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: Interactive Field Visualizer (7 cols) */}
        <div className="lg:col-span-8 rounded-2xl border border-stone-300    p-6 shadow-none relative">
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-sans text-stone-800 flex items-center gap-2">
              <span>Striker: <strong className="text-stone-800">{selectedBatter?.name || "Shai Hope (RHB)"}</strong></span>
              <span>•</span>
              <span>Bowler: <strong className="text-stone-800">{selectedBowler?.name || "Mayank Yadav (Fast)"}</strong></span>
            </div>
            <div className="text-xs font-sans text-stone-800">
              Ring: <strong className={isOutsideLegal ? "text-stone-800" : "text-stone-800"}>{outsideCircleCount} / {maxOutsidePermitted} Outside</strong>
            </div>
          </div>

          {/* Top-Down Interactive SVG Field */}
          <div className="relative aspect-square max-w-[620px] mx-auto border border-stone-300 rounded-full overflow-hidden bg-white shadow-inner">
            <svg
              ref={svgRef}
              viewBox="-50 -50 100 100"
              className="w-full h-full cursor-crosshair select-none" style={{touchAction:"none"}} aria-label="Field layout. Tab to a fielder and use arrow keys to move it."
              onPointerMove={handleFielderDrag}
              onPointerUp={() => setActiveFielderId(null)}
              onPointerCancel={() => setActiveFielderId(null)}
            >
              {/* Outer Turf & Grass Pattern */}
              <circle cx="0" cy="0" r="48" fill="#0d241a" stroke="#1b4d37" strokeWidth="0.5" />
              <circle cx="0" cy="0" r="45" fill="#0f2b1f" stroke="#b99b37" strokeDasharray="1.5 1.5" strokeWidth="0.6" opacity="0.8" />
              
              {/* 30-Yard Circle */}
              <circle cx="0" cy="0" r="23" fill="none" stroke="#46664f" strokeWidth="0.7" strokeDasharray="2 1.5" opacity="0.7" />
              <text x="0" y="-24.5" fill="#46664f" fontSize="2.5" textAnchor="middle" fontFamily="monospace" opacity="0.7">
                30-YARD CIRCLE ({selectedPhase})
              </text>

              {/* Pitch Strip */}
              <rect x="-3" y="-12" width="6" height="24" fill="#a48c66" rx="0.5" />
              {/* Bowling Creases */}
              <line x1="-3" y1="-10" x2="3" y2="-10" stroke="#ffffff" strokeWidth="0.5" />
              <line x1="-3" y1="10" x2="3" y2="10" stroke="#ffffff" strokeWidth="0.5" />
              {/* Stumps */}
              <circle cx="0" cy="-10" r="0.6" fill="#facc15" />
              <circle cx="0" cy="10" r="0.6" fill="#facc15" />

              {/* Field Grid Axes */}
              <line x1="0" y1="-45" x2="0" y2="45" stroke="#ffffff" strokeWidth="0.2" opacity="0.15" strokeDasharray="1 1" />
              <line x1="-45" y1="0" x2="45" y2="0" stroke="#ffffff" strokeWidth="0.2" opacity="0.15" strokeDasharray="1 1" />

              {/* Boundary Labels */}
              <text x="0" y="47" fill="#64748b" fontSize="2.2" textAnchor="middle" fontFamily="monospace">STRAIGHT (70m)</text>
              <text x="0" y="-46" fill="#64748b" fontSize="2.2" textAnchor="middle" fontFamily="monospace">LONG-ON / LONG-OFF (72m)</text>
              <text x="-46" y="1" fill="#64748b" fontSize="2.2" textAnchor="start" fontFamily="monospace">MID-WICKET (58m)</text>
              <text x="46" y="1" fill="#64748b" fontSize="2.2" textAnchor="end" fontFamily="monospace">POINT (58m)</text>

              {/* Draggable Fielders */}
              {fielders.map((f) => (
                <g
                  key={f.id}
                  tabIndex={0} role="button" aria-label={`${f.id}: position ${f.x}, ${f.y}. Arrow keys move; Shift moves five units.`}
                  onKeyDown={event => {
                    const directions: Record<string,[number,number]> = {ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
                    if(directions[event.key]) { event.preventDefault(); const [dx,dy]=directions[event.key]; const step=event.shiftKey?5:1; moveFielder(f.id,f.x+dx*step,f.y+dy*step); }
                  }}
                  transform={`translate(${f.x}, ${f.y})`}
                  onPointerDown={(e) => {
                    e.stopPropagation();
                    e.currentTarget.setPointerCapture(e.pointerId);
                    setActiveFielderId(f.id);
                  }}
                  className="cursor-grab active:cursor-grabbing transition-transform hover:scale-125"
                >
                  <circle
                    r="2.6"
                    fill={f.isCatching ? "#f59e0b" : f.isInsideCircle ? "#46664f" : "#10B981"}
                    stroke="#ffffff"
                    strokeWidth="0.5"
                    className="shadow-lg filter drop-shadow"
                  />
                  <text
                    y="0.8"
                    fontSize="1.6"
                    fill="#050811"
                    fontWeight="bold"
                    textAnchor="middle"
                    fontFamily="monospace"
                  >
                    {f.id === "wk" ? "WK" : f.id.slice(0, 2).toUpperCase()}
                  </text>
                  <text
                    y="4.5"
                    fontSize="1.6"
                    fill="#ffffff"
                    textAnchor="middle"
                    fontFamily="monospace"
                    className="pointer-events-none drop-shadow"
                  >
                    {f.name}
                  </text>
                </g>
              ))}
            </svg>
          </div>

          <div className="flex items-center justify-between text-xs font-sans text-stone-800 mt-4 px-2">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white" /> Ring Fielder</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white" /> Boundary Rider</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white" /> Catching Slip/Gully</span>
            <span>Click & Drag to reposition</span>
          </div>
        </div>

        {/* Right: Presets & Matchup Recommendations (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* Tactical Field Presets */}
          <div className="rounded-2xl border border-stone-300    p-5 shadow-none space-y-3">
            <div className="text-xs font-sans text-stone-800 uppercase tracking-widest flex items-center gap-1.5 font-bold">
              <Shield size={14} /> Tactical Field Presets
            </div>
            
            <div className="space-y-2">
              {STANDARD_PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleApplyPreset(p)}
                  className={`w-full text-left p-3 rounded-xl border text-xs font-sans transition-all ${
                    activePreset.id === p.id
                      ? "bg-stone-100 border-stone-300 text-stone-800 shadow-md shadow-cyan-500/10"
                      : "bg-white/[0.02] border-stone-300 text-stone-800 hover:border-stone-300 text-stone-800"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-stone-800">{p.name}</span>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-white/5 text-stone-800">
                      {p.category}
                    </span>
                  </div>
                  <p className="text-xs text-stone-800 mt-1 leading-snug">{p.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Opposition Matchup Plan Card */}
          <div className="rounded-2xl border border-stone-300    p-5 shadow-none space-y-3">
            <div className="text-xs font-sans text-stone-800 uppercase tracking-widest flex items-center gap-1.5 font-bold">
              <Swords size={14} /> Opposition Scouting Blueprint
            </div>
            
            <div className="text-xs font-sans space-y-2.5">
              <div className="p-2.5 rounded-lg bg-white/[0.02] border border-stone-300">
                <span className="text-stone-800">Target Line & Length:</span>
                <p className="text-stone-800 font-bold mt-0.5">Off-Stump 6m Good Length (Pulls & Cutters)</p>
              </div>

              <div className="p-2.5 rounded-lg bg-white/[0.02] border border-stone-300">
                <span className="text-stone-800">Chinnaswamy Boundary Risk:</span>
                <p className="text-stone-800 font-bold mt-0.5">58m Square Fence vulnerable to pull shot</p>
              </div>

              <div className="p-2.5 rounded-lg bg-white/[0.02] border border-stone-300">
                <span className="text-stone-800">Recommended Bowler:</span>
                <p className="text-stone-800 font-bold mt-0.5">Mayank Yadav (155kph hard deck bouncer)</p>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

