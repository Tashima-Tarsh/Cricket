from edge.score import BatLine, BowlLine, FieldLine, points, sr_bonus


def test_fifty_with_good_sr():
    # 50 runs + 5 fours + 2 sixes = 59 boundary/run points
    # sr 166.7 -> +4 ; r50 -> +8
    p = points(BatLine(runs=50, balls=30, fours=5, sixes=2), BowlLine(), FieldLine())
    assert p == 50 + 5 + 4 + 4 + 8


def test_duck_penalty():
    assert points(BatLine(runs=0, balls=4, out=True), BowlLine(), FieldLine()) == -2.0


def test_wicket_haul():
    # 4w*30=120 ; 2 lbw*8=16 ; w4 bonus=8 ; eco 20/4ov=5.0 -> +6
    p = points(BatLine(batted=False),
               BowlLine(balls=24, runs=20, wickets=4, lbw_bowled=2), FieldLine())
    assert p == 120 + 16 + 8 + 6


def test_floor_holds():
    p = points(BatLine(runs=0, balls=12, out=True),
               BowlLine(balls=120, runs=48), FieldLine())
    assert p >= -6.0


def test_sr_gate_below_ten_balls():
    a = points(BatLine(runs=6, balls=5, fours=1), BowlLine(), FieldLine())
    assert a == 7.0  # no sr bonus under 10 balls


def test_catches_bonus():
    p = points(BatLine(batted=False), BowlLine(), FieldLine(catches=3))
    assert p == 24 + 4


def test_strike_rate_parity_and_no_penalty_at_100():
    # SR = 100 on 20 balls: NO penalty, NO bonus
    assert sr_bonus(20, 20) == 0.0
    # SR = 80 on 20 balls (16 runs): within 70-129.99 -> 0.0
    assert sr_bonus(16, 20) == 0.0
    # SR = 65 on 20 balls (13 runs): within 60-69.99 -> -2.0
    assert sr_bonus(13, 20) == -2.0
    # SR = 55 on 20 balls (11 runs): within 50-59.99 -> -4.0
    assert sr_bonus(11, 20) == -4.0
    # SR = 40 on 20 balls (8 runs): under 50 -> -6.0
    assert sr_bonus(8, 20) == -6.0


def test_dot_balls_and_starting_xi():
    # Bowler with 12 dot balls and in starting XI
    p = points(
        BatLine(batted=False),
        BowlLine(balls=24, runs=18, wickets=2, dots=12),
        FieldLine(),
        is_xi=True
    )
    # is_xi (+4) + 2 wkts (60) + 12 dots (12) + eco 18/4ov=4.5 (+6) = 82
    assert p == 4.0 + 60.0 + 12.0 + 6.0
