from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class SimCfg:
    n_sims: int = 20000
    n_sims_ball: int = 2000
    n_field: int = 100000
    n_entries: int = 150
    engine: str = "marginal"


@dataclass(frozen=True)
class PortfolioCfg:
    max_exposure: float = 0.65
    min_swap: int = 3
    unique_cvc: bool = True
    jitter: float = 0.03


@dataclass(frozen=True)
class RelockCfg:
    min_edge: float = 0.02
    freeze_minutes: int = 3


@dataclass(frozen=True)
class ModelCfg:
    form_halflife_days: int = 120
    matchup_min_balls: int = 60
    shrink_prior_obs: int = 200
    window_edges: tuple = (0, 15, 30, 50, 75, 10**9)


@dataclass(frozen=True)
class Settings:
    root: Path
    data_dir: Path
    web_dir: Path
    artifacts: Path
    db_path: Path
    sim: SimCfg
    portfolio: PortfolioCfg
    relock: RelockCfg
    model: ModelCfg
    rules: dict
    venues: dict
    tz: str

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.web_dir, self.artifacts):
            d.mkdir(parents=True, exist_ok=True)


def _tupleise(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        out[k] = tuple(v) if isinstance(v, list) else v
    return out


@lru_cache(maxsize=1)
def settings() -> Settings:
    s = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text())
    rules = yaml.safe_load((ROOT / "config" / "rules.yaml").read_text())
    venues = yaml.safe_load((ROOT / "config" / "venues.yaml").read_text())
    paths = s.get("paths", {})
    data_dir = ROOT / paths.get("data", "data")
    return Settings(
        root=ROOT,
        data_dir=data_dir,
        web_dir=ROOT / paths.get("web", "web"),
        artifacts=ROOT / paths.get("artifacts", "artifacts"),
        db_path=data_dir / "edge.duckdb",
        sim=SimCfg(**s.get("sim", {})),
        portfolio=PortfolioCfg(**s.get("portfolio", {})),
        relock=RelockCfg(**s.get("relock", {})),
        model=ModelCfg(**_tupleise(s.get("model", {}))),
        rules=rules,
        venues=venues,
        tz=os.getenv("EDGE_TZ", "Asia/Kolkata"),
    )
