"""WBBL archive indexing preserves provenance, rejects invalid data and is atomic."""
from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
import json
import zipfile
import duckdb
import pytest

from gl_engine.wbbl_archive import build_wbbl_archive, CRICSHEET_WBBL_JSON


def archive_with(n=2, gender="female"):
    mem=BytesIO()
    with zipfile.ZipFile(mem,"w") as z:
        for i in range(n):
            match = {
                "info": {
                    "gender": gender, "dates": [f"202{i+1}-11-01"],
                    "teams": ["Sydney Sixers", "Sydney Thunder"],
                    "event": {"name": "Women's Big Bash League"},
                },
                "innings": [{"team": "Sydney Sixers",
                    "overs": [{"over":0, "deliveries":[
                        {"batter":"Alex Example","bowler":"Bella Example",
                         "runs":{"batter":4,"extras":0,"total":4}},
                        {"batter":"Alex Example","bowler":"Bella Example",
                         "runs":{"batter":0,"extras":1,"total":1},"extras":{"wides":1}}
                    ]}]}]
            }
            z.writestr(f"{i+1}.json",json.dumps(match))
    return mem.getvalue()


def test_index_creates_licensed_database():
    with TemporaryDirectory() as tmp:
        target=Path(tmp)/"wbbl.duckdb"
        result=build_wbbl_archive(archive_with(2),target,minimum_matches=2)
        assert result["status"]=="ARCHIVE_SYNCED"
        assert result["match_count"]==2
        assert result["source"]==CRICSHEET_WBBL_JSON
        with duckdb.connect(str(target),read_only=True) as db:
            assert db.execute("SELECT COUNT(*) FROM matches").fetchone()[0] == 2
            assert db.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0] == 4
            assert db.execute("SELECT SUM(CAST(is_legal_ball AS INTEGER)) FROM deliveries").fetchone()[0] == 2


def test_failure_does_not_replace_previous_archive():
    with TemporaryDirectory() as tmp:
        target=Path(tmp)/"wbbl.duckdb"
        build_wbbl_archive(archive_with(2),target,minimum_matches=2)
        original=target.read_bytes()
        with pytest.raises(ValueError):
            build_wbbl_archive(archive_with(1,gender="male"),target,minimum_matches=2)
        assert target.read_bytes()==original
