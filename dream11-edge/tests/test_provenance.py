import numpy as np
from unittest.mock import patch
from edge.optimize.constraints import Ctx, repair
from edge.optimize.portfolio import build


def test_generated_portfolio_has_provenance(roster):
    ctx = Ctx.from_frame(roster)
    rng = np.random.default_rng(7)
    sims = rng.normal(35, 8, (30, len(ctx.ids)))
    idx = {player: i for i, player in enumerate(ctx.ids)}
    squad = repair(ctx.ids[:11], ctx, rng)
    # Isolate portfolio serialization from the optional external MILP solver.
    with patch("edge.optimize.portfolio.solve_core", return_value=(squad, squad[0], squad[1])):
        portfolio = build(ctx, sims, idx, np.zeros((3, 30)), 1, rng)
    assert portfolio
    assert portfolio[0]['provenance']['verification_status'] == 'SIMULATION'
