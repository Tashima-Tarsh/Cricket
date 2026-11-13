"""No synthetic strike rates from missing women's T20 records."""
from pathlib import Path
from tempfile import TemporaryDirectory
import duckdb
from gl_engine.wt20_analytics import WT20AnalyticsEngine


def test_missing_player_does_not_invent_rates_or_h2h():
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp)/"women.duckdb"
        with duckdb.connect(str(db_path)) as db:
            db.execute("""CREATE TABLE deliveries(
                batter VARCHAR, bowler VARCHAR, runs_batter INT, runs_extras INT,
                runs_total INT, is_wicket BOOLEAN, player_dismissed VARCHAR,
                wicket_type VARCHAR, over INTEGER
            )""")
            db.execute("""INSERT INTO deliveries VALUES
                ('Alex Example','Bella Example',4,0,4,false,'','',0)""")
        eng=WT20AnalyticsEngine(str(db_path))
        batter=eng.query_batter_telemetry("No Such Player")
        assert batter["sample_balls"]==0
        assert batter["strike_rate"] is None
        assert batter["dismissal_prob_per_ball"] is None
        bowler=eng.query_bowler_telemetry("No Such Bowler")
        assert bowler["sample_balls"]==0
        assert bowler["economy"] is None
        matchup=eng.query_h2h_matchup("No Such Player","Bella Example")
        assert matchup["provenance"]=="INSUFFICIENT_PLAYER_HISTORY"
