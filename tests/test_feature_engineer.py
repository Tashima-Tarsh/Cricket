"""Legacy (demo-only) BBLFeatureEngineer interfaces; not production WBBL scoring."""
import pandas as pd
from feature_engineer import BBLFeatureEngineer


def balls():
    return pd.DataFrame([
        dict(match_id="m1",date="2024-01-01",innings=1,over=1,ball=1,
             batter="Example Batter",bowler="Example Bowler",
             batting_team="Sydney Sixers",bowling_team="Sydney Thunder",
             runs_batter=4,runs_total=4,is_wicket=0),
        dict(match_id="m2",date="2024-01-02",innings=1,over=2,ball=2,
             batter="Example Batter",bowler="Example Bowler",
             batting_team="Sydney Sixers",bowling_team="Sydney Thunder",
             runs_batter=1,runs_total=1,is_wicket=0)
    ])


def test_current_feature_engineer_produces_explicit_demo_frame():
    engine=BBLFeatureEngineer()
    frame=engine.build_ml_features(balls(),upcoming_players=[])
    assert not frame.empty
    assert {"player","fantasy_points","skill_rating","recent_form_last_5"}.issubset(frame.columns)


def test_unknown_venue_does_not_modify_recorded_scores():
    eng=BBLFeatureEngineer()
    frame=pd.DataFrame([{"role":"BAT","venue":"Unregistered venue",
                         "fantasy_points":22,"strike_rate":100}])
    out=eng.add_venue_quirks(frame)
    assert float(out.iloc[0]["fantasy_points"])==22.


def test_travel_fatigue_requires_long_bowler_route():
    eng=BBLFeatureEngineer()
    frame=pd.DataFrame([{"role":"BOWL","bowling_style":"right-arm fast",
                         "fantasy_points":40.0}])
    out=eng.add_travel_fatigue(frame,"MCG","SCG")
    assert out.iloc[0]["fantasy_points"]==40.0
