"""Backtesting must never train on match date or future fixtures."""
from datetime import date
import unittest
from gl_engine.capabilities.c19_backtesting import chronological_player_predictions


class ChronologicalBacktestTests(unittest.TestCase):
    def test_future_outcomes_cannot_change_pre_match_forecast(self):
        rows = [
            ("m1", date(2025, 1, 1), "Batter A", 10.0),
            ("m2", date(2025, 1, 2), "Batter A", 20.0),
            ("m3", date(2025, 1, 3), "Batter A", 30.0),
            ("target", date(2025, 1, 4), "Batter A", 99.0),
            ("same_day_other_match", date(2025, 1, 4), "Batter A", 600.0),
            ("future", date(2025, 1, 5), "Batter A", 9000.0),
        ]
        predictions, observed = chronological_player_predictions(
            rows, "target", date(2025, 1, 4)
        )
        self.assertEqual(observed, 1)
        self.assertEqual(predictions["Batter A"]["predicted_partial_points"], 20.0)
        self.assertEqual(predictions["Batter A"]["observed_partial_points"], 99.0)
        self.assertEqual(predictions["Batter A"]["prior_matches"], 3)

    def test_insufficient_history_not_imputed_as_performance(self):
        rows = [
            ("old", date(2025, 1, 1), "New Player", 2.0),
            ("target", date(2025, 1, 2), "New Player", 100.0),
        ]
        preds, observed = chronological_player_predictions(rows, "target", date(2025, 1, 2))
        self.assertEqual(preds, {})
        self.assertEqual(observed, 1)


if __name__ == "__main__":
    unittest.main()
