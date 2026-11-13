"""Exact-match, WBBL-only historical analytics and pre-match cutoff."""
from datetime import date
from tempfile import TemporaryDirectory
from pathlib import Path
import duckdb

from gl_engine.wbbl_historical import WBBLHistorical


def sample_db(path):
    with duckdb.connect(str(path)) as db:
        db.execute("CREATE TABLE matches(match_id VARCHAR, match_date DATE, team1 VARCHAR, team2 VARCHAR)")
        db.execute("""CREATE TABLE deliveries(
            match_id VARCHAR, batter VARCHAR, bowler VARCHAR, runs_batter INT,
            is_wicket BOOLEAN, player_dismissed VARCHAR)""")
        db.execute("""INSERT INTO matches VALUES
          ('old','2025-10-01','Sydney Sixers','Sydney Thunder'),
          ('future','2027-10-01','Sydney Sixers','Sydney Thunder'),
          ('other','2025-10-01','India','Zimbabwe')""")
        db.execute("""INSERT INTO deliveries VALUES
          ('old','Alex Example','Bella Example',4,false,''),
          ('old','Alex Example','Bella Example',0,true,'Alex Example'),
          ('future','Alex Example','Bella Example',6,false,''),
          ('other','Alex Example','Bella Example',6,false,'')""")


def test_cutoff_filter_and_exact_name():
    with TemporaryDirectory() as tmp:
        path=Path(tmp)/"wt20.duckdb"
        sample_db(path)
        api=WBBLHistorical(path)
        result=api.player("Alex Example",before=date(2026,11,13))
        assert result["status"]=="OBSERVED_CRICSHEET_PARTIAL"
        assert result["sample_matches"]==1
        assert result["sample_recorded_deliveries"]==2
        assert result["batting_runs"]==4
        assert api.player("Alex",before=date(2026,11,13))["status"]=="NO_WBBL_HISTORY"
        h2h=api.matchup("Alex Example","Bella Example",before=date(2026,11,13))
        assert h2h["recorded_deliveries"]==2
        assert h2h["dismissals"]==1


def test_no_database_does_not_fabricate():
    with TemporaryDirectory() as tmp:
        r=WBBLHistorical(Path(tmp)/"absent.duckdb").player("Alex Example")
        assert r["status"]=="DATA_UNAVAILABLE"
