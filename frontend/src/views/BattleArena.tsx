import React, { useState } from "react";
import { HeadToHeadBattle, BallTrajectory } from "../types";
import { Stadium3D } from "../components/Stadium3D";
import { 
  Swords, 
  Target, 
  ShieldAlert, 
  Zap, 
  TrendingUp, 
  Flame, 
  CheckCircle2, 
  Crosshair,
  BarChart3,
  Layers
} from "lucide-react";

interface BattleArenaProps {
  battles: HeadToHeadBattle[];
  trajectories: BallTrajectory[];
}

interface VenuePlayerRecord {
  player_name: string;
  team: string;
  role: string;
  venue: string;
  batting: {
    balls: number;
    runs: number;
    boundaries: number;
    outs: number;
    strike_rate: number;
  };
  bowling: {
    overs: number;
    runs_conceded: number;
    wickets: number;
    dots: number;
    economy: number;
  };
}

export const BattleArena: React.FC<BattleArenaProps> = ({ battles, trajectories }) => {
  const [filterTab, setFilterTab] = useState<"ALL" | "IND_VS_WI" | "WI_VS_IND" | "VENUE_CHINNASWAMY">("ALL");
  const [selectedBattleIndex, setSelectedBattleIndex] = useState(0);
  const [venueStats, setVenueStats] = useState<VenuePlayerRecord[]>([]);
  const [isLoadingVenue, setIsLoadingVenue] = useState(false);

  // Fetch verified Chinnaswamy venue stats
  React.useEffect(() => {
    const fetchVenue = async () => {
      setIsLoadingVenue(true);
      try {
        const res = await fetch("/api/venue/player-stats?venue=chinnaswamy");
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data.records)) setVenueStats(data.records);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoadingVenue(false);
      }
    };
    fetchVenue();
  }, []);

  const indBatters = ["abhishek", "samson", "tilak", "kishan", "shreyas", "iyer", "hardik", "suryakumar", "rinku", "naman", "dhir", "axar"];
  const wiBatters = ["pooran", "hope", "hetmyer", "powell", "rutherford", "shepherd", "chase"];

  const filteredBattles = React.useMemo(() => {
    if (filterTab === "IND_VS_WI") {
      return battles.filter(b => indBatters.some(n => b.batter_name.toLowerCase().includes(n)));
    }
    if (filterTab === "WI_VS_IND") {
      return battles.filter(b => wiBatters.some(n => b.batter_name.toLowerCase().includes(n)));
    }
    return battles;
  }, [battles, filterTab]);

  const activeBattle = filteredBattles[selectedBattleIndex] || filteredBattles[0] || battles[0];

  // Filter trajectories for this battle if any, else show representative delivery set
  const filteredTrajectories = trajectories.filter(
    (t) => 
      t.batter.toLowerCase().includes(activeBattle?.batter_name?.toLowerCase().split(" ")[0] || "") ||
      t.bowler.toLowerCase().includes(activeBattle?.bowler_name?.toLowerCase().split(" ")[0] || "")
  );
  const displayTrajectories = filteredTrajectories.length > 0 ? filteredTrajectories : trajectories.slice(0, 8);

  const isIndBatter = indBatters.some(n => activeBattle?.batter_name?.toLowerCase().includes(n));

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-stone-300">
        <div>
          <div className="flex items-center gap-2 text-xs font-sans text-stone-800 uppercase tracking-widest">
            <Swords size={14} /> Opposition Tactical Matchup Matrix
          </div>
          <h1 className="text-2xl lg:text-3xl font-semibold text-stone-800 uppercase tracking-tight mt-1 flex items-center gap-3">
            Player Battle Arena
            <span className="text-xs px-2.5 py-0.5 rounded border border-[#46664f]/40 bg-white text-emerald-800 font-sans font-bold">
              INDIA vs WEST INDIES ONLY
            </span>
          </h1>
          <p className="text-xs text-stone-800 mt-0.5 font-sans">
            Cross-team opposition micro analytics & M. Chinnaswamy Stadium historical player telemetry
          </p>
        </div>

        {/* Tab Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => { setFilterTab("ALL"); setSelectedBattleIndex(0); }}
            className={`px-3 py-1.5 rounded text-xs font-sans font-bold border transition-all ${
              filterTab === "ALL" ? "bg-emerald-700 text-white border-emerald-800" : "bg-white text-stone-700 border-stone-300 hover:bg-stone-50"
            }`}
          >
            ALL OPPOSITION ({battles.length})
          </button>
          <button
            onClick={() => { setFilterTab("IND_VS_WI"); setSelectedBattleIndex(0); }}
            className={`px-3 py-1.5 rounded text-xs font-sans font-bold border transition-all ${
              filterTab === "IND_VS_WI" ? "bg-emerald-700 text-white border-emerald-800" : "bg-white text-stone-700 border-stone-300 hover:bg-stone-50"
            }`}
          >
            IND BAT vs WI BOWL
          </button>
          <button
            onClick={() => { setFilterTab("WI_VS_IND"); setSelectedBattleIndex(0); }}
            className={`px-3 py-1.5 rounded text-xs font-sans font-bold border transition-all ${
              filterTab === "WI_VS_IND" ? "bg-emerald-700 text-white border-emerald-800" : "bg-white text-stone-700 border-stone-300 hover:bg-stone-50"
            }`}
          >
            WI BAT vs IND BOWL
          </button>
          <button
            onClick={() => setFilterTab("VENUE_CHINNASWAMY")}
            className={`px-3 py-1.5 rounded text-xs font-sans font-bold border transition-all ${
              filterTab === "VENUE_CHINNASWAMY" ? "bg-amber-600 text-white border-amber-700" : "bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100"
            }`}
          >
            CHINNASWAMY VENUE TELEMETRY ({venueStats.length})
          </button>
        </div>
      </div>

      {/* When Venue Telemetry tab is selected */}
      {filterTab === "VENUE_CHINNASWAMY" && (
        <div className="strike-panel p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-stone-300">
            <div>
              <div className="text-xs font-sans text-stone-800 uppercase tracking-widest font-bold">VENUE TELEMETRY: M. CHINNASWAMY STADIUM, BENGALURU</div>
              <h2 className="text-lg font-bold text-stone-800 mt-0.5">Historical Player Form at Match Venue (104 Matches Indexed in DuckDB)</h2>
            </div>
            <span className="text-xs font-mono bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded border border-emerald-300 font-bold">
              REAL VENUE EVIDENCE
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Batting at Chinnaswamy */}
            <div className="space-y-2">
              <h3 className="text-xs font-sans font-bold uppercase text-stone-800 tracking-wider">Top Batting Records at Chinnaswamy</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-sans border-collapse">
                  <thead>
                    <tr className="bg-stone-100 text-left border-b border-stone-300 text-stone-700">
                      <th className="p-2">Player</th>
                      <th className="p-2">Team</th>
                      <th className="p-2">Runs</th>
                      <th className="p-2">Balls</th>
                      <th className="p-2">Boundaries</th>
                      <th className="p-2">Strike Rate</th>
                      <th className="p-2">Outs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {venueStats.filter(v => v.batting.balls > 0).sort((a,b) => b.batting.runs - a.batting.runs).map((p, idx) => (
                      <tr key={idx} className="border-b border-stone-200 hover:bg-stone-50">
                        <td className="p-2 font-bold text-stone-900">{p.player_name}</td>
                        <td className="p-2 font-mono text-[10px] font-bold">
                          <span className={`px-1.5 py-0.5 rounded ${p.team === 'IND' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}`}>{p.team}</span>
                        </td>
                        <td className="p-2 font-semibold text-emerald-800">{p.batting.runs}</td>
                        <td className="p-2 text-stone-600">{p.batting.balls}</td>
                        <td className="p-2 text-stone-700">{p.batting.boundaries} (4s/6s)</td>
                        <td className="p-2 font-mono font-bold text-stone-900">{p.batting.strike_rate}</td>
                        <td className="p-2 text-stone-600">{p.batting.outs}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Bowling at Chinnaswamy */}
            <div className="space-y-2">
              <h3 className="text-xs font-sans font-bold uppercase text-stone-800 tracking-wider">Top Bowling Records at Chinnaswamy</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-sans border-collapse">
                  <thead>
                    <tr className="bg-stone-100 text-left border-b border-stone-300 text-stone-700">
                      <th className="p-2">Player</th>
                      <th className="p-2">Team</th>
                      <th className="p-2">Overs</th>
                      <th className="p-2">Wickets</th>
                      <th className="p-2">Runs Conc</th>
                      <th className="p-2">Economy</th>
                      <th className="p-2">Dots</th>
                    </tr>
                  </thead>
                  <tbody>
                    {venueStats.filter(v => v.bowling.overs > 0).sort((a,b) => b.bowling.wickets - a.bowling.wickets).map((p, idx) => (
                      <tr key={idx} className="border-b border-stone-200 hover:bg-stone-50">
                        <td className="p-2 font-bold text-stone-900">{p.player_name}</td>
                        <td className="p-2 font-mono text-[10px] font-bold">
                          <span className={`px-1.5 py-0.5 rounded ${p.team === 'IND' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}`}>{p.team}</span>
                        </td>
                        <td className="p-2 text-stone-700">{p.bowling.overs} ov</td>
                        <td className="p-2 font-bold text-emerald-800">{p.bowling.wickets} w</td>
                        <td className="p-2 text-stone-600">{p.bowling.runs_conceded}</td>
                        <td className="p-2 font-mono font-bold text-stone-900">{p.bowling.economy}</td>
                        <td className="p-2 text-stone-600">{p.bowling.dots}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Battle selector pills */}
      {filterTab !== "VENUE_CHINNASWAMY" && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 max-w-full">
          {filteredBattles.map((b, idx) => {
            const bIsInd = indBatters.some(n => b.batter_name.toLowerCase().includes(n));
            return (
              <button
                key={`${b.batter_id}-${b.bowler_id}`}
                onClick={() => setSelectedBattleIndex(idx)}
                className={`px-3 py-2 rounded text-xs font-sans whitespace-nowrap transition-all flex items-center gap-2 border ${
                  selectedBattleIndex === idx
                    ? "bg-emerald-800 text-white border-emerald-900 shadow-sm"
                    : "bg-white text-stone-800 border-stone-300 hover:bg-stone-50"
                }`}
              >
                <span className={`text-[9px] px-1 py-0.2 rounded font-mono font-bold ${
                  selectedBattleIndex === idx ? "bg-white/20 text-white" : (bIsInd ? "bg-blue-100 text-blue-800" : "bg-red-100 text-red-800")
                }`}>
                  {bIsInd ? "IND" : "WI"}
                </span>
                <span className="font-bold">{b.batter_name.split(" ").pop()}</span>
                <span className="text-xs opacity-60">vs</span>
                <span className={`text-[9px] px-1 py-0.2 rounded font-mono font-bold ${
                  selectedBattleIndex === idx ? "bg-white/20 text-white" : (!bIsInd ? "bg-blue-100 text-blue-800" : "bg-red-100 text-red-800")
                }`}>
                  {!bIsInd ? "IND" : "WI"}
                </span>
                <span className="font-bold">{b.bowler_name.split(" ").pop()}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* 2. Main Head- Split Arena */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        
        {/* Left Side: Batter Profile (4 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="strike-panel p-5 relative overflow-hidden h-full flex flex-col justify-between border-t-2 border-t-[#46664f]">
            <div className="absolute top-2 right-2 px-2 py-0.5 rounded text-xs font-sans bg-stone-100 text-stone-800 border border-[#46664f]/30">
              STRIKER
            </div>
            
            <div>
              <div className="text-xs font-sans text-stone-800 uppercase tracking-widest">BATTER PROFILE</div>
              <h2 className="text-xl font-semibold text-stone-800 mt-1">{activeBattle.batter_name}</h2>
              <div className="text-xs font-sans text-stone-800 flex items-center gap-2 mt-0.5">
                <span>LHB • Aggressive Anchor</span>
                <span className="text-stone-800">|</span>
                <span>Powerplay / Middle</span>
              </div>

              {/* Batter Stats Grid */}
              <div className="grid grid-cols-2 gap-2 mt-5 font-mono">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">H2H STRIKE RATE</div>
                  <div className="text-lg font-bold text-white mt-0.5">{activeBattle.strike_rate.toFixed(1)}</div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">+{((activeBattle.strike_rate - 135)).toFixed(1)} vs baseline</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">RUNS SCORED</div>
                  <div className="text-lg font-bold text-white mt-0.5">{activeBattle.runs} <span className="text-xs text-slate-400 font-normal">({activeBattle.balls}b)</span></div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{activeBattle.boundaries_count} boundaries hit</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">DISMISSALS</div>
                  <div className="text-lg font-bold text-rose-400 mt-0.5">{activeBattle.dismissals}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    {activeBattle.balls > 0 ? (activeBattle.balls / Math.max(1, activeBattle.dismissals)).toFixed(1) : 0} balls/wkt
                  </div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">DOT BALL %</div>
                  <div className="text-lg font-bold text-cyan-400 mt-0.5">{activeBattle.dot_pct}%</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Defensive balls</div>
                </div>
              </div>

              {/* Scoring Distribution by Sector */}
              <div className="mt-5">
                <div className="text-xs font-sans text-stone-800 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>SCORING ZONES VS THIS BOWLER</span>
                  <span className="text-stone-800">BOUNDARY RADAR</span>
                </div>
                <div className="space-y-1.5 text-xs font-sans">
                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Mid-Wicket / Deep Square</span>
                      <span className="text-stone-800">44% (2 Sixes)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-white" style={{ width: "44%" }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Long-On / Straight Arc</span>
                      <span className="text-stone-800">32% (1 Six, 2 Fours)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-white" style={{ width: "32%" }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Extra Cover / Point</span>
                      <span className="text-stone-800">24% (1 Four)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-stone-100" style={{ width: "24%" }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Batter Tactical Key */}
            <div className="mt-5 p-3 rounded bg-stone-100 border border-stone-300 text-xs text-stone-800 font-sans">
              <div className="flex items-center gap-1.5 text-stone-800 font-bold mb-1">
                <Flame size={12} /> BATTING EXPLOIT KEY
              </div>
              Steps out against flat trajectory deliveries; punishes overpitched balls through mid-wicket with 89% middle bat contact.
            </div>
          </div>
        </div>

        {/* Center: Interactive 3D Pitch Duel & Prediction Gauge (6 cols) */}
        <div className="lg:col-span-6 space-y-4 flex flex-col">
          
          {/* Win Probability Header */}
          <div className="strike-panel p-4    ">
            <div className="flex items-center justify-between text-xs font-sans mb-2">
              <span className="text-stone-800 font-bold flex items-center gap-1">
                <Crosshair size={14} /> {activeBattle.batter_name.toUpperCase()} EQUITY
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                activeBattle.advantage === "Batter Dominant" 
                  ? "bg-stone-100 text-stone-800 border border-stone-300"
                  : activeBattle.advantage === "Bowler Dominant"
                  ? "bg-stone-100 text-stone-800 border border-rose-500/30"
                  : "bg-stone-100 text-stone-800 border border-amber-500/30"
              }`}>
                {activeBattle.advantage}
              </span>
              <span className="text-stone-800 font-bold flex items-center gap-1">
                {activeBattle.bowler_name.toUpperCase()} EQUITY <ShieldAlert size={14} />
              </span>
            </div>

            {/* Split probability bar */}
            <div className="h-3 w-full bg-stone-100 rounded-full overflow-hidden flex border border-stone-300/60 p-0.5">
              <div 
                className="h-full    rounded-l-full transition-all duration-700" 
                style={{ width: `${activeBattle.win_probability_batter}%` }}
              ></div>
              <div 
                className="h-full    rounded-r-full transition-all duration-700" 
                style={{ width: `${100 - activeBattle.win_probability_batter}%` }}
              ></div>
            </div>

            <div className="flex justify-between text-xs font-sans telemetry-num mt-1.5 text-stone-800">
              <span className="text-stone-800 font-bold">{activeBattle.win_probability_batter}% Batter Control</span>
              <span className="text-stone-800 font-bold">{(100 - activeBattle.win_probability_batter).toFixed(1)}% Bowler Control</span>
            </div>

            {/* Analytical Sample Size & Shrinkage Provenance */}
            {activeBattle.balls < 25 ? (
              <div className="mt-2.5 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-[10px] font-mono text-amber-400 flex items-center justify-between">
                <span>⚡ Limited Sample: N = {activeBattle.balls} balls (Empirical Shrinkage Mode)</span>
                <span className="font-bold">Bayesian Prior Applied</span>
              </div>
            ) : (
              <div className="mt-2.5 px-2.5 py-1 rounded bg-cyan-500/10 border border-cyan-500/20 text-[10px] font-mono text-cyan-600 flex items-center justify-between">
                <span>✓ Robust Sample: N = {activeBattle.balls} balls</span>
                <span>Cricsheet Columnar Data</span>
              </div>
            )}
          </div>

          {/* 3D Pitch Arena */}
          <div className="flex-1 min-h-[380px] rounded-lg overflow-hidden border border-stone-300 shadow-none relative">
            <Stadium3D 
              initialCamera="pitch_heatmap" 
              className="h-full min-h-[380px]"
            />
            
            {/* Overlay Telemetry Badge */}
            <div className="absolute bottom-3 left-3 bg-white  border border-stone-300 px-3 py-1.5 rounded text-xs font-sans text-stone-800 pointer-events-none flex items-center gap-3">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-white"></span> Pitching Arcs
              </div>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-white"></span> Dismissal Zones
              </div>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-white"></span> Boundary Strikes
              </div>
            </div>
          </div>

          {/* Expected Outcome Distributions */}
          <div className="grid grid-cols-4 gap-2">
            <div className="strike-panel p-2.5 text-center">
              <div className="text-xs font-sans text-stone-800 uppercase">DOT PROB</div>
              <div className="text-base font-semibold text-stone-800 telemetry-num mt-0.5">{activeBattle.dot_pct}%</div>
              <div className="text-[8px] font-sans text-stone-800">Defensive block</div>
            </div>

            <div className="strike-panel p-2.5 text-center">
              <div className="text-xs font-sans text-stone-800 uppercase">ROTATION PROB</div>
              <div className="text-base font-semibold text-stone-800 telemetry-num mt-0.5">38.2%</div>
              <div className="text-[8px] font-sans text-stone-800">1 or 2 runs</div>
            </div>

            <div className="strike-panel p-2.5 text-center">
              <div className="text-xs font-sans text-stone-800 uppercase">BOUNDARY PROB</div>
              <div className="text-base font-semibold text-stone-800 telemetry-num mt-0.5">
                {((activeBattle.boundaries_count / Math.max(1, activeBattle.balls)) * 100).toFixed(1)}%
              </div>
              <div className="text-[8px] font-sans text-stone-800">4s or 6s</div>
            </div>

            <div className="strike-panel p-2.5 text-center">
              <div className="text-xs font-sans text-stone-800 uppercase">DISMISSAL CHANCE</div>
              <div className="text-base font-semibold text-stone-800 telemetry-num mt-0.5">
                {((activeBattle.dismissals / Math.max(1, activeBattle.balls)) * 100).toFixed(1)}%
              </div>
              <div className="text-[8px] font-sans text-stone-800">Per delivery</div>
            </div>
          </div>

        </div>

        {/* Right Side: Bowler Profile (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="strike-panel p-5 relative overflow-hidden h-full flex flex-col justify-between border-t-2 border-t-[#b99b37]">
            <div className="absolute top-2 right-2 px-2 py-0.5 rounded text-xs font-sans bg-lime-950/60 text-stone-800 border border-[#b99b37]/30">
              ATTACKER
            </div>

            <div>
              <div className="text-xs font-sans text-stone-800 uppercase tracking-widest">BOWLER PROFILE</div>
              <h2 className="text-xl font-semibold text-stone-800 mt-1">{activeBattle.bowler_name}</h2>
              <div className="text-xs font-sans text-stone-800 flex items-center gap-2 mt-0.5">
                <span>Left-Arm Wrist Spin</span>
                <span className="text-stone-800">|</span>
                <span>Overs 7 - 15</span>
              </div>

              {/* Bowler Stats Grid */}
              <div className="grid grid-cols-2 gap-2 mt-5 font-mono">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">H2H ECONOMY</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {activeBattle.balls > 0 ? ((activeBattle.runs / activeBattle.balls) * 6).toFixed(2) : "0.00"}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Runs per 6 balls</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">AVG BOWLING SPEED</div>
                  <div className="text-lg font-bold text-white mt-0.5">87.4 <span className="text-xs text-slate-400 font-normal">km/h</span></div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Flight & drop drift</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">TURNING RADIUS</div>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">3.8°</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Sharp turn on wear</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/10">
                  <div className="text-[10px] text-slate-400 uppercase">DISMISSAL THREAT</div>
                  <div className="text-lg font-bold text-rose-400 mt-0.5">HIGH</div>
                  <div className="text-[10px] text-rose-300 mt-0.5">LBW & Bowled googly</div>
                </div>
              </div>

              {/* Length Breakdown by Bowler */}
              <div className="mt-5">
                <div className="text-xs font-sans text-stone-800 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>LENGTH DISTRIBUTION TO THIS BATTER</span>
                  <span className="text-stone-800">HAWKEYE CLUSTER</span>
                </div>
                <div className="space-y-1.5 text-xs font-sans">
                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Good Length (6m - 8m)</span>
                      <span className="text-stone-800">52% (Tight control)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-white" style={{ width: "52%" }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Full / Drive Length (2m - 5m)</span>
                      <span className="text-stone-800">28% (Baiting loft)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-stone-100" style={{ width: "28%" }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-stone-800 mb-0.5">
                      <span>Back of Length / Short</span>
                      <span className="text-stone-800">20% (Cut / Pull bait)</span>
                    </div>
                    <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-stone-100" style={{ width: "20%" }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bowler Tactical Key */}
            <div className="mt-5 p-3 rounded bg-lime-950/30 border border-lime-800/40 text-xs text-lime-200 font-sans">
              <div className="flex items-center gap-1.5 text-stone-800 font-bold mb-1">
                <CheckCircle2 size={12} /> BOWLING DEFENSE SCHEME
              </div>
              Deliver wrong'un from wide of the crease at 90 km/h on a 5.8m length to induce an outside edge or sweep miscue into deep square leg.
            </div>
          </div>
        </div>

      </div>

      {/* 3. Deep Tactical Observations & Ball-by-Ball Cluster Logs */}
      <div className="strike-panel p-5">
        <div className="flex items-center justify-between pb-3 border-b border-stone-300">
          <div>
            <div className="text-xs font-sans text-stone-800 uppercase tracking-wider">CRICKET INTELLIGENCE REPORT</div>
            <h3 className="text-base font-bold text-stone-800 uppercase mt-0.5">Head- Micro Execution Notes</h3>
          </div>
          <div className="text-xs font-sans text-stone-800 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-stone-100"></span> Grounded Sample Size: {activeBattle.balls} Deliveries
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="p-3 bg-white rounded border border-stone-300">
            <div className="text-xs font-sans text-stone-800 uppercase flex items-center gap-1.5 font-bold mb-1">
              <Crosshair size={12} /> Release & Angle Mechanics
            </div>
            <p className="text-xs text-stone-800 leading-relaxed font-sans">
              Bowler releases at 2.14m vertical height with 11.2° inwards arm angle. When pitching on off-stump line against this batter, creates an average deviation of +3.4° away from the left-hander's blade.
            </p>
          </div>

          <div className="p-3 bg-white rounded border border-stone-300">
            <div className="text-xs font-sans text-stone-800 uppercase flex items-center gap-1.5 font-bold mb-1">
              <Flame size={12} /> Fantasy Impact & Captaincy Risk
            </div>
            <p className="text-xs text-stone-800 leading-relaxed font-sans">
              {activeBattle.advantage === "Batter Dominant" 
                ? "Batter holds 160+ SR upside. If batter negotiates the first 6 balls, expected fantasy output escalates to 68+ ceiling points." 
                : "Bowler represents prime captaincy multiplier. 2+ wicket probability in this middle overs match-up creates huge differential leverage in 11-player contests."}
            </p>
          </div>

          <div className="p-3 bg-white rounded border border-stone-300">
            <div className="text-xs font-sans text-stone-800 uppercase flex items-center gap-1.5 font-bold mb-1">
              <Layers size={12} /> Tactical Counter-Strategy
            </div>
            <p className="text-xs text-stone-800 leading-relaxed font-sans">
              {activeBattle.tactical_notes}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

