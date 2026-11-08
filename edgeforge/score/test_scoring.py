"""Golden tests against official Dream11 T20 table (dream11.com)."""
from edgeforge.score.dream11 import Dream11Scorer


def test_boundary_and_six_bonuses():
    s = Dream11Scorer()
    r = s.calculate(runs=40, balls_faced=30, fours=4, sixes=2, is_playing=True)
    # XI (4) + runs (40) + 4s bonus (4*1) + 6s bonus (2*2) + milestone 30+ (4) + SR 133.3 (2) = 58
    assert r.total == 58.0, r.total


def test_wicket_and_dot():
    s = Dream11Scorer()
    r = s.calculate(
        wickets=2, bowled_lbw=1, dots=8, overs_bowled=4.0, runs_conceded=24,
        is_playing=True,
    )
    # XI (4) + 2 wkts (60) + 1 bowled/lbw (8) + 8 dots (8) + eco 6.0 (4) = 84
    assert r.total == 84.0, r.total


def test_milestone_highest_only():
    s = Dream11Scorer()
    r = s.calculate(runs=100, balls_faced=55, fours=8, sixes=4, is_playing=True)
    # 100 runs + 8 4s-bonus + 8 6s-bonus + 16 century + 6 SR = 138 batting
    assert r.breakdown["batting"] == 100 + 8 + 8 + 16 + 6
    assert r.total == 100 + 8 + 8 + 16 + 6 + 4


def test_sr_no_penalty_at_100():
    s = Dream11Scorer()
    r = s.calculate(runs=20, balls_faced=20, is_playing=False)
    assert r.total == 20.0


if __name__ == "__main__":
    test_boundary_and_six_bonuses()
    test_wicket_and_dot()
    test_milestone_highest_only()
    test_sr_no_penalty_at_100()
    print("all golden scoring tests passed")
