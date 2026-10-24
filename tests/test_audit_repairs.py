"""Executable regression cases for the supplied integration audit."""
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import duckdb
import pandas as pd
from fastapi.testclient import TestClient

from gl_engine import universal_engine as ue, live_feed
from gl_engine.models import Player
from gl_engine.ortools_optimizer import ORToolsCricketOptimizer
from gl_engine.web_app import app, MATCH_FILE


class AuditRepairTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.players = [Player(**p) for p in json.loads(MATCH_FILE.read_text(encoding="utf-8"))["players"]]

    def test_unknown_match_never_returns_default(self):
        response = self.client.get('/api/state?match_id=does_not_exist')
        self.assertEqual(response.status_code, 409)
        with self.assertRaises(KeyError):
            ue.UniversalMatchEngine().get_unified_state('does_not_exist')

    def test_request_limits_are_enforced_before_solving(self):
        for query in ('teams=0', 'teams=21', 'overs=4', 'overs=21', 'risk=bad',
                      'spots=999999999', 'min_credits=95&max_credits=80',
                      'locked=unknown', 'excluded=unknown', 'exposure=bad',
                      'exposure=ind_mayank:nan', 'max_overlap=12'):
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/api/ortools/optimize?' + query).status_code, 422)

    def test_infeasible_locks_are_never_silently_relaxed(self):
        ids = [p.id for p in self.players[:12]]
        result = ORToolsCricketOptimizer(self.players).generate_grand_league_portfolio(
            num_teams=1, locked_player_ids=ids)
        self.assertEqual(result, [])

    def test_zero_exposure_means_no_selection(self):
        pid = self.players[0].id
        result = ORToolsCricketOptimizer(self.players).generate_grand_league_portfolio(
            num_teams=1, player_exposure_limits={pid: 0})
        self.assertTrue(result)
        self.assertNotIn(pid, [p.id for p in result[0].players])

    def test_reduced_overs_preserves_selected_credit_band(self):
        result = ORToolsCricketOptimizer(self.players).generate_grand_league_portfolio(
            num_teams=1, overs=10, credit_strategy='79-85')
        self.assertTrue(result)
        self.assertLessEqual(result[0].total_credits, 85)

    def test_state_applies_overs_to_projections_and_constraints(self):
        base = self.client.get('/api/state?force_refresh=true&overs=20').json()
        short = self.client.get('/api/state?force_refresh=true&overs=10').json()
        self.assertEqual(short['rain_constraints']['overs'], 10)
        self.assertNotEqual([p['projected_points'] for p in base['players']],
                            [p['projected_points'] for p in short['players']])

    def test_analyst_rain_query_is_an_explicit_illustration(self):
        result = self.client.get('/api/analyst/query?q=rain&match_id=ind_vs_wi_5th_t20_2026')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['provenance'], 'RULE_BASED_RETRIEVAL')
        self.assertIn('illustrative', result.json()['reply'].lower())

    def test_universal_infeasible_returns_no_invalid_roster(self):
        pool = [p.model_dump() for p in self.players]
        scenario = dict(id='test', name='Test', tag='TEST', script='Test',
                        target_c=pool[0]['id'], target_vc=pool[1]['id'], credit_min=1, credit_max=2)
        result = ue.UniversalMatchEngine()._solve_cp_sat_team(pool, scenario, [], 'IND', 'WI')
        self.assertIsNone(result)

    def test_live_outage_returns_empty_catalog(self):
        with patch.object(live_feed, '_fetch_from_cricdata_sdk', return_value=[]), \
             patch.object(live_feed, '_fetch_from_espn_rss', return_value=[]):
            self.assertEqual(live_feed.fetch_espn_cricinfo_live_matches(force_refresh=True), [])

    def test_health_checks_actual_database(self):
        with patch('gl_engine.wt20_analytics.DB_PATH', Path('__absent__.duckdb')):
            data = self.client.get('/api/health').json()
        self.assertEqual(data['status'], 'degraded')
        self.assertIsNone(data['database']['deliveries_indexed'])

    def test_ingestion_requires_authentication(self):
        with patch.dict('os.environ', {'CRICKET_ADMIN_TOKEN': 'test-token'}):
            self.assertEqual(self.client.post('/api/match/ingest', json={}).status_code, 401)

    def test_invalid_fixture_rejected(self):
        with patch.dict('os.environ', {'CRICKET_ADMIN_TOKEN': 'test-token'}):
            response = self.client.post('/api/match/ingest', json={}, headers={'Authorization': 'Bearer test-token'})
        self.assertEqual(response.status_code, 422)

    def test_player_names_are_bound_as_literal_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'stats.duckdb'
            con = duckdb.connect(str(path))
            con.execute('CREATE TABLE deliveries(batter VARCHAR, bowler VARCHAR, runs_batter INT, runs_total INT, is_wicket BOOLEAN)')
            con.execute("INSERT INTO deliveries VALUES ('Other', 'Other', 999, 999, true)")
            con.close()
            engine = ue.UniversalMatchEngine()
            meta = copy.deepcopy(engine._matches['afg_vs_ban_odi_sharjah'])
            meta['playing_xi_home'] = [dict(name="x'OR(1=1)OR'X", role='BAT', credits=8)]
            meta['playing_xi_away'] = []
            with patch.object(ue, 'DB_PATH', path):
                players = engine._profile_match_players(meta)
            self.assertEqual(players[0]['stats']['runs'], 0)

    def test_unicode_and_punctuation_names_keep_distinct_player_ids(self):
        engine = ue.UniversalMatchEngine()
        meta = copy.deepcopy(engine._matches['afg_vs_ban_odi_sharjah'])
        names = ['A B', 'A-B', '\u0928\u093f\u0924\u093f\u0936', '\u0930\u094b\u0939\u093f\u0924']
        meta['playing_xi_home'] = [dict(name=n, role='BAT', credits=8) for n in names]
        meta['playing_xi_away'] = []
        players = engine._profile_match_players(meta)
        self.assertEqual(len({p['id'] for p in players}), len(names))

    def test_missing_h2h_evidence_never_generates_counts(self):
        engine = ue.UniversalMatchEngine()
        with patch.object(ue, 'DB_PATH', Path('__absent__.duckdb')):
            self.assertEqual(engine._build_battle_matrix([p.model_dump() for p in self.players],
                                                       engine._matches['afg_ban']), [])

    def test_model_features_do_not_use_target_day(self):
        from gl_engine.xgboost_model import prepare_prematch_features
        rows = pd.DataFrame([
            dict(player='A', date='2025-01-01', min_over=1, runs=10, balls=8, balls_bowled=6,
                 runs_conceded=7, death_balls=0, pp_balls=6, fantasy_points=20),
            dict(player='A', date='2025-01-02', min_over=10, runs=99, balls=40, balls_bowled=24,
                 runs_conceded=50, death_balls=12, pp_balls=0, fantasy_points=140),
            dict(player='A', date='2025-01-02', min_over=0, runs=200, balls=100, balls_bowled=0,
                 runs_conceded=0, death_balls=0, pp_balls=0, fantasy_points=250),
        ])
        before = prepare_prematch_features(rows)
        rows.loc[1:, ['runs', 'min_over', 'balls_bowled', 'death_balls', 'fantasy_points']] = 999
        after = prepare_prematch_features(rows)
        features = ['batting_position', 'overs_bowled', 'death_overs_rate', 'powerplay_overs_rate',
                    'prior_avg_fantasy_pts', 'prior_strike_rate', 'prior_economy']
        pd.testing.assert_frame_equal(before[features], after[features])
        self.assertEqual(before.iloc[2]['prior_avg_fantasy_pts'], 20)

    def test_fixture_survives_engine_restart(self):
        fixture = dict(match_id='custom_regression', name='Regression fixture', format='T20',
                       teams={'home': {'name': 'Home', 'code': 'H'}, 'away': {'name': 'Away', 'code': 'A'}},
                       venue={'name': 'User venue'}, toss={'winner': 'Home', 'choice': 'bat'})
        for side in ('home', 'away'):
            fixture['playing_xi_' + side] = [dict(name=f'{side} {i}', role='WK' if i == 1 else ('BAT' if i < 5 else ('AR' if i < 8 else 'BOWL')),
                                                 credits=7.5, order=i, bat_hand='RHB', bowl_style='User supplied') for i in range(1,12)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixtures.sqlite3'
            engine = ue.UniversalMatchEngine(path)
            with patch.object(engine, 'get_unified_state', return_value={'status': 'success'}):
                engine.ingest_match(fixture)
            restored = ue.UniversalMatchEngine(path)
            self.assertEqual(restored._matches['custom_regression']['teams'], fixture['teams'])
            self.assertEqual(len(restored._matches['custom_regression']['playing_xi_home']), 11)
            with patch.object(ue, '_ENGINE_INSTANCE', restored):
                response = self.client.get('/api/ortools/optimize?match_id=custom_regression&teams=1')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['lineups'], 'Missing ownership must not impose invented CSP constraints')
            self.assertEqual(response.json()['ownership_status'], 'UNAVAILABLE_NEUTRAL_PRIOR')
            with patch.object(ue, '_ENGINE_INSTANCE', restored):
                response = self.client.get('/api/ortools/optimize?match_id=custom_regression&risk=DIFFERENTIAL_HEAVY')
            self.assertEqual(response.status_code, 422)

    def test_mcp_simulation_full_json_rpc(self):
        from gl_engine.mcp_server import CricketMCPServer
        server = CricketMCPServer()
        request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {
            'name': 'simulate_ball_by_ball', 'arguments': {'match_id': 'afg_ban', 'n_sims': 2}}}
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO(json.dumps(request) + '\n')), patch('sys.stdout', output):
            server.handle_stdio_rpc()
        response = json.loads(output.getvalue())
        self.assertNotIn('error', response)
        result = json.loads(response['result']['content'][0]['text'])
        self.assertEqual(len(result['player_distributions']), 22)
        self.assertEqual(result['num_simulations'], 2)
        for bad in (0, 1001, True, 1.5):
            with self.assertRaises(ValueError):
                server.call_tool('simulate_ball_by_ball', {'n_sims': bad})


if __name__ == '__main__':
    unittest.main()
