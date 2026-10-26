import React from "react";
import { ArrowLeftRight, Check, X, Sparkles, AlertTriangle, ShieldCheck } from "lucide-react";
import { PitchPlayer } from "./PitchMap";

interface TeamCompareProps {
  uniqueTeam: {
    name: string;
    captain: string;
    vice_captain: string;
    crowd_overlap_pct: number;
    projected_points: number;
    rank_1_probability_pct: number;
    total_credits: number;
    players: PitchPlayer[];
  };
  chalkTeam?: {
    name: string;
    captain: string;
    vice_captain: string;
    crowd_overlap_pct: number;
    projected_points: number;
    rank_1_probability_pct: number;
    total_credits: number;
    players: PitchPlayer[];
  };
}

export const TeamCompare: React.FC<TeamCompareProps> = ({ uniqueTeam, chalkTeam }) => {
  // Sort players by public ownership to dynamically find the highest-owned chalk picks
  const sortedByOwn = [...uniqueTeam.players].sort((a, b) => b.predicted_ownership - a.predicted_ownership);
  const chalkCaptainName = sortedByOwn[0]?.name || "High Chalk C";
  const chalkVcName = sortedByOwn[1]?.name || "High Chalk VC";
  const chalkOverlap = Math.min(880.0, Math.round(sortedByOwn.slice(0, 11).reduce((acc, p) => acc + p.predicted_ownership, 0) || 795.0));

  const syntheticChalk = chalkTeam || {
    name: "Casual Public Consensus (Chalk)",
    captain: chalkCaptainName,
    vice_captain: chalkVcName,
    crowd_overlap_pct: chalkOverlap,
    projected_points: Math.round(uniqueTeam.projected_points * 0.96),
    rank_1_probability_pct: 0.12,
    total_credits: 99.5,
    players: sortedByOwn.slice(0, 11)
  };

  const uniquePlayerNames = new Set(uniqueTeam.players.map((p) => p.name));

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0B0F14] p-5 shadow-2xl flex flex-col gap-6">
      <div className="flex items-center justify-between pb-3 border-b border-white/5">
        <div>
          <h4 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
            <ArrowLeftRight size={16} className="text-[#FFB300]" />
            Side-by-Side Team Diff: Contrarian Edge vs Public Chalk
          </h4>
          <p className="text-xs text-[#8A96A3]">
            See why the unique team maximizes solitary Rank-1 equity while avoiding mass prize splits.
          </p>
        </div>
      </div>

      {/* High-Level Comparison KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Unique Team Card */}
        <div className="p-4 rounded-xl border border-[#00C853]/40 bg-[#141A22] flex flex-col gap-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-[#00C853]/20 border-b border-l border-[#00C853]/40 text-[#00C853] text-[10px] font-mono font-bold rounded-bl-lg">
            YOUR GENERATED EDGE
          </div>
          <div>
            <span className="text-[10px] font-mono text-[#00C853] font-bold uppercase">
              Low-Crowd Overlap Portfolio
            </span>
            <h5 className="text-base font-bold text-white">{uniqueTeam.name}</h5>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Crowd Overlap</span>
              <strong className="text-sm text-[#00C853]">{uniqueTeam.crowd_overlap_pct}%</strong>
              <span className="text-[9px] text-[#00C853] block">Low collision risk</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Rank-1 Probability</span>
              <strong className="text-sm text-[#FFB300]">{uniqueTeam.rank_1_probability_pct}%</strong>
              <span className="text-[9px] text-[#FFB300] block">Solitary win equity</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Captain (2x)</span>
              <strong className="text-xs text-white truncate block">{uniqueTeam.captain}</strong>
              <span className="text-[9px] text-[#FFB300] block">Differential pick</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Credits Left</span>
              <strong className="text-xs text-white block">{(100.0 - uniqueTeam.total_credits).toFixed(1)} Cr</strong>
              <span className="text-[9px] text-[#8A96A3] block">Kills duplication</span>
            </div>
          </div>
        </div>

        {/* Chalk Team Card */}
        <div className="p-4 rounded-xl border border-[#FF5252]/40 bg-[#141A22] flex flex-col gap-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-[#FF5252]/20 border-b border-l border-[#FF5252]/40 text-[#FF5252] text-[10px] font-mono font-bold rounded-bl-lg">
            THE CHALK TRAP
          </div>
          <div>
            <span className="text-[10px] font-mono text-[#FF5252] font-bold uppercase">
              Casual Public Consensus
            </span>
            <h5 className="text-base font-bold text-white">{syntheticChalk.name}</h5>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Crowd Overlap</span>
              <strong className="text-sm text-[#FF5252]">{syntheticChalk.crowd_overlap_pct}%</strong>
              <span className="text-[9px] text-[#FF5252] block">Extremely heavy clumping</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Rank-1 Probability</span>
              <strong className="text-sm text-[#8A96A3]">{syntheticChalk.rank_1_probability_pct}%</strong>
              <span className="text-[9px] text-[#FF5252] block">Splits top prize 25k times</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Captain (2x)</span>
              <strong className="text-xs text-white truncate block">{syntheticChalk.captain}</strong>
              <span className="text-[9px] text-[#FF5252] block">Owned by 45%+ of entries</span>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F14] border border-white/5">
              <span className="text-[#8A96A3] block text-[10px]">Credits Left</span>
              <strong className="text-xs text-white block">{(100.0 - syntheticChalk.total_credits).toFixed(1)} Cr</strong>
              <span className="text-[9px] text-[#FF5252] block">Max credits = max duplicate</span>
            </div>
          </div>
        </div>
      </div>

      {/* Roster Diff List */}
      <div>
        <h6 className="text-xs font-mono font-bold uppercase text-[#8A96A3] mb-3">
          Your Strategic Lineup Composition
        </h6>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {uniqueTeam.players.map((p) => {
            const isDiff = p.predicted_ownership < 30.0;
            const isChalk = p.predicted_ownership >= 60.0;
            return (
              <div
                key={p.id}
                className="p-2 rounded-lg border border-white/5 bg-[#141A22] flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded bg-[#0B0F14] text-[10px] font-mono font-bold text-slate-300">
                    {p.role}
                  </span>
                  <span className="text-white font-medium truncate max-w-[110px]">{p.name}</span>
                </div>
                <div className="text-right font-mono">
                  <span
                    className={`text-[11px] font-bold ${
                      isDiff ? "text-[#00C853]" : isChalk ? "text-[#FF5252]" : "text-[#FFB300]"
                    }`}
                  >
                    {p.predicted_ownership.toFixed(0)}%
                  </span>
                  <span className="text-[10px] text-[#8A96A3] block">
                    {p.predicted_points.toFixed(0)} pts
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

