import React, { useState } from "react";
import { useMatchContext } from "../context/MatchContext";
import { DeliveryRecord } from "../types";
import {
  ListFilter,
  Download,
  Activity,
  Flame,
  TrendingUp,
  CircleDot,
  Shield,
  Layers,
  Search
} from "lucide-react";

// Real sample deliveries from recent matches (Matches 1-4)
const SAMPLE_DELIVERIES: DeliveryRecord[] = [
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 1, batter: "Abhishek Sharma", bowler: "Shamar Joseph", non_striker: "Sanju Samson", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: false, phase: "Powerplay", speed_kmh: 149.2, shot_zone: "Cover" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 2, batter: "Abhishek Sharma", bowler: "Shamar Joseph", non_striker: "Sanju Samson", runs_batter: 4, runs_extras: 0, runs_total: 4, is_wicket: false, phase: "Powerplay", speed_kmh: 151.0, shot_zone: "Point" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 3, batter: "Abhishek Sharma", bowler: "Shamar Joseph", non_striker: "Sanju Samson", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: false, phase: "Powerplay", speed_kmh: 150.4, shot_zone: "Mid-Off" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 4, batter: "Abhishek Sharma", bowler: "Shamar Joseph", non_striker: "Sanju Samson", runs_batter: 6, runs_extras: 0, runs_total: 6, is_wicket: false, phase: "Powerplay", speed_kmh: 147.8, shot_zone: "Mid-Wicket" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 5, batter: "Abhishek Sharma", bowler: "Shamar Joseph", non_striker: "Sanju Samson", runs_batter: 1, runs_extras: 0, runs_total: 1, is_wicket: false, phase: "Powerplay", speed_kmh: 148.5, shot_zone: "Fine Leg" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 1, ball: 6, batter: "Sanju Samson", bowler: "Shamar Joseph", non_striker: "Abhishek Sharma", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: false, phase: "Powerplay", speed_kmh: 152.1, shot_zone: "Gully" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 1, batter: "Abhishek Sharma", bowler: "Roston Chase", non_striker: "Sanju Samson", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: false, phase: "Powerplay", speed_kmh: 92.4, shot_zone: "Stumps" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 2, batter: "Abhishek Sharma", bowler: "Roston Chase", non_striker: "Sanju Samson", runs_batter: 1, runs_extras: 0, runs_total: 1, is_wicket: false, phase: "Powerplay", speed_kmh: 94.0, shot_zone: "Long-On" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 3, batter: "Sanju Samson", bowler: "Roston Chase", non_striker: "Abhishek Sharma", runs_batter: 4, runs_extras: 0, runs_total: 4, is_wicket: false, phase: "Powerplay", speed_kmh: 90.1, shot_zone: "Extra Cover" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 4, batter: "Sanju Samson", bowler: "Roston Chase", non_striker: "Abhishek Sharma", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: false, phase: "Powerplay", speed_kmh: 91.8, shot_zone: "Short Mid-Wicket" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 5, batter: "Sanju Samson", bowler: "Roston Chase", non_striker: "Abhishek Sharma", runs_batter: 6, runs_extras: 0, runs_total: 6, is_wicket: false, phase: "Powerplay", speed_kmh: 88.5, shot_zone: "Straight Long-Off" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 2, ball: 6, batter: "Sanju Samson", bowler: "Roston Chase", non_striker: "Abhishek Sharma", runs_batter: 1, runs_extras: 0, runs_total: 1, is_wicket: false, phase: "Powerplay", speed_kmh: 93.2, shot_zone: "Square Leg" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 3, ball: 4, batter: "Abhishek Sharma", bowler: "Roston Chase", non_striker: "Sanju Samson", runs_batter: 0, runs_extras: 0, runs_total: 0, is_wicket: true, wicket_type: "bowled", player_dismissed: "Abhishek Sharma", phase: "Powerplay", speed_kmh: 93.6, shot_zone: "Bowled" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 8, ball: 3, batter: "Tilak Varma", bowler: "Gudakesh Motie", non_striker: "Ishan Kishan", runs_batter: 4, runs_extras: 0, runs_total: 4, is_wicket: false, phase: "Middle", speed_kmh: 89.2, shot_zone: "Deep Backward Square" },
  { match_id: "ind_wi_decider_2026", innings: 1, over: 18, ball: 5, batter: "Sherfane Rutherford", bowler: "Arshdeep Singh", non_striker: "Rovman Powell", runs_batter: 6, runs_extras: 0, runs_total: 6, is_wicket: false, phase: "Death", speed_kmh: 138.4, shot_zone: "Deep Mid-Wicket" }
];

export const BallByBallLab: React.FC = () => {
  const { currentMatch, selectedPhase } = useMatchContext();
  const [sourceMode, setSourceMode] = useState<"SERIES" | "DUCKDB">("SERIES");
  const [selectedInnings, setSelectedInnings] = useState<number>(1);
  const [filterPhase, setFilterPhase] = useState<string>("ALL");
  const [searchFilter, setSearchFilter] = useState<string>("");
  const [duckdbDeliveries, setDuckdbDeliveries] = useState<DeliveryRecord[]>([]);
  const [isLoadingDuckdb, setIsLoadingDuckdb] = useState<boolean>(false);

  // Fetch live deliveries from DuckDB
  const fetchDuckdbDeliveries = async (phase = filterPhase) => {
    setIsLoadingDuckdb(true);
    try {
      const url = `/api/duckdb/deliveries?limit=150&phase=${phase !== "ALL" ? phase : ""}&match_id=${encodeURIComponent(currentMatch?.id || "")}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "success" && data.deliveries) {
          setDuckdbDeliveries(data.deliveries);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch DuckDB deliveries:", err);
    } finally {
      setIsLoadingDuckdb(false);
    }
  };

  const handleSourceModeChange = (mode: "SERIES" | "DUCKDB") => {
    setSourceMode(mode);
    if (mode === "DUCKDB" && duckdbDeliveries.length === 0) {
      fetchDuckdbDeliveries();
    }
  };

  const activeDataset = sourceMode === "DUCKDB" ? duckdbDeliveries : SAMPLE_DELIVERIES;

  const filteredDeliveries = activeDataset.filter((d) => {
    if (sourceMode === "SERIES" && d.innings !== selectedInnings) return false;
    if (filterPhase !== "ALL" && d.phase !== filterPhase) return false;
    if (searchFilter) {
      const q = searchFilter.toLowerCase();
      return (
        d.batter.toLowerCase().includes(q) ||
        d.bowler.toLowerCase().includes(q) ||
        (d.shot_zone && d.shot_zone.toLowerCase().includes(q))
      );
    }
    return true;
  });

  const totalRuns = filteredDeliveries.reduce((acc, d) => acc + d.runs_total, 0);
  const totalWickets = filteredDeliveries.filter((d) => d.is_wicket).length;
  const dotCount = filteredDeliveries.filter((d) => d.runs_total === 0 && !d.is_wicket).length;
  const boundaryCount = filteredDeliveries.filter((d) => d.runs_batter >= 4).length;
  const dotBallPct = filteredDeliveries.length > 0 ? Math.round((dotCount / filteredDeliveries.length) * 100) : 0;

  const handleExportCSV = () => {
    let csv = "Match,Innings,Over,Ball,Batter,Bowler,Runs_Bat,Extras,Total,Wicket,Type,Phase,Speed_kmh,Zone\n";
    filteredDeliveries.forEach((d) => {
      csv += `${d.match_id},${d.innings},${d.over},${d.ball},"${d.batter}","${d.bowler}",${d.runs_batter},${d.runs_extras},${d.runs_total},${d.is_wicket},"${d.wicket_type || ""}","${d.phase}",${d.speed_kmh || ""},"${d.shot_zone || ""}"\n`;
    });
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `BALL_BY_BALL_${currentMatch.id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* 1. Header & Filters Toolbar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-stone-300">
        <div>
          <div className="flex items-center gap-2 text-xs font-sans text-stone-800 uppercase tracking-widest">
            <CircleDot size={14} /> DuckDB Columnar Delivery Telemetry (194,239 Indexed)
          </div>
          <h1 className="text-2xl lg:text-3xl font-semibold text-stone-800 tracking-tight flex items-center gap-3 mt-1">
            Ball-by-Ball Lab
            <span className="text-xs px-2.5 py-0.5 rounded border border-stone-300 bg-stone-100 text-stone-800 font-sans">
              MICRO EVENT EXPLORER
            </span>
          </h1>
          <p className="text-xs text-stone-800 font-sans mt-0.5">
            Delivery-level speeds, line & lengths, dot pressure progression, and phase breakdowns.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Source Dataset Selector */}
          <div className="flex bg-white/[0.04] p-1 rounded-xl border border-stone-300 text-xs font-sans">
            <button
              onClick={() => handleSourceModeChange("SERIES")}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                sourceMode === "SERIES"
                  ? "bg-stone-100 text-stone-800 shadow-md shadow-cyan-500/20"
                  : "text-stone-800 text-stone-800"
              }`}
            >
              2026 MATCH
            </button>
            <button
              onClick={() => handleSourceModeChange("DUCKDB")}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                sourceMode === "DUCKDB"
                  ? "bg-stone-100 text-stone-800 shadow-md shadow-purple-500/20"
                  : "text-stone-800 text-stone-800"
              }`}
            >
              {isLoadingDuckdb ? "LOADING..." : "DUCKDB (194k)"}
            </button>
          </div>

          {/* Innings Selector (only if in SERIES mode) */}
          {sourceMode === "SERIES" && (
            <div className="flex bg-white/[0.04] p-1 rounded-xl border border-stone-300 text-xs font-sans">
              {[1, 2].map((inn) => (
                <button
                  key={inn}
                  onClick={() => setSelectedInnings(inn)}
                  className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                    selectedInnings === inn
                      ? "bg-stone-100 text-stone-800 shadow-md shadow-cyan-500/20"
                      : "text-stone-800 text-stone-800"
                  }`}
                >
                  Innings {inn}
                </button>
              ))}
            </div>
          )}

          {/* Phase Filter */}
          <div className="flex bg-white/[0.04] p-1 rounded-xl border border-stone-300 text-xs font-sans">
            {["ALL", "Powerplay", "Middle", "Death"].map((ph) => (
              <button
                key={ph}
                onClick={() => setFilterPhase(ph)}
                className={`px-2.5 py-1.5 rounded-lg font-bold transition-all ${
                  filterPhase === ph
                    ? "bg-stone-100 text-stone-800"
                    : "text-stone-800 text-stone-800"
                }`}
              >
                {ph}
              </button>
            ))}
          </div>

          <button
            onClick={handleExportCSV}
            className="px-4 py-2 rounded-xl bg-white/[0.05] border border-stone-300 hover:border-stone-300 text-stone-800 text-stone-800 text-xs font-sans font-bold flex items-center gap-2 transition-all"
          >
            <Download size={14} className="text-stone-800" /> EXPORT CSV
          </button>
        </div>
      </div>

      {/* 2. Micro Telemetry Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border border-stone-300 bg-white/[0.02]">
          <div className="text-xs font-sans text-stone-800 uppercase">RUNS IN FILTER</div>
          <div className="text-2xl font-semibold text-stone-800 font-sans mt-1">{totalRuns} Runs</div>
          <div className="text-xs font-sans text-stone-800 mt-1 flex items-center gap-1">
            <TrendingUp size={12} /> {(totalRuns / Math.max(1, filteredDeliveries.length) * 6).toFixed(1)} Projected RPO
          </div>
        </div>

        <div className="p-4 rounded-xl border border-stone-300 bg-white/[0.02]">
          <div className="text-xs font-sans text-stone-800 uppercase">WICKETS FALLEN</div>
          <div className="text-2xl font-semibold text-stone-800 font-sans mt-1">{totalWickets} Wkts</div>
          <div className="text-xs font-sans text-stone-800 mt-1">Striking every {(filteredDeliveries.length / Math.max(1, totalWickets)).toFixed(0)} balls</div>
        </div>

        <div className="p-4 rounded-xl border border-stone-300 bg-white/[0.02]">
          <div className="text-xs font-sans text-stone-800 uppercase">DOT-BALL PRESSURE</div>
          <div className="text-2xl font-semibold text-stone-800 font-sans mt-1">{dotBallPct}%</div>
          <div className="text-xs font-sans text-stone-800 mt-1">{dotCount} Dot deliveries</div>
        </div>

        <div className="p-4 rounded-xl border border-stone-300 bg-white/[0.02]">
          <div className="text-xs font-sans text-stone-800 uppercase">BOUNDARIES HIT</div>
          <div className="text-2xl font-semibold text-stone-800 font-sans mt-1">{boundaryCount} Boundaries</div>
          <div className="text-xs font-sans text-stone-800 mt-1">1 every {(filteredDeliveries.length / Math.max(1, boundaryCount)).toFixed(1)} balls</div>
        </div>
      </div>

      {/* 3. Delivery Table with Filter */}
      <div className="rounded-2xl border border-stone-300    p-6 shadow-none space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs font-sans text-stone-800">
            Showing <strong className="text-stone-800">{filteredDeliveries.length}</strong> Deliveries in Innings {selectedInnings} ({filterPhase})
          </div>

          <div className="relative w-full sm:w-64">
            <Search size={14} className="absolute left-3 top-2.5 text-stone-800" />
            <input aria-label="Search filter"
              type="text"
              placeholder="Search batter, bowler, shot..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-white/[0.04] border border-stone-300 text-xs font-sans text-stone-800 placeholder-slate-500 focus:outline-none focus:border-stone-300"
            />
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="border-b border-stone-300 text-stone-800 text-xs uppercase">
                <th className="py-2 px-3">OVER.BALL</th>
                <th className="py-2 px-3">BATTER</th>
                <th className="py-2 px-3">BOWLER</th>
                <th className="py-2 px-2 text-center">SPEED</th>
                <th className="py-2 px-3">SHOT ZONE</th>
                <th className="py-2 px-2 text-center">RUNS</th>
                <th className="py-2 px-3">EVENT</th>
                <th className="py-2 px-2 text-center">PHASE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredDeliveries.map((d, idx) => (
                <tr
                  key={`${d.innings}-${d.over}-${d.ball}-${idx}`}
                  className="hover:bg-white/[0.03] transition-colors"
                >
                  <td className="py-2.5 px-3 font-bold text-stone-800">
                    {d.over - 1}.{d.ball}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-stone-800">{d.batter}</td>
                  <td className="py-2.5 px-3 text-stone-800">{d.bowler}</td>
                  <td className="py-2.5 px-2 text-center font-sans text-stone-800">
                    {d.speed_kmh ? `${d.speed_kmh} km/h` : "—"}
                  </td>
                  <td className="py-2.5 px-3 text-stone-800">{d.shot_zone || "Defensive"}</td>
                  <td className="py-2.5 px-2 text-center">
                    <span
                      className={`px-2 py-0.5 rounded font-bold ${
                        d.runs_total >= 6
                          ? "bg-stone-100 text-stone-800 border border-stone-300"
                          : d.runs_total >= 4
                          ? "bg-stone-100 text-stone-800 border border-stone-300"
                          : d.runs_total === 0
                          ? "text-stone-800"
                          : "text-stone-800"
                      }`}
                    >
                      {d.runs_total}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    {d.is_wicket ? (
                      <span className="px-2 py-0.5 rounded bg-stone-100 text-stone-800 border border-rose-500/30 font-bold">
                        WICKET ({d.wicket_type})
                      </span>
                    ) : (
                      <span className="text-stone-800">Legal ball</span>
                    )}
                  </td>
                  <td className="py-2.5 px-2 text-center text-stone-800">{d.phase}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
