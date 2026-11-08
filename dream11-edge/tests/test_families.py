"""Verify empirical families fitting and serialization in dream11-edge."""
from pathlib import Path
import pickle
from edge.model.distributions import Family


def test_empirical_families_pkl_structure():
    fam_path = Path(__file__).parent.parent / "artifacts" / "families.pkl"
    if not fam_path.exists():
        return
    with open(fam_path, "rb") as fh:
        families = pickle.load(fh)
    assert len(families) >= 20
    for role in ["BAT", "BOWL", "AR", "WK"]:
        assert (role, 0) in families
        assert (role, 30) in families
        fam = families[(role, 0)]
        assert isinstance(fam, Family)
        assert fam.name in ("gamma", "lognormal", "weibull", "skewnorm", "exgaussian")
        assert fam.ks < 0.25
