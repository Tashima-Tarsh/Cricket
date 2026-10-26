import React from "react";
import { Users, TrendingUp, AlertTriangle, Sparkles } from "lucide-react";
import { PitchPlayer } from "./PitchMap";

interface OwnershipHeatmapProps {
  players: PitchPlayer[];
  selectedPlayerIds?: string[];
  onPlayerClick?: (player: PitchPlayer) => void;
}

export const OwnershipHeatmap: React.FC<OwnershipHeatmapProps> = ({
  players,
  selectedPlayerIds = [],
  onPlayerClick
}) => {
  // Sort players by ownership descending
  const sorted = [...players].sort((a, b) => b.predicted_ownership - a.predicted_ownership);

  const chalkTier = sorted.filter((p) => p.predicted_ownership >= 60.0);
  const midTier = sorted.filter((p) => p.predicted_ownership >= 30.0 && p.predicted_ownership < 60.0);
  const diffTier = sorted.filter((p) => p.predicted_ownership < 30.0);

  const selectedSet = new Set(selectedPlayerIds);

  const renderTier = (
    title: string,
    tierPlayers: PitchPlayer[],
    badgeColor: string,
    icon: React.ReactNode,
    subtitle: string
  ) => {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            {icon}
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              {title}
            </span>
            <span className="text-[10px] font-mono text-[#8A96A3]">({tierPlayers.length})</span>
          </div>
          <span className="text-[10px] font-mono text-[#8A96A3]">{subtitle}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {tierPlayers.map((p) => {
            const isSelected = selectedSet.has(p.id);
            return (
              <div
                key={p.id}
                onClick={() => onPlayerClick?.(p)}
                className={`p-2.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? "border-[#00C853] bg-[#00C853]/10 shadow-[0_0_15px_rgba(0,200,83,0.15)]"
                    : "border-white/5 bg-[#141A22] hover:border-white/20"
                }`}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <span className="w-6 h-6 rounded bg-[#0B0F14] border border-white/10 flex items-center justify-center text-[10px] font-mono font-bold text-slate-300 shrink-0">
                    {p.role}
                  </span>
                  <div className="truncate">
                    <div className="text-xs font-bold text-white truncate">{p.name}</div>
                    <div className="text-[10px] font-mono text-[#8A96A3]">
                      {p.team} • {p.credits} Cr
                    </div>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <div className={`text-xs font-mono font-bold ${badgeColor}`}>
                    {p.predicted_ownership.toFixed(1)}%
                  </div>
                  <div className="text-[10px] font-mono text-[#8A96A3]">
                    {p.predicted_points.toFixed(0)} pts
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0B0F14] p-4 flex flex-col gap-5 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/5">
        <div>
          <h4 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
            <Users size={16} className="text-[#00C853]" />
            Public Ownership & Chalk Heatmap
          </h4>
          <p className="text-xs text-[#8A96A3]">
            Identify the crowd consensus and pivot to high-leverage differential gems.
          </p>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-[10px] font-mono">
          <span className="flex items-center gap-1 text-[#FF5252]">
            <span className="w-2 h-2 rounded-full bg-[#FF5252]" /> Danger Chalk (&ge;60%)
          </span>
          <span className="flex items-center gap-1 text-[#FFB300]">
            <span className="w-2 h-2 rounded-full bg-[#FFB300]" /> Core Middle (30-60%)
          </span>
          <span className="flex items-center gap-1 text-[#00C853]">
            <span className="w-2 h-2 rounded-full bg-[#00C853]" /> Differential (&lt;30%)
          </span>
        </div>
      </div>

      {/* Heatmap Gradient Bar */}
      <div className="w-full">
        <div className="h-2.5 rounded-full w-full bg-gradient-to-r from-[#00C853] via-[#FFB300] to-[#FF5252] shadow-inner" />
        <div className="flex justify-between text-[10px] font-mono text-[#8A96A3] mt-1">
          <span>0% (Hyper-contrarian)</span>
          <span>50% (League average)</span>
          <span>100% (Maximum chalk)</span>
        </div>
      </div>

      {/* Tiers */}
      {renderTier(
        "Chalk Danger Cluster",
        chalkTier,
        "text-[#FF5252]",
        <AlertTriangle size={14} className="text-[#FF5252]" />,
        "High crowd consensus - duplicate danger"
      )}

      {renderTier(
        "Core Field Middle",
        midTier,
        "text-[#FFB300]",
        <TrendingUp size={14} className="text-[#FFB300]" />,
        "Moderate ownership anchor plays"
      )}

      {renderTier(
        "Differential Gems",
        diffTier,
        "text-[#00C853]",
        <Sparkles size={14} className="text-[#00C853]" />,
        "Solitary first-place leverage"
      )}
    </div>
  );
};

