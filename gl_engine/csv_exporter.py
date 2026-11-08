"""Enterprise CSV & Bulk Lineup Exporters for Dream11 and My11Circle.
Formats OR-Tools generated multi-lineup portfolios into standard Dream11 & My11Circle
bulk upload specifications for instant 1-click contest entry.
"""

from typing import List, Dict, Any
import csv
import io
from .models import Lineup

class BulkPlatformExporter:
    """Generates 1-click bulk CSV files formatted strictly for major fantasy platforms."""

    @staticmethod
    def export_dream11_csv(lineups: List[Lineup]) -> str:
        """Exports lineups matching official Dream11 bulk roster template.
        Columns: Team, Player 1..11, Captain, Vice Captain, Total Credits, Combined Ownership %
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            "Team",
            "Player 1", "Player 2", "Player 3", "Player 4", "Player 5",
            "Player 6", "Player 7", "Player 8", "Player 9", "Player 10", "Player 11",
            "Captain", "Vice Captain", "Total Credits", "CSP %"
        ]
        writer.writerow(headers)

        for idx, lineup in enumerate(lineups, start=1):
            p_names = [p.name for p in lineup.players]
            # Ensure exactly 11 names
            while len(p_names) < 11:
                p_names.append("")
            
            c_name = lineup.captain.name if lineup.captain else ""
            vc_name = lineup.vice_captain.name if lineup.vice_captain else ""
            credits_val = round(lineup.total_credits, 1)
            csp_val = round(lineup.csp or lineup.total_ownership_sum, 1)

            row = [f"Team {idx}"] + p_names[:11] + [c_name, vc_name, credits_val, csp_val]
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def export_my11circle_csv(lineups: List[Lineup]) -> str:
        """Exports lineups matching My11Circle multi-entry CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Team_ID", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11",
            "C", "VC", "Credits", "Selection_Sum"
        ]
        writer.writerow(headers)

        for idx, lineup in enumerate(lineups, start=1):
            p_names = [p.name for p in lineup.players]
            while len(p_names) < 11:
                p_names.append("")
            
            c_name = lineup.captain.name if lineup.captain else ""
            vc_name = lineup.vice_captain.name if lineup.vice_captain else ""

            row = [
                f"T{idx}",
                p_names[0], p_names[1], p_names[2], p_names[3], p_names[4],
                p_names[5], p_names[6], p_names[7], p_names[8], p_names[9], p_names[10],
                c_name, vc_name, round(lineup.total_credits, 1), round(lineup.csp or lineup.total_ownership_sum, 1)
            ]
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def export_syndicate_json(lineups: List[Lineup]) -> List[Dict[str, Any]]:
        """Exports rich quantitative syndicate summary with exposure counts and risk telemetry."""
        exposure_map: Dict[str, int] = {}
        c_exposure_map: Dict[str, int] = {}
        vc_exposure_map: Dict[str, int] = {}
        total = len(lineups) or 1

        for l in lineups:
            for p in l.players:
                exposure_map[p.name] = exposure_map.get(p.name, 0) + 1
            if l.captain:
                c_exposure_map[l.captain.name] = c_exposure_map.get(l.captain.name, 0) + 1
            if l.vice_captain:
                vc_exposure_map[l.vice_captain.name] = vc_exposure_map.get(l.vice_captain.name, 0) + 1

        return {
            "total_lineups": len(lineups),
            "player_exposures": {
                name: {"count": cnt, "pct": round((cnt / total) * 100.0, 1)}
                for name, cnt in sorted(exposure_map.items(), key=lambda x: x[1], reverse=True)
            },
            "captain_exposures": {
                name: {"count": cnt, "pct": round((cnt / total) * 100.0, 1)}
                for name, cnt in sorted(c_exposure_map.items(), key=lambda x: x[1], reverse=True)
            },
            "vice_captain_exposures": {
                name: {"count": cnt, "pct": round((cnt / total) * 100.0, 1)}
                for name, cnt in sorted(vc_exposure_map.items(), key=lambda x: x[1], reverse=True)
            }
        }
