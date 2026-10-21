import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def roster():
    roles = ["WK", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL",
             "BOWL", "BAT", "WK"] * 2
    rows = []
    for i in range(22):
        rows.append(dict(
            player_id=f"p{i:02d}", name=f"Player {i:02d}",
            team="A" if i < 11 else "B", role=roles[i],
            credit=8.0 + (i % 4), bat_pos=(i % 11) + 1,
            overseas=(i % 5 == 0), proj=34.0 - i * 0.5,
            sd=20.0, p_dnb=0.15, own_pct=20.0 - i * 0.6,
            boom=0.1, leverage=0.0,
        ))
    return pd.DataFrame(rows)
