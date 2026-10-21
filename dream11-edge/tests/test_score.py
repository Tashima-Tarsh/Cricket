from edge.score import BatLine, BowlLine, FieldLine, points


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
