"""Unit and integration contract tests for Canonical Provider Architecture."""
import unittest
import time
from gl_engine.providers.canonical_provider import (
    CanonicalFixture,
    CanonicalXI,
    CanonicalXIPlayer,
    CircuitBreaker,
    TokenBucketRateLimiter,
    BaseCanonicalAdapter,
    CrossProviderVerifier,
)


class TestCanonicalProvider(unittest.TestCase):
    def test_circuit_breaker_transitions(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.allow_request())

        # Record 2 failures -> remains CLOSED
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, "CLOSED")

        # 3rd failure -> trips to OPEN
        cb.record_failure()
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.allow_request())

        # Wait for recovery timeout
        time.sleep(0.25)
        self.assertTrue(cb.allow_request())
        self.assertEqual(cb.state, "HALF_OPEN")

        # Success resets to CLOSED
        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")

    def test_rate_limiter_budget(self):
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_sec=1.0)
        self.assertTrue(limiter.acquire(1))
        self.assertTrue(limiter.acquire(1))
        # Depleted
        self.assertFalse(limiter.acquire(1))

    def test_resilient_executor_retries_and_succeeds(self):
        adapter = BaseCanonicalAdapter(name="TestProvider", max_retries=3)
        attempts = 0

        def flaky_call():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ConnectionError("Transient network failure")
            return {"status": "SUCCESS", "data": 42}

        res = adapter.execute_with_resilience(flaky_call)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(attempts, 2)
        self.assertEqual(adapter.circuit_breaker.state, "CLOSED")

    def test_cross_provider_verifier_corroborates_matching_xis(self):
        players_h = [CanonicalXIPlayer(name=f"Home P{i}", team="HOME") for i in range(11)]
        players_a = [CanonicalXIPlayer(name=f"Away P{i}", team="AWAY") for i in range(11)]

        xi1 = CanonicalXI(
            provider="Sportmonks",
            provider_fixture_id="sm_123",
            home_team="Home Team",
            away_team="Away Team",
            home_xi=players_h,
            away_xi=players_a,
            is_fully_confirmed=True
        )
        xi2 = CanonicalXI(
            provider="CricketData",
            provider_fixture_id="cd_456",
            home_team="Home Team",
            away_team="Away Team",
            home_xi=list(reversed(players_h)),  # order independent
            away_xi=list(players_a),
            is_fully_confirmed=True
        )

        res = CrossProviderVerifier.verify_xis(xi1, xi2)
        self.assertEqual(res["status"], "CROSS_PROVIDER_CORROBORATED")
        self.assertEqual(res["confirmed_count"], 22)
        self.assertIn("Sportmonks", res["providers"])
        self.assertIn("CricketData", res["providers"])

    def test_cross_provider_verifier_rejects_mismatch(self):
        players_h = [CanonicalXIPlayer(name=f"Home P{i}", team="HOME") for i in range(11)]
        players_a1 = [CanonicalXIPlayer(name=f"Away P{i}", team="AWAY") for i in range(11)]
        players_a2 = [CanonicalXIPlayer(name=f"Away P{i}", team="AWAY") for i in range(10)] + [
            CanonicalXIPlayer(name="Unmatched Sub", team="AWAY")
        ]

        xi1 = CanonicalXI(
            provider="Sportmonks",
            provider_fixture_id="sm_123",
            home_team="Home Team",
            away_team="Away Team",
            home_xi=players_h,
            away_xi=players_a1,
        )
        xi2 = CanonicalXI(
            provider="CricketData",
            provider_fixture_id="cd_456",
            home_team="Home Team",
            away_team="Away Team",
            home_xi=players_h,
            away_xi=players_a2,
        )

        with self.assertRaises(ValueError) as ctx:
            CrossProviderVerifier.verify_xis(xi1, xi2)
        self.assertIn("Away XI discrepancy", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
