"""Chronological model features exclude same-day and future matches."""
from datetime import date
import unittest
from gl_engine.model_validation import build_historical_feature_rows, evaluate_historical_rows


class PredictionValidationTests(unittest.TestCase):
    def test_future_and_same_day_not_in_model_features(self):
        d = date
        rows = [
            ("a", d(2025, 1, 1), "Player A", 10),
            ("b", d(2025, 1, 2), "Player A", 20),
            ("c", d(2025, 1, 3), "Player A", 30),
            ("target", d(2025, 1, 4), "Player A", 40),
            ("other_same_date", d(2025, 1, 4), "Player A", 9000),
            ("future", d(2025, 1, 5), "Player A", 9999),
        ]
        features = build_historical_feature_rows(rows)
        item = next(r for r in features if r["match_id"] == "target")
        self.assertEqual(item["features"][0], 20)
        self.assertEqual(item["history_count"], 3)
        self.assertLess(item["latest_input_date"], item["date"])

    def test_no_fabricated_skill_for_insufficient_history(self):
        rows = [("a", date(2025, 1, 1), "P", 10),
                ("b", date(2025, 1, 2), "P", 20)]
        result = evaluate_historical_rows(rows)
        self.assertEqual(result["status"], "INSUFFICIENT_HISTORY")
        self.assertFalse(result["contest_probability_calibrated"])


if __name__ == "__main__":
    unittest.main()
