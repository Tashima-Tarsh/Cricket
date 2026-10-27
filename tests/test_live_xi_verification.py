"""No offline/mock or squad-only record can masquerade as confirmed XI."""
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from gl_engine.live_xi_verification import compare_independent_xis, verify_live_xi
from gl_engine.providers.sportmonks_api import SportmonksCricketClient
from gl_engine.cricketdata_api import CricketDataClient


def samples():
    sportmonks = {
        "status": "LIVE_PROVIDER_RESPONSE", "home_team": "Alpha",
        "away_team": "Bravo", "playing_xi": {
            team: [
                {"name": f"{team} Player {i}", "lineup_status": True}
                for i in range(11)
            ] for team in ("home", "away")
        },
    }
    # provider player identities map to the same team name, not generic home/away
    cricketdata = {"teams": {
        team: {"playing_xi": [
            {"name": f"{side} Player {i}"} for i in range(11)
        ]} for team, side in (("Alpha", "home"), ("Bravo", "away"))
    }}
    return sportmonks, cricketdata


class LiveXiVerificationTests(unittest.TestCase):
    def test_agreeing_confirmed_xis(self):
        sm, cd = samples()
        report = compare_independent_xis(sm, cd)
        self.assertEqual(report["count"], 22)
        self.assertEqual(report["status"], "CROSS_PROVIDER_CORROBORATED")

    def test_squad_only_not_confirmation(self):
        sm, cd = samples()
        for team in cd["teams"].values():
            team["squad"] = team.pop("playing_xi")
        with self.assertRaises(ValueError):
            compare_independent_xis(sm, cd)

    def test_mismatched_players_fail_closed(self):
        sm, cd = samples()
        cd["teams"]["Alpha"]["playing_xi"][1]["name"] = "Replacement"
        with self.assertRaises(ValueError):
            compare_independent_xis(sm, cd)

    def test_sportmonks_unconfirmed_status_is_rejected(self):
        sm, cd = samples()
        sm["playing_xi"]["home"][0]["lineup_status"] = False
        with self.assertRaises(ValueError):
            compare_independent_xis(sm, cd)

    def test_missing_provider_credentials_fail_closed(self):
        with patch("gl_engine.live_xi_verification.SportmonksCricketClient") as a, patch(
            "gl_engine.live_xi_verification.CricketDataClient"
        ) as b:
            a.return_value.is_live = False
            b.return_value.is_live = False
            with self.assertRaises(HTTPException) as error:
                verify_live_xi(sportmonks_fixture_id="1", cricketdata_match_id="2")
            self.assertEqual(error.exception.status_code, 503)

    def test_offline_clients_do_not_return_fake_live_data(self):
        self.assertEqual(SportmonksCricketClient(api_token="MOCK_TOKEN").get_livescores(), [])
        self.assertEqual(SportmonksCricketClient(api_token="MOCK_TOKEN").get_fixture_details("fixture"), {})
        self.assertEqual(CricketDataClient(api_key="MOCK_KEY").get_current_matches(), [])


if __name__ == "__main__":
    unittest.main()
