import React from "react";
import { ArrowLeftRight } from "lucide-react";
import { PitchPlayer } from "./PitchMap";

interface TeamSnapshot {
  name: string;
  captain: string;
  vice_captain: string;
  crowd_overlap_pct: number;
  projected_points: number;
  rank_1_probability_pct: number | null;
  total_credits: number;
  players: PitchPlayer[];
}

interface TeamCompareProps {
  uniqueTeam: TeamSnapshot;
  chalkTeam?: TeamSnapshot;
}

export const TeamCompare: React.FC<TeamCompareProps> = ({ uniqueTeam, chalkTeam }) => {
  const otherNames = new Set(chalkTeam?.players.map((p) => p.id) ?? []);
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0B0F14] p-5 shadow-2xl flex flex-col gap-5">
      <h4 className="text-sm font-bold text-white flex items-center gap-2">
        <ArrowLeftRight size={16} className="text-[#FFB300]" />
        Team comparison · evidence-first
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[uniqueTeam, chalkTeam].map((team, index) => (
          <div key={index} className="rounded-xl border border-white/10 bg-[#141A22] p-4">
            {team ? (
              <>
                <h5 className="text-white font-bold">{team.name}</h5>
                <p className="text-xs text-[#8A96A3] mt-2">Captain: {team.captain}</p>
                <p className="text-xs text-[#8A96A3]">Vice-captain: {team.vice_captain}</p>
                <p className="text-xs text-[#8A96A3]">Credits spent: {team.total_credits.toFixed(1)}</p>
                <p className="text-xs text-[#8A96A3]">Rank-1 probability: {team.rank_1_probability_pct == null ? "Not calibrated" : `${team.rank_1_probability_pct}%`}</p>
                <p className="text-xs text-[#8A96A3]">Ownership sum: {team.crowd_overlap_pct.toFixed(1)}% (estimate, not duplication probability)</p>
              </>
            ) : (
              <>
                <h5 className="text-white font-bold">Opposing field not available</h5>
                <p className="text-xs text-[#8A96A3] mt-2">
                  Provide an observed comparison lineup. We do not fabricate a public
                  chalk team, opponent ownership or contest win probabilities.
                </p>
              </>
            )}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {uniqueTeam.players.map((p) => (
          <div key={p.id} className="p-2 border border-white/10 rounded bg-[#141A22] text-xs">
            <span className="font-bold text-white">{p.name}</span>
            <span className="text-[#8A96A3] ml-2">{p.role} · {p.team}</span>
            {chalkTeam && <span className="block text-[#8A96A3]">{otherNames.has(p.id) ? "Shared pick" : "Unique pick"}</span>}
          </div>
        ))}
      </div>
    </div>
  );
};
