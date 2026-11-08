"""
Correlation matrix for BBL/WBBL fantasy cricket.
Computes real bowler-batter dismissal relationships and batting partnerships
from ball-by-ball data. These drive the Grand League correlation constraints:
  - Negative correlation (Block): a bowler who dismisses a batter often
    should not be Captain with that batter as Vice-Captain.
  - Positive correlation (Stack): batting partnerships amplify each other.
"""
import json
import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import pandas as pd


class CorrelationMatrix:
    def __init__(self, balls_df: pd.DataFrame):
        self.balls_df = balls_df.copy()
        # bowler_name -> {batter_name: dismissal_count}
        self.bowler_batter_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # batter_name -> {partner_name: balls_faced_together}
        self.partnership_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._build()

    def _build(self) -> None:
        if self.balls_df.empty:
            return

        df = self.balls_df.copy()

        # Negative correlation: bowler dismisses batter
        if "is_wicket" in df.columns and "bowler" in df.columns and "batter" in df.columns:
            wickets = df[df["is_wicket"].astype(int) == 1]
            for _, row in wickets.iterrows():
                bowler = str(row["bowler"]).strip()
                batter = str(row["batter"]).strip()
                if bowler and batter and bowler != batter:
                    self.bowler_batter_matrix[bowler][batter] += 1

        # Positive correlation: batting partnerships (same batter + non-striker in same over)
        if "batter" in df.columns and "non_striker" in df.columns and "match_id" in df.columns and "over" in df.columns:
            for (match_id, innings, over), group in df.groupby(["match_id", "innings", "over"]):
                batters = set()
                for _, row in group.iterrows():
                    b1 = str(row["batter"]).strip()
                    b2 = str(row["non_striker"]).strip()
                    if b1:
                        batters.add(b1)
                    if b2:
                        batters.add(b2)
                batters = sorted(batters)
                for i in range(len(batters)):
                    for j in range(i + 1, len(batters)):
                        b1, b2 = batters[i], batters[j]
                        self.partnership_matrix[b1][b2] += 1
                        self.partnership_matrix[b2][b1] += 1

    def get_negative_correlations(self, bowler_name: str) -> List[str]:
        """Return batters dismissed by this bowler, sorted by dismissal count desc."""
        if bowler_name not in self.bowler_batter_matrix:
            return []
        rels = self.bowler_batter_matrix[bowler_name]
        return sorted(rels.keys(), key=lambda b: rels[b], reverse=True)

    def get_positive_correlations(self, batter_name: str) -> List[str]:
        """Return batting partners of this batter, sorted by partnership strength desc."""
        if batter_name not in self.partnership_matrix:
            return []
        rels = self.partnership_matrix[batter_name]
        return sorted(rels.keys(), key=lambda p: rels[p], reverse=True)

    def dismissal_count(self, bowler_name: str, batter_name: str) -> int:
        return int(self.bowler_batter_matrix.get(bowler_name, {}).get(batter_name, 0))

    def partnership_count(self, batter_a: str, batter_b: str) -> int:
        return int(self.partnership_matrix.get(batter_a, {}).get(batter_b, 0))

    def summary(self) -> Dict[str, int]:
        return {
            "bowler_batter_rivalries": len(self.bowler_batter_matrix),
            "total_dismissal_edges": sum(len(v) for v in self.bowler_batter_matrix.values()),
            "partnerships": len(self.partnership_matrix),
            "total_partnership_edges": sum(len(v) for v in self.partnership_matrix.values()),
        }

    def save(self, path: str = "correlation_matrix.json") -> None:
        data = {
            "bowler_batter": {k: dict(v) for k, v in self.bowler_batter_matrix.items()},
            "partnership": {k: dict(v) for k, v in self.partnership_matrix.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
