import React, { useState } from "react";
import { Crown, Sparkles, Shield, Zap, Info } from "lucide-react";
import { DifferentialBadge } from "./DifferentialBadge";

export interface PitchPlayer {
  id: string;
  name: string;
  role: string;
  team: string;
  credits: number;
  predicted_points: number;
  predicted_ownership: number;
  differential_score: number;
  is_captain?: boolean;
  is_vice_captain?: boolean;
}

interface PitchMapProps {
  players: PitchPlayer[];
  teamName: string;
  captainName?: string;
  viceCaptainName?: string;
}

export const PitchMap: React.FC<PitchMapProps> = ({
  players,
  teamName,
  captainName,
  viceCaptainName
}) => {
  const [selectedPlayer, setSelectedPlayer] = useState<PitchPlayer | null>(null);

  // Categorize players by role to position them logically on the cricket field
  const wks = players.filter((p) => p.role === "WK");
  const bats = players.filter((p) => p.role === "BAT");
  const ars = players.filter((p) => p.role === "AR");
  const bowls = players.filter((p) => p.role === "BOWL");

  // Coordinates on a 600x750 SVG cricket field
  const getCoordinates = (role: string, indexInRole: number, totalInRole: number) => {
    const spread = (index: number, total: number, startX: number, endX: number) => {
      if (total <= 1) return (startX + endX) / 2;
      return startX + (index / (total - 1)) * (endX - startX);
    };

    switch (role) {
      case "WK":
        return {
          x: spread(indexInRole, totalInRole, 220, 380),
          y: 110
        };
      case "BAT":
        return {
          x: spread(indexInRole, totalInRole, 110, 490),
          y: 230
        };
      case "AR":
        return {
          x: spread(indexInRole, totalInRole, 140, 460),
          y: 390
        };
      case "BOWL":
        return {
          x: spread(indexInRole, totalInRole, 90, 510),
          y: 560
        };
      default:
        return { x: 300, y: 350 };
    }
  };

  const renderPlayerNodes = (roleList: PitchPlayer[], role: string) => {
    return roleList.map((p, idx) => {
      const { x, y } = getCoordinates(role, idx, roleList.length);
      const isC = p.is_captain || p.name === captainName;
      const isVC = p.is_vice_captain || p.name === viceCaptainName;
      const isSelected = selectedPlayer?.id === p.id;
      const isHighDiff = p.predicted_ownership < 30.0;
      const isChalk = p.predicted_ownership >= 65.0;

      return (
        <g
          key={p.id || p.name}
          transform={`translate(${x}, ${y})`}
          className="cursor-pointer transition-transform duration-300 hover:scale-110"
          onClick={() => setSelectedPlayer(isSelected ? null : p)}
        >
          {/* Pulsing ring for C / VC */}
          {isC && (
            <circle
              r="26"
              fill="none"
              stroke="#FFB300"
              strokeWidth="2"
              className="animate-ping opacity-30"
            />
          )}
          {isVC && (
            <circle
              r="24"
              fill="none"
              stroke="#00E5FF"
              strokeWidth="1.5"
              className="animate-pulse opacity-40"
            />
          )}

          {/* Node Background */}
          <circle
            r="20"
            fill={isC ? "#1E1A0C" : isVC ? "#0C1B22" : "#141A22"}
            stroke={
              isC
                ? "#FFB300"
                : isVC
                ? "#00E5FF"
                : isHighDiff
                ? "#00C853"
                : isChalk
                ? "#FF5252"
                : "#2A3644"
            }
            strokeWidth={isC || isVC ? "2.5" : "1.5"}
            className="filter drop-shadow-[0_4px_10px_rgba(0,0,0,0.6)]"
          />

          {/* Role Icon / Initials */}
          <text
            y="4"
            textAnchor="middle"
            fill={isC ? "#FFB300" : isVC ? "#00E5FF" : "#E8EDF2"}
            fontSize="10"
            fontFamily="JetBrains Mono, monospace"
            fontWeight="bold"
          >
            {p.role}
          </text>

          {/* Captain / Vice Captain Badge */}
          {isC && (
            <g transform="translate(12, -14)">
              <circle r="9" fill="#FFB300" />
              <text
                y="3.5"
                textAnchor="middle"
                fill="#0B0F14"
                fontSize="9"
                fontWeight="900"
                fontFamily="sans-serif"
              >
                C
              </text>
            </g>
          )}
          {isVC && (
            <g transform="translate(12, -14)">
              <circle r="9" fill="#00E5FF" />
              <text
                y="3.5"
                textAnchor="middle"
                fill="#0B0F14"
                fontSize="8"
                fontWeight="900"
                fontFamily="sans-serif"
              >
                VC
              </text>
            </g>
          )}

          {/* Player Name Pill */}
          <g transform="translate(0, 32)">
            <rect
              x="-48"
              y="-10"
              width="96"
              height="20"
              rx="4"
              fill="#0B0F14"
              stroke={isC ? "#FFB300" : isVC ? "#00E5FF" : "#2A3644"}
              strokeWidth="0.75"
              fillOpacity="0.92"
            />
            <text
              y="3"
              textAnchor="middle"
              fill="#E8EDF2"
              fontSize="9"
              fontFamily="Inter, sans-serif"
              fontWeight="600"
            >
              {p.name.length > 13 ? p.name.substring(0, 12) + "…" : p.name}
            </text>
          </g>

          {/* Quick Metrics Bar below Name */}
          <g transform="translate(0, 48)">
            <text
              textAnchor="middle"
              fill={isHighDiff ? "#00C853" : isChalk ? "#FF5252" : "#8A96A3"}
              fontSize="7.5"
              fontFamily="JetBrains Mono, monospace"
              fontWeight="bold"
            >
              {p.predicted_points.toFixed(0)} pts • {p.predicted_ownership.toFixed(0)}% own
            </text>
          </g>
        </g>
      );
    });
  };

  return (
    <div className="relative w-full rounded-2xl border border-white/10 bg-[#0B0F14] p-4 overflow-hidden shadow-2xl flex flex-col items-center">
      {/* Header bar */}
      <div className="w-full flex items-center justify-between pb-3 border-b border-white/5 z-10 mb-2">
        <div>
          <span className="text-xs font-mono text-[#00C853] uppercase tracking-wider font-bold">
            Tactical Pitch Formation
          </span>
          <h4 className="text-sm font-bold text-white tracking-tight">{teamName}</h4>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#FFB300]/15 border border-[#FFB300]/30 text-[#FFB300] font-bold">
            C: {captainName?.split(" ").pop() || "Captain"} (2x)
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 font-bold">
            VC: {viceCaptainName?.split(" ").pop() || "Vice Captain"} (1.5x)
          </span>
        </div>
      </div>

      {/* SVG Cricket Field */}
      <div className="relative w-full max-w-[540px] aspect-[4/5]">
        <svg
          viewBox="0 0 600 750"
          className="w-full h-full select-none"
        >
          <defs>
            <radialGradient id="fieldGrass" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#14261B" />
              <stop offset="70%" stopColor="#0F1E16" />
              <stop offset="100%" stopColor="#0A140E" />
            </radialGradient>
            <linearGradient id="pitchStrip" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3E3424" />
              <stop offset="50%" stopColor="#4A3F2C" />
              <stop offset="100%" stopColor="#3E3424" />
            </linearGradient>
          </defs>

          {/* Outer Boundary Oval */}
          <ellipse
            cx="300"
            cy="375"
            rx="280"
            ry="350"
            fill="url(#fieldGrass)"
            stroke="#1D3827"
            strokeWidth="3"
            strokeDasharray="8 4"
          />

          {/* 30-Yard Circle */}
          <ellipse
            cx="300"
            cy="375"
            rx="190"
            ry="235"
            fill="none"
            stroke="#2E543A"
            strokeWidth="1.5"
            strokeDasharray="5 3"
            opacity="0.6"
          />

          {/* 22-Yard Pitch Strip */}
          <rect
            x="272"
            y="285"
            width="56"
            height="180"
            rx="4"
            fill="url(#pitchStrip)"
            stroke="#63543A"
            strokeWidth="1"
            opacity="0.85"
          />

          {/* Crease markings */}
          <line x1="265" y1="315" x2="335" y2="315" stroke="#FFFFFF" strokeWidth="1" opacity="0.4" />
          <line x1="265" y1="435" x2="335" y2="435" stroke="#FFFFFF" strokeWidth="1" opacity="0.4" />
          <rect x="290" y="300" width="20" height="4" fill="#E8EDF2" opacity="0.6" />
          <rect x="290" y="446" width="20" height="4" fill="#E8EDF2" opacity="0.6" />

          {/* Role Zone Guide Labels */}
          <text x="300" y="55" textAnchor="middle" fill="#8A96A3" fontSize="10" fontFamily="JetBrains Mono" opacity="0.4">
            WICKET-KEEPERS
          </text>
          <text x="300" y="195" textAnchor="middle" fill="#8A96A3" fontSize="10" fontFamily="JetBrains Mono" opacity="0.4">
            TOP & MIDDLE ORDER
          </text>
          <text x="300" y="360" textAnchor="middle" fill="#8A96A3" fontSize="10" fontFamily="JetBrains Mono" opacity="0.4">
            ALL-ROUNDER ROTATION
          </text>
          <text x="300" y="515" textAnchor="middle" fill="#8A96A3" fontSize="10" fontFamily="JetBrains Mono" opacity="0.4">
            BOWLING UNIT
          </text>

          {/* Render Player Nodes */}
          {renderPlayerNodes(wks, "WK")}
          {renderPlayerNodes(bats, "BAT")}
          {renderPlayerNodes(ars, "AR")}
          {renderPlayerNodes(bowls, "BOWL")}
        </svg>
      </div>

      {/* Selected Player Detail Card (Modal / Popover) */}
      {selectedPlayer && (
        <div className="w-full mt-3 p-3 rounded-xl border border-white/10 bg-[#141A22] flex items-center justify-between animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#0B0F14] border border-white/10 flex items-center justify-center font-mono font-bold text-sm text-[#00C853]">
              {selectedPlayer.role}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">{selectedPlayer.name}</span>
                <span className="text-xs font-mono text-[#8A96A3]">({selectedPlayer.team})</span>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono text-[#8A96A3]">
                <span>Credits: <strong className="text-white">{selectedPlayer.credits}</strong></span>
                <span>Exp: <strong className="text-white">{selectedPlayer.predicted_points.toFixed(1)} pts</strong></span>
                <span>Diff: <strong className="text-[#FFB300]">{selectedPlayer.differential_score.toFixed(2)}</strong></span>
              </div>
            </div>
          </div>
          <DifferentialBadge ownershipPct={selectedPlayer.predicted_ownership} size="sm" />
        </div>
      )}
    </div>
  );
};

