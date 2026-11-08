import React from "react";
import { Sparkles, AlertTriangle, ShieldCheck } from "lucide-react";

interface DifferentialBadgeProps {
  ownershipPct: number;
  differentialScore?: number;
  size?: "sm" | "md" | "lg";
}

export const DifferentialBadge: React.FC<DifferentialBadgeProps> = ({
  ownershipPct,
  differentialScore,
  size = "md"
}) => {
  const isDangerChalk = ownershipPct >= 65.0;
  const isHighDifferential = ownershipPct < 30.0;
  const isModerate = !isDangerChalk && !isHighDifferential;

  const sizeClasses = {
    sm: "px-1.5 py-0.5 text-[10px]",
    md: "px-2 py-0.8 text-xs",
    lg: "px-2.5 py-1 text-xs font-bold"
  }[size];

  if (isHighDifferential) {
    return (
      <span
        title="High Differential Edge: Only a fraction of the crowd owns this player!"
        className={`inline-flex items-center gap-1 rounded-full border border-[#FFB300]/40 bg-[#FFB300]/15 text-[#FFB300] font-mono tracking-tight ${sizeClasses}`}
      >
        <Sparkles size={size === "sm" ? 10 : 12} className="text-[#FFB300] animate-pulse" />
        <span>Only {ownershipPct.toFixed(1)}% own this pick</span>
      </span>
    );
  }

  if (isDangerChalk) {
    return (
      <span
        title="High-ownership danger: Massively chalky! Failure causes widespread bust, but wins split prize."
        className={`inline-flex items-center gap-1 rounded-full border border-[#FF5252]/40 bg-[#FF5252]/15 text-[#FF5252] font-mono tracking-tight ${sizeClasses}`}
      >
        <AlertTriangle size={size === "sm" ? 10 : 12} className="text-[#FF5252]" />
        <span>everyone owns this ({ownershipPct.toFixed(1)}%)</span>
      </span>
    );
  }

  return (
    <span
      title="Balanced leverage"
      className={`inline-flex items-center gap-1 rounded-full border border-[#00C853]/30 bg-[#00C853]/10 text-[#00C853] font-mono tracking-tight ${sizeClasses}`}
    >
      <ShieldCheck size={size === "sm" ? 10 : 12} className="text-[#00C853]" />
      <span>your edge ({ownershipPct.toFixed(1)}%)</span>
    </span>
  );
};

