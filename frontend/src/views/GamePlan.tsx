import React, { useState } from "react";
import { 
  ClipboardList, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Target, 
  Flame, 
  Layers, 
  UserCheck, 
  Clock, 
  Zap,
  ArrowRight
} from "lucide-react";
import { useMatchContext } from "../context/MatchContext";
import { OverPlan, Player, TacticalObjective } from "../types";

const INITIAL_IND_GAMEPLAN: OverPlan[] = [
  // Powerplay (Overs 1-6)
  {
    overNumber: 1,
    phase: "Powerplay",
    assignedBowlerId: "ind_arshdeep",
    assignedBowlerName: "Arshdeep Singh",
    expectedBatters: ["S Hope", "A Jangoo"],
    objective: "Wicket Strike",
    targetLineLength: "Full swing into right-hander pads / 5th stump angle",
    fieldPresetId: "ind_pace_inward",
    matchupRationale: "Hope averages 21.4 vs left-arm inswing in first 6 balls. Target front pad lbw.",
    riskRating: "Low",
    confidencePct: 88
  },
  {
    overNumber: 2,
    phase: "Powerplay",
    assignedBowlerId: "ind_bhuvneshwar",
    assignedBowlerName: "Bhuvneshwar Kumar",
    expectedBatters: ["A Jangoo", "S Hope"],
    objective: "Run Containment",
    targetLineLength: "Upright seam, good length just outside off",
    fieldPresetId: "ind_pace_inward",
    matchupRationale: "Jangoo false shot rate 38% against 130kph outswing on good length.",
    riskRating: "Low",
    confidencePct: 82
  },
  {
    overNumber: 3,
    phase: "Powerplay",
    assignedBowlerId: "ind_mayank",
    assignedBowlerName: "Mayank Yadav",
    expectedBatters: ["S Hope", "S Hetmyer"],
    objective: "Wicket Strike",
    targetLineLength: "Hard length 148km/h directed at throat/armpit",
    fieldPresetId: "ind_pace_inward",
    matchupRationale: "Sheer pace rush; true bounce produces top edges to fine leg.",
    riskRating: "Moderate",
    confidencePct: 85
  },
  {
    overNumber: 4,
    phase: "Powerplay",
    assignedBowlerId: "ind_arshdeep",
    assignedBowlerName: "Arshdeep Singh",
    expectedBatters: ["S Hetmyer", "S Hope"],
    objective: "Matchup Strangle",
    targetLineLength: "Wide full length slanting across Hetmyer",
    fieldPresetId: "ind_pace_inward",
    matchupRationale: "Deny Hetmyer leg-side arc. Force lofted drive towards deep backward point.",
    riskRating: "Moderate",
    confidencePct: 79
  },
  {
    overNumber: 5,
    phase: "Powerplay",
    assignedBowlerId: "ind_mayank",
    assignedBowlerName: "Mayank Yadav",
    expectedBatters: ["S Hetmyer", "R Powell"],
    objective: "Wicket Strike",
    targetLineLength: "Back of length seam attack into ribs",
    fieldPresetId: "ind_pace_inward",
    matchupRationale: "Powell strike rate drops to 94 vs 145km/h+ deliveries in powerplay.",
    riskRating: "Moderate",
    confidencePct: 84
  },
  {
    overNumber: 6,
    phase: "Powerplay",
    assignedBowlerId: "ind_axar",
    assignedBowlerName: "Axar Patel",
    expectedBatters: ["R Powell", "S Rutherford"],
    objective: "Run Containment",
    targetLineLength: "Flat dart 96km/h sliding on with arm onto stumps",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "End of powerplay squeeze. Powell struggles to generate elevation off back foot.",
    riskRating: "Low",
    confidencePct: 80
  },
  // Middle Overs (Overs 7-15)
  {
    overNumber: 7,
    phase: "Middle",
    assignedBowlerId: "ind_varun",
    assignedBowlerName: "Varun Chakaravarthy",
    expectedBatters: ["S Rutherford", "R Powell"],
    objective: "Wicket Strike",
    targetLineLength: "Mystery carrom ball and googly on middle-stump line",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Rutherford dot-ball % against mystery wrist-spin is 44%. High dismissal equity.",
    riskRating: "Low",
    confidencePct: 91
  },
  {
    overNumber: 8,
    phase: "Middle",
    assignedBowlerId: "ind_axar",
    assignedBowlerName: "Axar Patel",
    expectedBatters: ["R Powell", "R Chase"],
    objective: "Run Containment",
    targetLineLength: "Tight stump- line, denying width",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Economy is 6.8 rpo in middle overs.",
    riskRating: "Low",
    confidencePct: 86
  },
  {
    overNumber: 9,
    phase: "Middle",
    assignedBowlerId: "ind_varun",
    assignedBowlerName: "Varun Chakaravarthy",
    expectedBatters: ["R Chase", "R Shepherd"],
    objective: "Wicket Strike",
    targetLineLength: "Leg-cutter dipping outside off into driving arc",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Induce rash lofted strokes towards long-off.",
    riskRating: "Moderate",
    confidencePct: 87
  },
  {
    overNumber: 10,
    phase: "Middle",
    assignedBowlerId: "ind_axar",
    assignedBowlerName: "Axar Patel",
    expectedBatters: ["R Shepherd", "K Paul"],
    objective: "Run Containment",
    targetLineLength: "Full and fast flat trajectories",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Keep boundary count under 1 per over during transition.",
    riskRating: "Low",
    confidencePct: 83
  },
  {
    overNumber: 11,
    phase: "Middle",
    assignedBowlerId: "ind_varun",
    assignedBowlerName: "Varun Chakaravarthy",
    expectedBatters: ["R Shepherd", "K Paul"],
    objective: "Wicket Strike",
    targetLineLength: "Googly turning sharply past Shepherd's forward defence",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Bowled or LBW probability highest when Shepherd attempts across-the-line swipe.",
    riskRating: "Moderate",
    confidencePct: 89
  },
  {
    overNumber: 12,
    phase: "Middle",
    assignedBowlerId: "ind_bhuvneshwar",
    assignedBowlerName: "Bhuvneshwar Kumar",
    expectedBatters: ["K Paul", "S Springer"],
    objective: "Run Containment",
    targetLineLength: "Knuckle ball and back-of-hand slower cutters",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Disrupt timing before death overs commence.",
    riskRating: "Low",
    confidencePct: 81
  },
  {
    overNumber: 13,
    phase: "Middle",
    assignedBowlerId: "ind_axar",
    assignedBowlerName: "Axar Patel",
    expectedBatters: ["S Springer", "K Paul"],
    objective: "Run Containment",
    targetLineLength: "Defensive trajectory wide of off stump",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Exhaust Axar's 4th over before death surge begins.",
    riskRating: "Low",
    confidencePct: 80
  },
  {
    overNumber: 14,
    phase: "Middle",
    assignedBowlerId: "ind_varun",
    assignedBowlerName: "Varun Chakaravarthy",
    expectedBatters: ["K Paul", "G Motie"],
    objective: "Wicket Strike",
    targetLineLength: "Top-spin gripper turning into lower order pads",
    fieldPresetId: "wi_spin_choke",
    matchupRationale: "Exhaust Varun's 4th over aiming to clean up middle order.",
    riskRating: "Moderate",
    confidencePct: 88
  },
  {
    overNumber: 15,
    phase: "Middle",
    assignedBowlerId: "ind_bhuvneshwar",
    assignedBowlerName: "Bhuvneshwar Kumar",
    expectedBatters: ["S Springer", "G Motie"],
    objective: "Run Containment",
    targetLineLength: "Full wide yorkers testing deep cover boundaries",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Preparation for death phase. Low boundary conceded rate.",
    riskRating: "Moderate",
    confidencePct: 83
  },
  // Death Overs (Overs 16-20)
  {
    overNumber: 16,
    phase: "Death",
    assignedBowlerId: "ind_mayank",
    assignedBowlerName: "Mayank Yadav",
    expectedBatters: ["R Shepherd", "S Springer"],
    objective: "Wicket Strike",
    targetLineLength: "150km/h searing yorker at the base of off stump",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Express pace destroys late order clearing ability.",
    riskRating: "Moderate",
    confidencePct: 90
  },
  {
    overNumber: 17,
    phase: "Death",
    assignedBowlerId: "ind_arshdeep",
    assignedBowlerName: "Arshdeep Singh",
    expectedBatters: ["R Shepherd", "S Joseph"],
    objective: "Death Yorker Lock",
    targetLineLength: "Pinpoint wide yorkers skimming the tramline",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Arshdeep death economy 7.2 rpo in matches 1-4. Prevents leg-side heave.",
    riskRating: "Low",
    confidencePct: 92
  },
  {
    overNumber: 18,
    phase: "Death",
    assignedBowlerId: "ind_mayank",
    assignedBowlerName: "Mayank Yadav",
    expectedBatters: ["S Joseph", "G Motie"],
    objective: "Wicket Strike",
    targetLineLength: "Throat bouncer followed by 149kph toe-crusher",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Finish tail-end resistance rapidly.",
    riskRating: "Moderate",
    confidencePct: 86
  },
  {
    overNumber: 19,
    phase: "Death",
    assignedBowlerId: "ind_bhuvneshwar",
    assignedBowlerName: "Bhuvneshwar Kumar",
    expectedBatters: ["A Hosein", "G Motie"],
    objective: "Death Yorker Lock",
    targetLineLength: "Deceptive knuckle yorkers dipping at batter ankles",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Bhuvneshwar 4th and final over. Masterclass death execution.",
    riskRating: "Low",
    confidencePct: 88
  },
  {
    overNumber: 20,
    phase: "Death",
    assignedBowlerId: "ind_arshdeep",
    assignedBowlerName: "Arshdeep Singh",
    expectedBatters: ["G Motie", "A Hosein"],
    objective: "Death Yorker Lock",
    targetLineLength: "Clutch reverse-swing yorkers right into the base of middle stump",
    fieldPresetId: "wi_death_lock",
    matchupRationale: "Arshdeep 4th and final over to seal innings containment under 150.",
    riskRating: "Low",
    confidencePct: 94
  }
];

function generateMatchGamePlan(players: Player[], bowlingTeam: string, battingTeam: string): OverPlan[] {
  const bowlers = players.filter(p => p.team === bowlingTeam && (p.role === "BOWL" || p.role === "AR"));
  const batters = players.filter(p => p.team === battingTeam).sort((a, b) => (a.batting_order || 5) - (b.batting_order || 5));
  
  if (bowlers.length === 0) {
    return INITIAL_IND_GAMEPLAN;
  }

  const pacers = bowlers.filter(b => (b.bowling_style || "").toLowerCase().includes("fast") || (b.bowling_style || "").toLowerCase().includes("pace") || (b.bowling_style || "").toLowerCase().includes("medium"));
  const spinners = bowlers.filter(b => (b.bowling_style || "").toLowerCase().includes("spin") || (b.bowling_style || "").toLowerCase().includes("break") || (b.bowling_style || "").toLowerCase().includes("orthodox") || (b.bowling_style || "").toLowerCase().includes("slow"));
  const sortedBowlers = [...pacers, ...spinners, ...bowlers];
  const uniqueBowlers = Array.from(new Set(sortedBowlers));

  const plan: OverPlan[] = [];
  const counts: Record<string, number> = {};
  let lastBowlerId: string | null = null;

  for (let over = 1; over <= 20; over++) {
    const phase: "Powerplay" | "Middle" | "Death" = over <= 6 ? "Powerplay" : over <= 15 ? "Middle" : "Death";
    
    let pool = uniqueBowlers;
    if (phase === "Powerplay" && pacers.length >= 2) {
      pool = pacers;
    } else if (phase === "Middle" && spinners.length >= 2) {
      pool = [...spinners, ...bowlers];
    } else if (phase === "Death" && pacers.length >= 2) {
      pool = pacers;
    }

    let eligible = pool.filter(b => b.id !== lastBowlerId && (counts[b.id] || 0) < 4);
    if (eligible.length === 0) {
      eligible = uniqueBowlers.filter(b => b.id !== lastBowlerId && (counts[b.id] || 0) < 4);
    }
    if (eligible.length === 0) {
      eligible = uniqueBowlers.filter(b => (counts[b.id] || 0) < 4);
    }
    const chosen = eligible[0] || uniqueBowlers[over % uniqueBowlers.length];
    counts[chosen.id] = (counts[chosen.id] || 0) + 1;
    lastBowlerId = chosen.id;

    const expBatters = phase === "Powerplay" 
      ? batters.slice(0, 2).map(b => b.name)
      : phase === "Middle"
      ? batters.slice(1, 5).map(b => b.name)
      : batters.slice(4, 8).map(b => b.name);

    const tacticalObjective: TacticalObjective = phase === "Powerplay" 
      ? "Wicket Strike" 
      : phase === "Death" 
      ? "Death Yorker Lock" 
      : "Run Containment";

    plan.push({
      overNumber: over,
      phase,
      assignedBowlerId: chosen.id,
      assignedBowlerName: chosen.name,
      expectedBatters: expBatters.length > 0 ? expBatters : ["Top Order Batter"],
      objective: tacticalObjective,
      targetLineLength: phase === "Death" ? "Full wide yorkers & hard length bouncers" : phase === "Powerplay" ? "Good length top of off-stump with swing" : "Stump-to-stump tight line with flight variations",
      fieldPresetId: phase === "Powerplay" ? "powerplay_ring" : phase === "Death" ? "death_lock" : "middle_squeeze",
      matchupRationale: `${chosen.name} (${chosen.bowling_style || 'Bowler'}) targeting opposition ${phase.toLowerCase()} phase. Opponent dismissal probability high.`,
      riskRating: phase === "Death" ? "Moderate" : "Low",
      confidencePct: 80 + (over % 15)
    });
  }
  return plan;
}

export const GamePlan: React.FC = () => {
  const { currentPlayers, currentMatch, navigateToWorkspace } = useMatchContext();
  const teams = Array.from(new Set(currentPlayers.map(p => p.team).filter(Boolean)));
  const defaultBowlingTeam = teams[0] || currentMatch?.teams?.home?.code || currentMatch?.teams?.home?.name || "IND";
  const [bowlingTeam, setBowlingTeam] = useState<string>(defaultBowlingTeam);
  const [gamePlan, setGamePlan] = useState<OverPlan[]>(INITIAL_IND_GAMEPLAN);
  const [selectedOver, setSelectedOver] = useState<number>(1);

  React.useEffect(() => {
    if (teams.length > 0 && !teams.includes(bowlingTeam)) {
      setBowlingTeam(teams[0]);
    }
  }, [teams, bowlingTeam]);

  React.useEffect(() => {
    const oppTeam = teams.find(t => t !== bowlingTeam) || teams[1] || "OPP";
    const dynamicPlan = generateMatchGamePlan(currentPlayers, bowlingTeam, oppTeam);
    setGamePlan(dynamicPlan);
  }, [bowlingTeam, currentPlayers, currentMatch?.id]);

  // Available bowlers for selected bowling team
  const availableBowlers = currentPlayers.filter(
    (p) => (p.role === "BOWL" || p.role === "AR") && (p.team === bowlingTeam)
  );

  // Calculate bowler quotas
  const bowlerOversCount: Record<string, number> = {};
  gamePlan.forEach((plan) => {
    bowlerOversCount[plan.assignedBowlerName] = (bowlerOversCount[plan.assignedBowlerName] || 0) + 1;
  });

  // Check validity: No bowler > 4 overs, and no bowler bowling consecutive overs
  const quotaViolations: string[] = [];
  Object.entries(bowlerOversCount).forEach(([name, count]) => {
    if (count > 4) {
      quotaViolations.push(`${name} has been assigned ${count} overs (Max allowed: 4)`);
    }
  });

  const consecutiveViolations: string[] = [];
  for (let i = 0; i < gamePlan.length - 1; i++) {
    if (gamePlan[i].assignedBowlerName === gamePlan[i + 1].assignedBowlerName) {
      consecutiveViolations.push(
        `${gamePlan[i].assignedBowlerName} is scheduled for consecutive Overs ${i + 1} and ${i + 2}`
      );
    }
  }

  const currentOverData = gamePlan.find((p) => p.overNumber === selectedOver) || gamePlan[0];

  const handleBowlerChange = (overNum: number, bowlerId: string, bowlerName: string) => {
    setGamePlan((prev) =>
      prev.map((plan) =>
        plan.overNumber === overNum
          ? { ...plan, assignedBowlerId: bowlerId, assignedBowlerName: bowlerName }
          : plan
      )
    );
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-white border border-stone-300 shadow-none ">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl    border border-stone-300 text-stone-800">
            <ClipboardList size={24} />
          </div>
          <div>
            <h1 className="text-xl font-heading font-semibold tracking-wider text-stone-800 flex items-center gap-2">
              OVER-BY-OVER TACTICAL GAME PLAN
              <span className="text-xs font-sans px-2 py-0.5 rounded-full bg-stone-100 border border-stone-300 text-stone-800">
                20-OVER BLUEPRINT
              </span>
            </h1>
            <p className="text-xs font-sans text-stone-800">
              Bowler Quota Management • Matchup Targeting • Line/Length Directives
            </p>
          </div>
        </div>

        {/* Team Selector & Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-stone-100 p-1.5 rounded-xl border border-stone-300">
            <span className="text-xs font-sans text-stone-800 uppercase px-2">Bowling Side:</span>
            {teams.length > 0 ? (
              teams.map((t) => (
                <button
                  key={t}
                  onClick={() => setBowlingTeam(t)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-sans font-bold transition-all ${
                    bowlingTeam === t
                      ? "bg-white text-stone-900 border border-stone-300 shadow-sm"
                      : "text-stone-600 hover:text-stone-900"
                  }`}
                >
                  {t} BOWLING
                </button>
              ))
            ) : (
              <>
                <button
                  onClick={() => setBowlingTeam("IND")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-sans font-bold transition-all ${
                    bowlingTeam === "IND" ? "bg-white text-stone-900" : "text-stone-600"
                  }`}
                >
                  INDIA BOWLING
                </button>
                <button
                  onClick={() => setBowlingTeam("WI")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-sans font-bold transition-all ${
                    bowlingTeam === "WI" ? "bg-white text-stone-900" : "text-stone-600"
                  }`}
                >
                  WI BOWLING
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Quota & Validation Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Bowler Quota Card */}
        <div className="md:col-span-2 p-4 rounded-xl bg-stone-100 border border-stone-300 flex flex-wrap items-center gap-3">
          <span className="text-xs font-sans text-stone-800 uppercase flex items-center gap-1.5">
            <UserCheck size={14} className="text-stone-800" />
            Quota Tracker:
          </span>
          {Object.entries(bowlerOversCount).map(([name, count]) => (
            <div
              key={name}
              className={`px-2.5 py-1 rounded-lg text-xs font-sans flex items-center gap-2 border ${
                count === 4
                  ? "bg-stone-100 border-stone-300 text-stone-800 font-bold"
                  : count > 4
                  ? "bg-stone-100 border-rose-500 text-stone-800 font-bold"
                  : "bg-stone-100 border-stone-300 text-stone-800"
              }`}
            >
              <span>{name.split(" ")[0]}</span>
              <span className="px-1.5 py-0.2 rounded bg-black/40 text-xs">
                {count}/4 Ov
              </span>
            </div>
          ))}
        </div>

        {/* Validation Status */}
        <div className="p-4 rounded-xl bg-stone-100 border border-stone-300 flex items-center justify-between">
          <span className="text-xs font-sans text-stone-800 uppercase">ICC Rule Check:</span>
          {quotaViolations.length === 0 && consecutiveViolations.length === 0 ? (
            <div className="flex items-center gap-1.5 text-xs font-sans text-stone-800 font-bold">
              <CheckCircle2 size={16} />
              <span>LEGAL PLAN CONFIRMED</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-xs font-sans text-stone-800 font-bold">
              <AlertTriangle size={16} />
              <span>VIOLATION DETECTED</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Over-by-Over Matrix + Over Detail Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: 20-Over Interactive Timeline (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-4 rounded-2xl bg-stone-100 border border-stone-300 space-y-4 ">
            <div className="flex items-center justify-between border-b border-stone-300 pb-3">
              <div className="text-sm font-heading font-bold text-stone-800 flex items-center gap-2">
                <Clock size={16} className="text-stone-800" />
                <span>20-Over Bowling Progression</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-sans">
                <span className="px-2 py-0.5 rounded bg-stone-100 text-stone-800 border border-stone-300">PP: 1-6</span>
                <span className="px-2 py-0.5 rounded bg-stone-100 text-stone-800 border border-blue-500/20">MID: 7-15</span>
                <span className="px-2 py-0.5 rounded bg-stone-100 text-stone-800 border border-rose-500/20">DEATH: 16-20</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-[640px] overflow-y-auto pr-1">
              {gamePlan.map((plan) => {
                const isSelected = plan.overNumber === selectedOver;
                const phaseColor =
                  plan.phase === "Powerplay"
                    ? "border-l-cyan-400"
                    : plan.phase === "Middle"
                    ? "border-l-blue-400"
                    : "border-l-rose-400";

                return (
                  <div
                    key={plan.overNumber}
                    onClick={() => setSelectedOver(plan.overNumber)}
                    className={`p-3 rounded-xl border border-l-4 transition-all cursor-pointer ${phaseColor} ${
                      isSelected
                        ? "bg-stone-100 border-stone-300 "
                        : "bg-stone-100 border-stone-300 hover:bg-white/5"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-sans mb-1">
                      <span className="font-semibold text-stone-800">OVER {plan.overNumber}</span>
                      <span className={`text-xs px-1.5 py-0.2 rounded font-bold ${
                        plan.objective === "Wicket Strike"
                          ? "bg-stone-100 text-stone-800"
                          : plan.objective === "Death Yorker Lock"
                          ? "bg-stone-100 text-stone-800"
                          : "bg-stone-100 text-stone-800"
                      }`}>
                        {plan.objective}
                      </span>
                    </div>

                    <div className="text-xs font-bold text-stone-800 truncate">
                      {plan.assignedBowlerName}
                    </div>

                    <div className="text-xs text-stone-800 truncate mt-1">
                      Target: {plan.targetLineLength}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Selected Over Tactical Breakdown (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-5 rounded-2xl bg-stone-100 border border-stone-300 space-y-5  sticky top-20">
            <div className="flex items-center justify-between border-b border-stone-300 pb-3">
              <div className="flex items-center gap-2">
                <Target size={18} className="text-stone-800" />
                <span className="font-heading font-semibold text-stone-800 text-base">
                  OVER {currentOverData.overNumber} TACTICAL DOSSIER
                </span>
              </div>
              <span className="text-xs font-sans text-stone-800 bg-stone-100 px-2 py-0.5 rounded border border-stone-300">
                {currentOverData.phase} Phase
              </span>
            </div>

            {/* Bowler Reassignment Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-sans text-stone-800">ASSIGNED BOWLER:</label>
              <select
                value={currentOverData.assignedBowlerName}
                onChange={(e) => {
                  const bName = e.target.value;
                  const bObj = availableBowlers.find((p) => p.name === bName);
                  handleBowlerChange(currentOverData.overNumber, bObj ? bObj.id : "", bName);
                }}
                className="w-full bg-stone-100 border border-stone-300 rounded-xl px-3 py-2 text-xs font-sans text-stone-800 focus:outline-none focus:border-stone-300"
              >
                {availableBowlers.length > 0 ? (
                  availableBowlers.map((b) => (
                    <option key={b.id} value={b.name}>
                      {b.name} ({b.bowling_style || b.role}) - {bowlerOversCount[b.name] || 0}/4 Ov
                    </option>
                  ))
                ) : (
                  <option value={currentOverData.assignedBowlerName}>
                    {currentOverData.assignedBowlerName}
                  </option>
                )}
              </select>
            </div>

            {/* Expected Matchup Batters */}
            <div className="p-3.5 rounded-xl bg-stone-100 border border-stone-300 space-y-2">
              <div className="text-xs font-sans text-stone-800 uppercase">ANTICIPATED STRIKERS:</div>
              <div className="flex items-center gap-2">
                {currentOverData.expectedBatters.map((bat, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-lg bg-white/5 border border-stone-300 text-xs font-sans text-stone-800 font-bold">
                    {bat}
                  </span>
                ))}
              </div>
            </div>

            {/* Target Line & Length */}
            <div className="p-3.5 rounded-xl bg-stone-100 border border-stone-300 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-sans text-stone-800 font-bold">
                <Target size={14} />
                <span>DIRECTED LINE & LENGTH:</span>
              </div>
              <p className="text-xs text-stone-800 font-sans leading-relaxed">
                {currentOverData.targetLineLength}
              </p>
            </div>

            {/* Tactical Rationale */}
            <div className="p-3.5 rounded-xl bg-stone-100 border border-stone-300 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-sans text-stone-800 font-bold">
                <Flame size={14} />
                <span>MATCHUP ANALYTICAL RATIONALE:</span>
              </div>
              <p className="text-xs text-stone-800 font-sans leading-relaxed">
                {currentOverData.matchupRationale}
              </p>
            </div>

            {/* Confidence & Quick Field Link */}
            <div className="pt-2 flex items-center justify-between">
              <div className="text-xs font-sans text-stone-800">
                Success Confidence: <span className="text-stone-800 font-bold">{currentOverData.confidencePct}%</span>
              </div>
              <button
                onClick={() => navigateToWorkspace("field-strategy")}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-stone-100 border border-stone-300 hover:bg-stone-100 text-stone-800 text-xs font-sans font-bold transition-all"
              >
                <span>OPEN FIELD CANVAS</span>
                <ArrowRight size={12} />
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

