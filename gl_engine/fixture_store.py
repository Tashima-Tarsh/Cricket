"""Validated custom fixtures in a local SQLite store. No inferred playing XIs."""
import json
import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FixturePlayer(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    name: str = Field(min_length=1, max_length=100)
    role: Literal["WK", "BAT", "AR", "BOWL"]
    credits: float = Field(gt=0, le=20)
    order: int = Field(ge=1, le=11)
    bat_hand: Literal["RHB", "LHB"]
    bowl_style: str = Field(max_length=100)
    projected_ownership: float | None = Field(default=None, ge=0, le=100)
    expected_overs: float | None = Field(default=None, ge=0, le=10)
    is_c: bool = False
    is_vc: bool = False
    is_wk: bool = False


class CustomFixture(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    match_id: str = Field(pattern=r"^custom_[a-zA-Z0-9_-]{1,100}$")
    name: str = Field(min_length=3, max_length=200)
    format: str = Field(default="T20", max_length=100)
    id: str | None = None
    status: str = Field(default="USER SUPPLIED", max_length=200)
    current_crr: float = Field(default=0, ge=0, le=100)
    projected_total: float = Field(default=0, ge=0, le=1000)
    chasing_win_prob: float = Field(default=50, ge=0, le=100)
    teams: dict
    venue: dict
    toss: dict
    playing_xi_home: list[FixturePlayer] = Field(min_length=11, max_length=11)
    playing_xi_away: list[FixturePlayer] = Field(min_length=11, max_length=11)

    @model_validator(mode="after")
    def validate_fixture(self):
        json.dumps(self.model_dump(), allow_nan=False)
        codes = []
        for side in ("home", "away"):
            team = self.teams.get(side, {})
            if not isinstance(team, dict) or not isinstance(team.get("name"), str) or not team["name"].strip():
                raise ValueError("Both named teams are required")
            code = team.get("code", "")
            if not isinstance(code, str) or not re.fullmatch(r"[A-Z0-9-]{1,12}", code):
                raise ValueError("Team codes must contain 1-12 uppercase letters, digits or hyphens")
            codes.append(code)
        if codes[0] == codes[1]:
            raise ValueError("Team codes must differ")
        if self.teams['home']['name'] == self.teams['away']['name']:
            raise ValueError("Team names must differ")
        for field, upper in (("avg_first_innings", 1000), ("avg_second_innings", 1000),
                             ("dew_factor", 1), ("chasing_win_pct", 100),
                             ("pace_wicket_pct", 100), ("spin_wicket_pct", 100)):
            if field in self.venue:
                value = self.venue[field]
                if type(value) not in (int, float) or not 0 <= value <= upper:
                    raise ValueError(f"Venue {field} must be numeric within 0-{upper}")
        for xi in (self.playing_xi_home, self.playing_xi_away):
            if {p.order for p in xi} != set(range(1, 12)):
                raise ValueError("Each XI must have unique batting positions 1-11")
        names = [p.name.casefold() for p in self.playing_xi_home + self.playing_xi_away]
        if len(set(names)) != 22:
            raise ValueError("All 22 player names must be distinct")
        if not isinstance(self.venue.get("name"), str) or not self.venue["name"].strip():
            raise ValueError("A venue name is required")
        if self.toss.get("choice") not in {"bat", "bowl"}:
            raise ValueError("Toss choice must be bat or bowl")
        if self.toss.get("winner") not in {self.teams[s]["name"] for s in ("home", "away")}:
            raise ValueError("Toss winner must be one of the supplied teams")
        return self


class FixtureStore:
    def __init__(self, path=None):
        self.path = Path(path or os.getenv("CRICKET_FIXTURE_DB") or
                         Path(__file__).parent.parent / "data" / "custom_fixtures.sqlite3")

    def load(self):
        if not self.path.exists():
            return []
        with closing(sqlite3.connect(self.path)) as con:
            return [json.loads(row[0]) for row in con.execute("SELECT payload FROM fixtures")]

    def save(self, fixture):
        # JSON disallows NaN/Infinity even inside optional nested context.
        payload = json.dumps(fixture, allow_nan=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute("CREATE TABLE IF NOT EXISTS fixtures (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            con.execute("INSERT INTO fixtures VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                        (fixture["id"], payload))
