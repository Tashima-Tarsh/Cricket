import React, { useState } from "react";
import { StadiumVenue } from "../types";
import { VENUES } from "../data/mockData";
import { Stadium3D } from "../components/Stadium3D";
import {
  Layers,
  Compass,
  Thermometer,
  CloudRain,
  Shield,
  Activity,
  Maximize,
  Filter,
  MapPin,
  Sparkles,
  Crosshair,
  Target,
  Flame,
  ArrowRight,
  User,
  CheckCircle2
} from "lucide-react";
import { useMatchContext } from "../context/MatchContext";

interface MatchupPreset {
  id: string;
  batterName: string;
  batterRole: string;
  bowlerName: string;
  bowlerType: string;
  speedKmh: number;
  pitchLineLength: string;
  bounceHeightM: number;
  falseShotPct: number;
  intendedShot: string;
  dismissalRisk: string;
  fieldingPreset: string;
  keyFielders: string[];
  fantasyDirective: string;
  advantage: "BOWLER_DOMINANT" | "BATTER_DOMINANT" | "COMPETITIVE";
}

const MATCHUP_PRESETS: MatchupPreset[] = [
  {
    id: "hetmyer_mayank",
    batterName: "Shimron Hetmyer",
    batterRole: "LHB • Middle Order Power Hitter",
    bowlerName: "Mayank Yadav",
    bowlerType: "Right-Arm Express Fast (150+ km/h)",
    speedKmh: 149.5,
    pitchLineLength: "7.8m Back of Length (Chest- Height on 5th Stump)",
    bounceHeightM: 1.88,
    falseShotPct: 43.8,
    intendedShot: "Front-foot pull shot over deep midwicket",
    dismissalRisk: "Steep bounce causes top edge to fine leg or deep square leg (64% probability)",
    fieldingPreset: "Throat Bouncer Trap (Law 28 Compliant)",
    keyFielders: ["Deep Backward Square (61m rope)", "Deep Mid-Wicket", "Fly Slip", "Short Extra Cover"],
    fantasyDirective: "🔥 CAPTAIN BOWLER MAYANK YADAV (0.36% C). Fade Hetmyer in this matchup because true red-soil bounce produces top-edge catches.",
    advantage: "BOWLER_DOMINANT"
  },
  {
    id: "hope_arshdeep",
    batterName: "Shai Hope",
    batterRole: "RHB • Top Order Anchor / WK",
    bowlerName: "Arshdeep Singh",
    bowlerType: "Left-Arm Fast-Medium (Inswing Specialist)",
    speedKmh: 136.2,
    pitchLineLength: "5.2m Full Inswinging Length into Right-Hander Pads",
    bounceHeightM: 1.15,
    falseShotPct: 35.3,
    intendedShot: "Front-foot on-drive or straight punch",
    dismissalRisk: "Late inward hoop beats inside edge &rarr; LBW or Bowled through the gate",
    fieldingPreset: "Inswing Strike Field",
    keyFielders: ["1st Slip (wide)", "Leg Gully / Short Mid-Wicket", "Deep Fine Leg", "Mid-On (saving single)"],
    fantasyDirective: "👑 LOCK ARSHDEEP SINGH AS VICE-CAPTAIN. Hope averages only 21.4 vs left-arm seam in the first 8 balls.",
    advantage: "BOWLER_DOMINANT"
  },
  {
    id: "tilak_motie",
    batterName: "Tilak Varma",
    batterRole: "LHB • Middle Order Anchor / Finisher",
    bowlerName: "Gudakesh Motie",
    bowlerType: "Slow Left-Arm Orthodox (88 km/h)",
    speedKmh: 87.4,
    pitchLineLength: "4.8m Good Length on Middle and Leg",
    bounceHeightM: 1.25,
    falseShotPct: 11.1,
    intendedShot: "Orthodox and reverse sweep behind square",
    dismissalRisk: "Extremely low dismissal hazard (0 dismissals in 36 balls)",
    fieldingPreset: "Defensive Ring Strangle",
    keyFielders: ["Deep Square Leg", "Deep Backward Point", "Long-On", "Short Third Man"],
    fantasyDirective: "⭐ CAPTAIN TILAK VARMA (1.23% C). Strikes at 172.2 against Motie with 0 dismissals. High ceiling at Chinnaswamy.",
    advantage: "BATTER_DOMINANT"
  },
  {
    id: "samson_joseph",
    batterName: "Sanju Samson",
    batterRole: "RHB • Power Hitter / WK",
    bowlerName: "Shamar Joseph",
    bowlerType: "Right-Arm Fast (148 km/h Steep Bounce)",
    speedKmh: 148.2,
    pitchLineLength: "7.2m Hard Length just outside Off Stump",
    bounceHeightM: 1.76,
    falseShotPct: 40.9,
    intendedShot: "Back-foot punch through covers",
    dismissalRisk: "Extra bounce induces outside edge to keeper or 1st slip",
    fieldingPreset: "Seam Extraction Trap",
    keyFielders: ["1st Slip", "Gully", "Deep Third Man", "Cover Point"],
    fantasyDirective: "💎 DIFFERENTIAL BOWLER: SHAMAR JOSEPH (0.17% C). Extra bounce creates wicket opportunities against Samson.",
    advantage: "BOWLER_DOMINANT"
  },
  {
    id: "abhishek_joseph",
    batterName: "Abhishek Sharma",
    batterRole: "LHB • Ultra-Aggressive Opener",
    bowlerName: "Shamar Joseph",
    bowlerType: "Right-Arm Fast (148 km/h)",
    speedKmh: 147.8,
    pitchLineLength: "5.8m Full Length outside Off Stump",
    bounceHeightM: 1.42,
    falseShotPct: 14.3,
    intendedShot: "Lofted punch over mid-off and extra cover",
    dismissalRisk: "Punishes full pace; strike rate 192.9",
    fieldingPreset: "Off-Side Powerplay Boundary Ring",
    keyFielders: ["Deep Cover (Boundary Rider)", "Third Man", "Mid-On", "Mid-Off inside circle"],
    fantasyDirective: "⚡ HIGH-SCORING SHOOTOUT ASSET. Abhishek dominates pace on full lengths. Captain in 220+ shootout scripts.",
    advantage: "BATTER_DOMINANT"
  }
];

export const PitchLab: React.FC = () => {
  const { currentMatch, currentPlayers, currentBattles, navigateToWorkspace } = useMatchContext();
  const [selectedVenue, setSelectedVenue] = useState<StadiumVenue>(VENUES[0]);
  const [selectedPhase, setSelectedPhase] = useState<"All" | "Powerplay" | "Middle" | "Death">("All");
  const [bowlerType, setBowlerType] = useState<"All" | "Pace" | "Spin">("All");

  const dynamicMatchups: MatchupPreset[] = React.useMemo(() => {
    if (currentBattles && currentBattles.length > 0) {
      return currentBattles.map((b: any, idx: number) => ({
        id: `battle_${b.batter_id || idx}_${b.bowler_id || idx}`,
        batterName: b.batter || b.batter_name || "Batter",
        batterRole: `${b.batter_hand || 'RHB'} • Top Order`,
        bowlerName: b.bowler || b.bowler_name || "Bowler",
        bowlerType: `${b.bowling_style || 'Fast-Medium'} (${b.speed_kmh || 135} km/h)`,
        speedKmh: b.speed_kmh || 135.0,
        pitchLineLength: b.target_length || "5.5m Good Length outside off",
        bounceHeightM: b.bounce_m || 1.35,
        falseShotPct: b.false_shot_pct || 28.5,
        intendedShot: b.intended_shot || "Drive or punch through off-side",
        dismissalRisk: b.dismissal_hazard || "Edge to keeper or slip cordon",
        fieldingPreset: "Standard Ring Protection",
        keyFielders: ["Deep Point", "Cover Ring", "1st Slip", "Mid-Off"],
        fantasyDirective: b.fantasy_note || `Tactical edge in current pitch conditions. Expected fantasy leverage pick.`,
        advantage: (b.advantage || "COMPETITIVE") as any
      }));
    }
    
    const teams = Array.from(new Set(currentPlayers.map(p => p.team).filter(Boolean)));
    if (teams.length >= 2) {
      const batSide = currentPlayers.filter(p => p.team === teams[0] && (p.role === "BAT" || p.role === "WK" || p.role === "AR"));
      const bowlSide = currentPlayers.filter(p => p.team === teams[1] && (p.role === "BOWL" || p.role === "AR"));
      const pairs: MatchupPreset[] = [];
      for (let i = 0; i < Math.min(4, Math.max(batSide.length, bowlSide.length)); i++) {
        const bat = batSide[i % batSide.length];
        const bowl = bowlSide[i % bowlSide.length];
        if (bat && bowl) {
          pairs.push({
            id: `pair_${bat.id}_${bowl.id}`,
            batterName: bat.name,
            batterRole: `${bat.batting_style || 'RHB'} • Batting Position #${bat.batting_order || (i + 1)}`,
            bowlerName: bowl.name,
            bowlerType: `${bowl.bowling_style || 'Fast-Medium'} Specialist`,
            speedKmh: (bowl.bowling_style || "").toLowerCase().includes("spin") ? 88.5 : 138.0,
            pitchLineLength: (bowl.bowling_style || "").toLowerCase().includes("spin") ? "4.5m Flighted Full Length" : "6.5m Hard Length into Ribs",
            bounceHeightM: (bowl.bowling_style || "").toLowerCase().includes("spin") ? 1.15 : 1.55,
            falseShotPct: 32.0 + (i * 3),
            intendedShot: "Attacking stroke targeting boundary rope",
            dismissalRisk: (bowl.bowling_style || "").toLowerCase().includes("spin") ? "Grip and turn inducing mistimed lofted catch" : "Steep bounce producing top edge or caught behind",
            fieldingPreset: "Tactical Dismissal Trap",
            keyFielders: ["Deep Mid-Wicket", "Long-On", "Deep Backward Square", "Cover"],
            fantasyDirective: `Key fixture duel: ${bowl.name} expected to challenge ${bat.name}. High impact on captaincy rankings.`,
            advantage: i % 2 === 0 ? "BOWLER_DOMINANT" : "BATTER_DOMINANT"
          });
        }
      }
      if (pairs.length > 0) return pairs;
    }
    return MATCHUP_PRESETS;
  }, [currentBattles, currentPlayers]);

  const [selectedDuelId, setSelectedDuelId] = useState<string>(dynamicMatchups[0]?.id || "hetmyer_mayank");

  React.useEffect(() => {
    if (dynamicMatchups.length > 0 && !dynamicMatchups.some(m => m.id === selectedDuelId)) {
      setSelectedDuelId(dynamicMatchups[0].id);
    }
  }, [dynamicMatchups, selectedDuelId]);

  const activeDuel = dynamicMatchups.find((m) => m.id === selectedDuelId) || dynamicMatchups[0] || MATCHUP_PRESETS[0];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header & Stadium Selector Strip */}
      <div className="rounded-2xl border border-stone-300     p-6 shadow-none ">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-sans text-stone-800 uppercase tracking-widest">
              <Layers size={14} className="" /> 3D Spatial Hawkeye Engine
            </div>
            <h1 className="text-2xl sm:text-3xl font-semibold text-stone-800 tracking-tight flex items-center gap-3">
              Pitch & venue assumptions
              <span className="text-xs px-3 py-1 rounded-full border border-stone-300 bg-stone-100 text-stone-800 font-sans font-bold">
                OPTIONAL 3D
              </span>
            </h1>
            <p className="text-xs text-stone-800 font-sans max-w-2xl">
              Hawkeye ball trajectory delivery clusters, sub-surface soil moisture degradation, altitude air-density drag, and boundary radar geometry.
            </p>
          </div>

          {/* Stadium Switcher Glass Pills */}
          <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-white/[0.03] border border-stone-300 ">
            {VENUES.map((v) => (
              <button
                key={v.id}
                onClick={() => setSelectedVenue(v)}
                className={`px-4 py-2 rounded-xl text-xs font-sans transition-all flex items-center gap-2 ${
                  selectedVenue.id === v.id
                    ? "   border border-stone-300 text-stone-800 font-bold "
                    : "text-stone-800 text-stone-800 hover:bg-white/[0.05]"
                }`}
              >
                <MapPin size={12} className={selectedVenue.id === v.id ? "text-stone-800" : "text-stone-800"} />
                <span>{v.city}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main 3D Canvas + Analytical Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Fullscreen 3D Pitch View (8 cols) */}
        <div className="lg:col-span-8 flex flex-col rounded-2xl border border-stone-300 bg-white shadow-none overflow-hidden min-h-[540px]">
          {/* Phase Filter Controls */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3 border-b border-stone-300 bg-stone-100 ">
            <div className="flex items-center gap-2">
              <Filter size={14} className="text-stone-800" />
              <span className="text-xs font-sans text-stone-800">Phase:</span>
              <div className="flex items-center gap-1">
                {(["All", "Powerplay", "Middle", "Death"] as const).map((ph) => (
                  <button
                    key={ph}
                    onClick={() => setSelectedPhase(ph)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-sans transition-all ${
                      selectedPhase === ph
                        ? "bg-stone-100 text-stone-800 font-bold shadow-sm"
                        : "text-stone-800 text-stone-800 bg-white/[0.03]"
                    }`}
                  >
                    {ph}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-sans text-stone-800">Bowler:</span>
              <div className="flex items-center gap-1">
                {(["All", "Pace", "Spin"] as const).map((bt) => (
                  <button
                    key={bt}
                    onClick={() => setBowlerType(bt)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-sans transition-all ${
                      bowlerType === bt
                        ? "bg-stone-100 text-stone-800 font-bold shadow-sm"
                        : "text-stone-800 text-stone-800 bg-white/[0.03]"
                    }`}
                  >
                    {bt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex-1 w-full min-h-[480px] relative   ">
            <Stadium3D
              initialCamera="pitch_heatmap"
              filterPhase={selectedPhase}
              filterBowlerType={bowlerType}
              className="w-full h-full"
            />
          </div>
        </div>

        {/* Right Tactical Sidebar (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          {/* Soil & Pitch Nature */}
          <div className="rounded-2xl border border-stone-300    p-6 shadow-none space-y-4">
            <div className="text-xs font-sans text-stone-800 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles size={12} /> VENUE SURFACE SPECIFICATIONS
            </div>
            <h3 className="font-heading font-semibold text-stone-800 text-xl">
              {selectedVenue.name}
            </h3>
            <p className="text-xs text-stone-800 leading-relaxed font-sans">
              {selectedVenue.pitch_nature}
            </p>

            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-stone-300 text-xs font-sans">
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-xs text-stone-800">Soil Structure</div>
                <div className="text-stone-800 font-bold mt-1 text-xs truncate" title={selectedVenue.soil_type}>
                  {selectedVenue.soil_type}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-xs text-stone-800">1st Innings Par</div>
                <div className="text-stone-800 font-semibold mt-1 text-base telemetry-num">{selectedVenue.avg_first_innings} <span className="text-xs text-stone-800 font-normal">runs</span></div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-xs text-stone-800">Pace / Spin Split</div>
                <div className="text-stone-800 font-bold mt-1">{selectedVenue.pace_wicket_pct}% / {selectedVenue.spin_wicket_pct}%</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-xs text-stone-800">Chasing Win Bias</div>
                <div className="text-stone-800 font-bold mt-1">{selectedVenue.chasing_win_pct}%</div>
              </div>
            </div>
          </div>

          {/* Stadium Boundary Radar Dimensions */}
          <div className="rounded-2xl border border-stone-300    p-6 shadow-none space-y-4">
            <div className="text-xs font-sans text-stone-800 font-bold uppercase tracking-wider flex items-center justify-between">
              <span>BOUNDARY RADAR METRICS</span>
              <span className="text-stone-800 font-normal">DIMENSIONS</span>
            </div>

            <div className="space-y-2 text-xs font-sans">
              {Object.entries(selectedVenue.boundaries).map(([sector, dist]) => (
                <div key={sector} className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]">
                  <span className="text-stone-800 capitalize">{sector.replace("_", " ")}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-2 bg-stone-100 rounded-full overflow-hidden">
                      <div
                        className="h-full    rounded-full"
                        style={{ width: `${(dist / 85) * 100}%` }}
                      />
                    </div>
                    <span className="text-stone-800 font-bold w-10 text-right">{dist}m</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 3. INTERACTIVE 3D SPATIAL DUEL & TACTICAL FIELD TRAP LAB */}
      <div className="rounded-2xl border border-stone-300     p-6 shadow-none space-y-5 ">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-stone-300">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-stone-100 border border-stone-300 text-stone-800">
              <Crosshair size={22} />
            </div>
            <div>
              <div className="text-xs font-sans text-stone-800 font-bold uppercase tracking-wider">
                3D SPATIAL DELIVERY & TACTICAL FIELD TRAP
              </div>
              <h2 className="text-xl font-heading font-semibold text-stone-800 flex items-center gap-2">
                H2H DUEL SIMULATOR: BATTER X vs BOWLER Y
                <span className="text-xs font-sans px-2 py-0.5 rounded-full bg-stone-100 text-stone-800 border border-stone-300">
                  LAW 28 ENGINE
                </span>
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-sans text-stone-800">SELECT MATCHUP:</span>
            <select aria-label="Duel id"
              value={selectedDuelId}
              onChange={(e) => setSelectedDuelId(e.target.value)}
              className="bg-stone-100 border border-stone-300 rounded-xl px-3 py-1.5 text-xs font-sans text-stone-800 font-bold focus:outline-none focus:border-stone-300"
            >
              {dynamicMatchups.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.batterName} vs {m.bowlerName} ({m.speedKmh} km/h)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Duel Grid: 3 Analytical Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Card 1: Bowler Trajectory & Pitch Telemetry */}
          <div className="p-4 rounded-xl bg-stone-100 border border-stone-300 space-y-3">
            <div className="text-xs font-sans text-stone-800 uppercase font-bold tracking-wider flex items-center justify-between">
              <span>BOWLER DELIVERY PROFILE</span>
              <span className="text-stone-800 font-sans font-bold">{activeDuel.speedKmh} km/h</span>
            </div>
            <div className="text-base font-bold text-stone-800 font-sans">
              {activeDuel.bowlerName}
            </div>
            <div className="text-xs text-stone-800 font-sans">
              {activeDuel.bowlerType}
            </div>

            <div className="space-y-2 pt-2 border-t border-stone-300 text-xs font-sans">
              <div className="p-2.5 rounded-lg bg-white/[0.03] space-y-1">
                <span className="text-xs text-stone-800 uppercase">Pitch Landing & Length:</span>
                <div className="text-stone-800 font-bold text-xs">{activeDuel.pitchLineLength}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-white/[0.03] flex justify-between items-center">
                <span className="text-xs text-stone-800 uppercase">Chinnaswamy Bounce:</span>
                <span className="text-stone-800 font-bold">{activeDuel.bounceHeightM}m (Shoulder/Throat)</span>
              </div>
            </div>
          </div>

          {/* Card 2: Batter Response & Dismissal Hazard */}
          <div className="p-4 rounded-xl bg-stone-100 border border-stone-300 space-y-3">
            <div className="text-xs font-sans text-stone-800 uppercase font-bold tracking-wider flex items-center justify-between">
              <span>BATTER SHOT & VULNERABILITY</span>
              <span className="text-stone-800 font-sans font-bold">{activeDuel.falseShotPct}% False Shot</span>
            </div>
            <div className="text-base font-bold text-stone-800 font-sans">
              {activeDuel.batterName}
            </div>
            <div className="text-xs text-stone-800 font-sans">
              {activeDuel.batterRole}
            </div>

            <div className="space-y-2 pt-2 border-t border-stone-300 text-xs font-sans">
              <div className="p-2.5 rounded-lg bg-white/[0.03] space-y-1">
                <span className="text-xs text-stone-800 uppercase">Intended Stroke:</span>
                <div className="text-stone-800 font-bold text-xs">{activeDuel.intendedShot}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-stone-100 border border-rose-500/20 space-y-1">
                <span className="text-xs text-stone-800 uppercase font-bold">Dismissal Hazard Mode:</span>
                <div className="text-stone-800 text-xs font-sans leading-snug">{activeDuel.dismissalRisk}</div>
              </div>
            </div>
          </div>

          {/* Card 3: Law 28 Fielding Trap & Key Catchers */}
          <div className="p-4 rounded-xl bg-stone-100 border border-stone-300 space-y-3">
            <div className="text-xs font-sans text-stone-800 uppercase font-bold tracking-wider flex items-center justify-between">
              <span>FIELDING TRAP SETUP</span>
              <span className="text-stone-800 font-sans font-bold">LAW 28 LEGAL</span>
            </div>
            <div className="text-base font-bold text-stone-800 font-sans truncate">
              {activeDuel.fieldingPreset}
            </div>
            <div className="text-xs text-stone-800 font-sans">
              Tailored catchers set for the miscue / edge
            </div>

            <div className="space-y-1.5 pt-2 border-t border-stone-300 text-xs font-sans">
              <span className="text-xs text-stone-800 uppercase">Key Catchers Placed:</span>
              <div className="grid grid-cols-2 gap-1.5">
                {activeDuel.keyFielders.map((pos, idx) => (
                  <div key={idx} className="p-1.5 rounded bg-white/[0.03] border border-stone-300 text-xs text-stone-800 truncate" title={pos}>
                    📍 {pos}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Optimal Fantasy Recommendation Banner & Quick Actions */}
        <div className="p-4 rounded-xl     border border-stone-300 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-stone-100 text-stone-800 shrink-0">
              <Flame size={18} />
            </div>
            <div className="space-y-0.5">
              <div className="text-xs font-sans text-stone-800 font-bold uppercase">
                OPTIMAL FANTASY TACTICAL DIRECTIVE
              </div>
              <div className="text-xs text-stone-800 font-sans font-bold leading-relaxed">
                {activeDuel.fantasyDirective}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => navigateToWorkspace("fantasy-lab")}
              className="px-4 py-2 rounded-xl bg-stone-100 hover:bg-stone-100 border border-stone-300 text-stone-800 text-xs font-sans font-bold flex items-center gap-1.5 transition-all"
            >
              <span>APPLY TO FANTASY LAB</span>
              <ArrowRight size={14} />
            </button>
            <button
              onClick={() => navigateToWorkspace("field-strategy")}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-stone-300 text-stone-800 text-xs font-sans font-bold flex items-center gap-1.5 transition-all"
            >
              <span>OPEN FIELD CANVAS</span>
            </button>
          </div>
        </div>

        {/* Provenance Footnote */}
        <div className="flex flex-wrap items-center justify-between text-[10px] font-mono text-stone-500 px-3 py-1 bg-stone-100/60 rounded border border-stone-200">
          <span>PROVENANCE: Kinematic Spatial Model (Simulated from Cricinfo release telemetry & Law 28 geometry)</span>
          <span>Pitch Restitution Coefficient: e = 0.58 (Chinnaswamy Red Clay Sand-Base)</span>
        </div>
      </div>
    </div>
  );
};
