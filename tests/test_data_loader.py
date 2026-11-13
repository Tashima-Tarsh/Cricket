"""Current data-loader behavior: explicit synthetic demo vs fail-closed real data."""
from tempfile import TemporaryDirectory
import pandas as pd
from unittest.mock import patch
from data_loader import CricsheetLoader, generate_sample_bbl_data


def test_explicit_demo_data_is_repeatable():
    a = generate_sample_bbl_data(n_matches=3)
    b = generate_sample_bbl_data(n_matches=3)
    assert not a.empty
    pd.testing.assert_frame_equal(a,b)
    assert {"match_id","batter","bowler","runs_batter","is_wicket"}.issubset(a.columns)


def test_real_data_loader_never_falls_back_to_demo():
    with TemporaryDirectory() as tmp:
        loader=CricsheetLoader(cache_dir=tmp)
        with patch.object(loader,"fetch_zip",return_value=None):
            result=loader.load_bbl_data()
        assert result.empty


def test_only_explicit_opt_in_allows_demo():
    with TemporaryDirectory() as tmp:
        loader=CricsheetLoader(cache_dir=tmp)
        with patch.object(loader,"fetch_zip",return_value=None):
            result=loader.load_bbl_data(max_matches=2,use_synthetic_fallback=True)
        assert not result.empty
