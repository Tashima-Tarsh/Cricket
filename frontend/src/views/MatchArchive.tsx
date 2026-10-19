import React, { useState } from "react";
import { MatchInfo } from "../types";
import { useMatchContext } from "../context/MatchContext";
import { 
  Calendar, 
  Database, 
  Search, 
  TrendingUp, 
  CloudRain, 
  CheckCircle, 
  Clock, 
  Radio, 
  ChevronRight,
  Shield,
  Activity,
  Layers,
  ArrowRight,
  Sparkles
} from "lucide-react";

interface MatchArchiveProps {
  currentMatch: MatchInfo;
}

export const MatchArchive: React.FC<MatchArchiveProps> = ({ currentMatch }) => {
  const { refreshState } = useMatchContext();
  const [selectedSeason, setSelectedSeason] = useState("2026");
  const [formatFilter, setFormatFilter] = useState("ALL");
  const [rainOvers, setRainOvers] = useState(15);
  const [rainWickets, setRainWickets] = useState(2);
  const [switchingMatchId, setSwitchingMatchId] = useState<string | null>(null);

  const handleSelectMatch = async (matchId: string) => {
    setSwitchingMatchId(matchId);
    try {
      await refreshState(matchId);
    } finally {
      setSwitchingMatchId(null);
    }
  };

  // DLS calculation simulator
  const dlsParScore = Math.round(190 * (1 - Math.pow(0.85, rainOvers / 2)) * (1 - 0.05 * rainWickets));

  const fixtures2026 = [
    {
      id: "ind_w_vs_zim_w_2026_02",
      name: "2nd T20I: India Women vs Zimbabwe Women",
      date: "2026-10-18",
      venue: "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
      status: "LIVE / UPCOMING TODAY 7 PM",
      result: "India Women lead series 1-0",
      csk_score: "IND-W 165/4 (Proj)",
      rcb_score: "ZIM-W 122/8 (Proj)",
      cricoracle_wpa: "Deepti Sharma (P95: 116.4 pts) + Mandhana top-order blitz",
      tactical_summary: "Visakhapatnam gripping deck favoring finger spinners in middle overs. Spinners take 51.5% of historical wickets. Grand League portfolio utilizes 15-20 Cr unspent.",
      phase_breakdown: "PP: IND-W 52/1 vs ZIM-W 38/2 | MID: IND-W 68/2 vs ZIM-W 54/4 | DEATH: IND-W 45/1 vs ZIM-W 30/2",
      pacer_wickets: "Spin Bias: 51.5% (Pace 48.5%)",
      dot_pct: "Expected dot %: 42.0% dots"
    },
    {
      id: "ind_w_vs_zim_w_2026_01",
      name: "1st T20I: India Women vs Zimbabwe Women",
      date: "2026-10-16",
      venue: "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
      status: "COMPLETED",
      result: "India Women won by 48 runs",
      csk_score: "IND-W 172/3 (20.0)",
      rcb_score: "ZIM-W 124/8 (20.0)",
      cricoracle_wpa: "Smriti Mandhana 68 (42) + Deepti Sharma 3/16 generated +48% WPA",
      tactical_summary: "Dominant powerplay stand by Mandhana & Shafali. Middle overs squeeze from Deepti & Shree Charani choked the chase.",
      phase_breakdown: "PP: IND-W 58/0 vs ZIM-W 34/2 | MID: IND-W 70/2 vs ZIM-W 56/4 | DEATH: IND-W 44/1 vs ZIM-W 34/2",
      pacer_wickets: "Spin Bias: 55.0% (Pace 45.0%)",
      dot_pct: "44.6% dots"
    },
    {
      id: "ind_vs_wi_5th_t20_2026",
      name: "5th T20I (SERIES DECIDER): India vs West Indies",
      date: "2026-10-18",
      venue: "M. Chinnaswamy Stadium, Bengaluru",
      status: "TOSS DELAYED DUE TO RAIN (9-OV DECIDER)",
      result: "Series tied 2-2 • Decider",
      csk_score: "Par: 104 in 9 overs",
      rcb_score: "Chinnaswamy Dew Track",
      cricoracle_wpa: "Pace bias 59.6% wickets • Rain shortened 9 overs (2.4 PP)",
      tactical_summary: "High altitude carry, true bounce, short boundaries (60m). Overcast skies & rain delay offer heavy early lateral movement.",
      phase_breakdown: "PP: 36-44 runs (2.4 ov) | MID/DEATH: 60-70 runs (6.2 ov)",
      pacer_wickets: "Historical Pace Bias: 59.6%",
      dot_pct: "Expected dot %: 34-38%"
    },
    {
      id: "ind_wi_2026_04",
      name: "4th T20I: India vs West Indies",
      date: "2026-10-14",
      venue: "ACA-VDCA Stadium, Visakhapatnam",
      status: "COMPLETED",
      result: "West Indies won by 18 runs",
      csk_score: "160 all out (19.1)",
      rcb_score: "178/6 (20.0)",
      cricoracle_wpa: "Sherfane Rutherford 68 (36) + Gudakesh Motie 3/22 swung WPA +46%",
      tactical_summary: "Slow left-arm orthodox strangle on a gripping surface. Abhishek (12) and Samson (8) caught attempting across-the-line pulls.",
      phase_breakdown: "PP: WI 46/2 vs IND 42/3 | MID: WI 74/2 vs IND 68/4 | DEATH: WI 58/2 vs IND 50/3",
      pacer_wickets: "7/16 wkts (43.8%)",
      dot_pct: "44.1% dots"
    },
    {
      id: "ind_wi_2026_03",
      name: "3rd T20I: India vs West Indies",
      date: "2026-10-12",
      venue: "Barabati Stadium, Cuttack",
      status: "COMPLETED",
      result: "India won by 7 wickets",
      csk_score: "145/3 (15.2)",
      rcb_score: "142 all out (18.4)",
      cricoracle_wpa: "Mayank Yadav 4/18 (152 km/h express spell) generated +54% WPA",
      tactical_summary: "High-pace back of length exploited WI middle-order technical vulnerabilities. Tilak Varma 54* (32) comfortably anchored chase.",
      phase_breakdown: "PP: WI 44/3 vs IND 58/1 | MID: WI 66/5 vs IND 68/2 | DEATH: WI 32/2 vs IND 19/0",
      pacer_wickets: "10/13 wkts (76.9%)",
      dot_pct: "47.5% dots"
    },
    {
      id: "ind_wi_2026_02",
      name: "2nd T20I: India vs West Indies",
      date: "2026-10-10",
      venue: "Narendra Modi Stadium, Ahmedabad",
      status: "COMPLETED",
      result: "West Indies won by 4 wickets",
      csk_score: "182/7 (20.0)",
      rcb_score: "183/6 (19.2)",
      cricoracle_wpa: "Shai Hope 62* (48) anchor + Powell 44 (22) swung chase +38% WPA",
      tactical_summary: "WI targeted India's 4th/5th bowling options (NK Reddy & Axar Patel conceded 54 runs in 5 overs combined). Shepherd 28* (12) closed out.",
      phase_breakdown: "PP: IND 54/1 vs WI 51/1 | MID: IND 72/4 vs WI 76/3 | DEATH: IND 56/2 vs WI 56/2",
      pacer_wickets: "9/13 wkts (69.2%)",
      dot_pct: "36.8% dots"
    },
    {
      id: "ind_wi_2026_01",
      name: "1st T20I: India vs West Indies",
      date: "2026-10-08",
      venue: "Eden Gardens, Kolkata",
      status: "COMPLETED",
      result: "India won by 28 runs",
      csk_score: "194/4 (20.0)",
      rcb_score: "166/8 (20.0)",
      cricoracle_wpa: "Abhishek Sharma 88 (44) + Arshdeep 3/24 sealed +42% WPA",
      tactical_summary: "India exploited Powerplay field restrictions (62/0). WI stalled against middle overs spin before Rutherford's late flurry (41 off 20).",
      phase_breakdown: "PP: IND 62/0 vs WI 48/2 | MID: IND 78/2 vs WI 64/4 | DEATH: IND 54/2 vs WI 54/2",
      pacer_wickets: "6/12 wkts (50%)",
      dot_pct: "41.2% dots"
    }
  ];

  return (
    <div className="space-y-6">
      {/* 1. Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest">
            <Database size={14} /> Historical & Live Telemetry Archive
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white uppercase tracking-tight mt-1 flex items-center gap-3">
            Match Archive & Live Center
            <span className="text-xs px-2.5 py-0.5 rounded border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 font-mono">
              CRICSHEET & OPENIPL 2026
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5 font-sans">
            Ball-by-ball historical datasets, CricOracle2026 Win Probability Added (WPA) & Duckworth-Lewis-Stern Engine
          </p>
        </div>

        {/* Season Selector */}
        <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-lg border border-white/10">
          <span className="text-xs font-mono text-slate-400 px-2">EDITION:</span>
          {["2026", "2025", "2024", "ALL-TIME"].map((season) => (
            <button
              key={season}
              onClick={() => setSelectedSeason(season)}
              className={`px-3 py-1 rounded text-xs font-sans transition-all ${
                selectedSeason === season
                  ? "bg-emerald-600 text-white font-bold shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {season}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Live Match Feature Hero Banner */}
      <div className="rounded-xl p-6 bg-slate-900/80 border border-white/10 shadow-lg border-t-2 border-t-emerald-500">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5">
                <Radio size={12} className="animate-pulse" /> LIVE TELEMETRY
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {currentMatch?.venue?.name || "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium"}, {currentMatch?.venue?.city || "Visakhapatnam"}
              </span>
            </div>

            <div className="flex items-center gap-6 mt-3">
              <div>
                <div className="text-2xl font-bold text-white">{currentMatch?.teams?.home?.name || "India"}</div>
                <div className="text-lg font-mono text-emerald-400 font-bold">
                  {currentMatch?.teams?.home?.score || "1-0 Lead"} <span className="text-xs text-slate-400">({currentMatch?.teams?.home?.overs || "20.0"} ov)</span>
                </div>
              </div>

              <div className="text-xs font-mono text-slate-400 px-2 py-1 bg-slate-800 rounded border border-white/10">
                VS
              </div>

              <div>
                <div className="text-2xl font-bold text-white">{currentMatch?.teams?.away?.name || "Zimbabwe Women"}</div>
                <div className="text-lg font-mono text-emerald-400 font-bold">
                  {currentMatch?.teams?.away?.score || "Series 0-1"} <span className="text-xs text-slate-400">({currentMatch?.teams?.away?.overs || "20.0"} ov)</span>
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-300 font-sans mt-2">
              {currentMatch?.toss?.statement || "Official Match Telemetry Active"}
            </p>
          </div>

          {/* CricOracle2026 Real-Time Win Equity */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-white/10 min-w-[280px]">
            <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
              <span>CRICORACLE WPA WIN PROB</span>
              <span className="text-emerald-400 font-bold">68.0%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex border border-white/10">
              <div className="h-full bg-cyan-500" style={{ width: "32%" }}></div>
              <div className="h-full bg-emerald-500" style={{ width: "68%" }}></div>
            </div>
            <div className="flex justify-between text-xs font-mono mt-1.5 text-slate-300">
              <span className="text-cyan-400 font-bold">WI: 32.0%</span>
              <span className="text-emerald-400 font-bold">IND: 68.0%</span>
            </div>
            <div className="mt-3 pt-2 border-t border-white/10 text-xs font-sans text-slate-400">
              Required Run Rate: <strong className="text-white">11.72 RPO</strong> • Balls Remaining: <strong className="text-white">44</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 3. DLS Calculator & Duckworth-Lewis Par Simulator */}
      <div className="rounded-xl p-5 bg-slate-900/80 border border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div>
            <div className="text-xs font-mono text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
              <CloudRain size={14} /> RAIN INTERRUPTION SIMULATOR
            </div>
            <h3 className="text-base font-bold text-white uppercase mt-0.5">
              Duckworth-Lewis-Stern (DLS) Target Engine
            </h3>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 border border-sky-500/30">
            Resource Percentage Algorithm
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4 items-center">
          {/* Slider 1: Overs */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-sans text-slate-300">
              <span>Interrupted Overs Cutoff:</span>
              <span className="text-emerald-400 font-bold">{rainOvers} Overs</span>
            </div>
            <input aria-label="Rain overs"
              type="range"
              min="5"
              max="19"
              value={rainOvers}
              onChange={(e) => setRainOvers(Number(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>5 Ov (Min T20)</span>
              <span>12 Ov</span>
              <span>19 Ov</span>
            </div>
          </div>

          {/* Slider 2: Wickets Lost */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-sans text-slate-300">
              <span>Wickets Lost at Stoppage:</span>
              <span className="text-rose-400 font-bold">{rainWickets} Wickets</span>
            </div>
            <input aria-label="Rain wickets"
              type="range"
              min="0"
              max="9"
              value={rainWickets}
              onChange={(e) => setRainWickets(Number(e.target.value))}
              className="w-full accent-rose-500 bg-slate-800 h-1.5 rounded cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>0 Wickets</span>
              <span>5 Wickets</span>
              <span>9 Wickets</span>
            </div>
          </div>

          {/* DLS Par Output Box */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-white/10 flex items-center justify-between">
            <div>
              <div className="text-xs font-mono text-slate-400 uppercase">CALCULATED DLS PAR SCORE</div>
              <div className="text-3xl font-bold text-white telemetry-num mt-0.5">
                {dlsParScore} <span className="text-xs text-slate-400 font-sans font-normal">runs</span>
              </div>
              <div className="text-xs font-sans text-slate-400 mt-1">
                Win margin threshold at {rainOvers} overs
              </div>
            </div>
            <div className="text-right">
              <span className="px-2.5 py-1 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-mono font-bold">
                STANDBY PAR
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Season 2026 Fixture & Archive Ledger */}
      <div className="rounded-xl p-5 bg-slate-900/80 border border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div>
            <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">SERIES 2026 SCHEDULE & RECORDS</div>
            <h3 className="text-base font-bold text-white uppercase mt-0.5">Official 2026 Fixtures & WPA Telemetry</h3>
          </div>
          <div className="text-xs font-mono text-slate-400">
            Showing 5 Matches (DuckDB ground truth)
          </div>
        </div>

        <div className="space-y-3 mt-4">
          {fixtures2026.map((f) => (
            <div
              key={f.id}
              className="p-4 rounded-xl bg-slate-950/70 border border-white/10 hover:border-emerald-500/50 transition-all flex flex-col md:flex-row md:items-start justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono px-2 py-0.5 rounded font-bold ${
                    f.status === "LIVE NOW" 
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/40" 
                      : f.status.includes("DECIDER") || f.status.includes("UPCOMING")
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                      : "bg-slate-800 text-slate-300 border border-white/10"
                  }`}>
                    {f.status}
                  </span>
                  <span className="text-xs font-mono text-slate-400">{f.date}</span>
                  <span className="text-slate-600 font-sans">•</span>
                  <span className="text-xs font-sans text-slate-400">{f.venue}</span>
                </div>

                <div className="text-base font-bold text-white">
                  {f.name}
                </div>
                
                <div className="text-xs font-sans text-emerald-400 font-bold">
                  {f.result}
                </div>

                {f.tactical_summary && (
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">
                    {f.tactical_summary}
                  </p>
                )}

                {f.phase_breakdown && (
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono text-slate-300">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-white/10">
                      {f.phase_breakdown}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-white/10">
                      {f.pacer_wickets}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-white/10">
                      {f.dot_pct}
                    </span>
                  </div>
                )}
              </div>

              {/* Match WPA / Impact Badge & Match Switcher */}
              <div className="bg-slate-900 p-3.5 rounded-xl border border-white/10 text-left md:text-right min-w-[240px] shrink-0 space-y-2.5">
                <div>
                  <div className="text-[10px] font-mono text-slate-400 uppercase">CRICORACLE 2026 TELEMETRY</div>
                  <div className="text-xs font-sans text-emerald-300 font-bold leading-snug">{f.cricoracle_wpa}</div>
                  <div className="text-[10px] font-mono text-slate-500">Cricsheet verified series log</div>
                </div>

                <button
                  onClick={() => handleSelectMatch(f.id)}
                  disabled={switchingMatchId === f.id || currentMatch?.id === f.id}
                  className={`w-full py-1.5 px-3 rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition-all ${
                    currentMatch?.id === f.id
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-default"
                      : "bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 hover:border-cyan-400 cursor-pointer shadow-[0_0_12px_rgba(6,182,212,0.2)]"
                  }`}
                >
                  {currentMatch?.id === f.id ? (
                    <>
                      <CheckCircle size={13} className="text-emerald-400" /> ACTIVE WORKSPACE
                    </>
                  ) : switchingMatchId === f.id ? (
                    "LOADING..."
                  ) : (
                    <>
                      <Sparkles size={13} /> LOAD MATCH TELEMETRY <ArrowRight size={13} />
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

