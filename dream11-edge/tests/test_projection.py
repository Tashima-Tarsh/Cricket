from edge.pipeline import demo_roster
from edge.model.projection_model import project_frame


def test_projections_are_sane():
    df = project_frame(demo_roster())
    assert len(df) == 22
    assert df.proj.between(1, 95).all()
    assert (df.sd > 0).all()
    assert df.p_dnb.between(0, 1).all()


def test_top_order_projects_above_tail():
    df = project_frame(demo_roster())
    assert df[df.player_id.isin(["p00","p01"])].proj.mean() > \
           df[df.player_id.isin(["p08","p10"])].proj.mean()


def test_bowlers_project_above_zero():
    df = project_frame(demo_roster())
    assert df[df.player_id.isin(["p09","p21"])].proj.min() > 8

