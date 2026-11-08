"""Phase 0 safety contracts. Test fixtures are never production roster sources."""
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class Phase0SafetyTests(unittest.TestCase):
    def test_no_forbidden_production_literals(self):
        forbidden = ('Top Batter', 'Star Opener', 'Tailender', 'Strike Pacer',
                     'AFG_GURBAZ', 'LIVE & TRACKED', 'Rank 1 Contender', '0.946')
        hits = []
        for directory in ('gl_engine', 'edgeforge', 'dream11-edge/edge', 'frontend/src'):
            for path in (ROOT / directory).rglob('*'):
                if path.suffix not in ('.py', '.ts', '.tsx', '.html', '.json') or path.name.startswith('test_'):
                    continue
                for line, value in enumerate(path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                    if any(word in value for word in forbidden):
                        hits.append(f'{path.relative_to(ROOT)}:{line}')
        self.assertEqual(hits, [])

    def test_catalog_does_not_reuse_fifth_fixture_roster(self):
        from gl_engine.match_catalog import get_match_data, UnknownMatchError
        for match_id in ('ind_wi_2026_01', 'ind_wi_2026_02', 'ind_wi_2026_03', 'ind_wi_2026_04'):
            with self.subTest(match_id=match_id), self.assertRaises(UnknownMatchError):
                get_match_data(match_id)

    def test_global_schema_is_shared_and_rejects_invalid_evidence(self):
        from gl_engine.provenance import DataProvenance
        from edgeforge.models.schemas import DataProvenance as EdgeProvenance
        from pydantic import ValidationError
        self.assertIs(DataProvenance, EdgeProvenance)
        value = DataProvenance(source='unavailable')
        self.assertEqual(value.verification_status, 'UNVERIFIED')
        self.assertIsNotNone(value.timestamp.tzinfo)
        for kwargs in ({'source':'unavailable', 'verification_status':'VERIFIED'},
                       {'source':'estimated', 'confidence':0.9},
                       {'source':'provider', 'sample_size':-1}):
            with self.assertRaises(ValidationError):
                DataProvenance(**kwargs)

    def test_roster_guard_rejects_empty_duplicate_and_dummy_names(self):
        from gl_engine.roster_safety import validate_roster
        from fastapi import HTTPException
        for roster in ([], [{'id':'same', 'name':'Same', 'team':'A'}]*11,
                       [{'id':str(i), 'name':'Top Batter', 'team':'A'} for i in range(11)]):
            with self.assertRaises(HTTPException) as caught:
                validate_roster(roster)
            self.assertEqual(caught.exception.status_code, 503)

    def test_universal_empty_roster_fails_before_battles_or_solver(self):
        from gl_engine.universal_engine import UniversalMatchEngine
        from fastapi import HTTPException
        engine = UniversalMatchEngine.__new__(UniversalMatchEngine)
        engine._matches = {'empty': {'id':'empty'}}
        engine._cached_states = {}
        with patch.object(engine, '_profile_match_players', return_value=[]), \
             patch.object(engine, '_build_battle_matrix') as battles:
            with self.assertRaises(HTTPException) as caught:
                engine.get_unified_state('empty')
            self.assertEqual(caught.exception.status_code, 503)
            battles.assert_not_called()

    def test_api_success_and_error_responses_have_provenance(self):
        from fastapi.testclient import TestClient
        from gl_engine.web_app import app
        from edgeforge.app import app as edge_app
        for application, paths in ((app, ('/api/health', '/api/portal/roster?match_id=missing', '/api/missing')),
                                   (edge_app, ('/', '/api/missing'))):
            with TestClient(application) as client:
                for path in paths:
                    response = client.get(path)
                    self.assertIn('provenance', response.json(), path)
                    self.assertIn('verification_status', response.json()['provenance'])

    def test_nested_lineups_and_players_have_provenance(self):
        from gl_engine.provenance import annotate_payload
        data = annotate_payload({'lineups':[{'players':[{'id':'real-id'}]}]}, 'test:unverified')
        for obj in (data, data['lineups'][0], data['lineups'][0]['players'][0]):
            self.assertEqual(obj['provenance']['verification_status'], 'UNVERIFIED')

    def test_unknown_roster_cannot_fall_back(self):
        from gl_engine.web_app import get_portal_match_roster
        from gl_engine.match_catalog import UnknownMatchError
        with self.assertRaises(UnknownMatchError):
            get_portal_match_roster('unconnected_fixture')

    def test_transport_preserves_maps_and_labels_errors_and_downloads(self):
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import PlainTextResponse
        from fastapi.testclient import TestClient
        from gl_engine.provenance import install_provenance
        app = FastAPI()
        install_provenance(app)
        @app.get('/lineups')
        def lineups():
            return {'lineups':[{'players':[{'id':'x'}], 'team_balance':{'A':6,'B':5}}]}
        @app.get('/invalid')
        def invalid():
            return {'provenance':{'source':'unavailable','verification_status':'VERIFIED'}}
        @app.get('/crash')
        def crash():
            raise RuntimeError('private error detail')
        @app.get('/download')
        def download():
            return PlainTextResponse('unchanged csv')
        with TestClient(app, raise_server_exceptions=False) as client:
            data = client.get('/lineups').json()['lineups'][0]
            self.assertIn('provenance', data)
            self.assertEqual(data['team_balance'], {'A':6,'B':5})
            for path in ('/invalid', '/crash'):
                response = client.get(path)
                self.assertEqual(response.status_code, 503)
                self.assertIn('provenance', response.json())
                self.assertNotIn('private error', response.text)
            download = client.get('/download')
            self.assertEqual(download.text, 'unchanged csv')
            self.assertIn('x-data-provenance', download.headers)
            self.assertNotIn('provenance', client.get('/openapi.json').json())

    def test_core_lineups_carry_provenance_without_http(self):
        import json
        from gl_engine.models import Player
        from gl_engine.ortools_optimizer import ORToolsCricketOptimizer
        players = [Player(**p) for p in json.loads((ROOT/'gl_engine/data/ind_wi_match.json').read_text())['players']]
        lineup = ORToolsCricketOptimizer(players).generate_grand_league_portfolio(num_teams=1)[0]
        self.assertEqual(lineup.provenance.verification_status, 'MODEL_ESTIMATE')
        self.assertTrue(all(p.provenance.verification_status == 'UNVERIFIED' for p in lineup.players))

    def test_universal_direct_lineup_is_provenance_tagged(self):
        import json
        from gl_engine.universal_engine import UniversalMatchEngine
        from gl_engine.models import Player
        pool = [Player(**p).model_dump(mode='json') for p in json.loads((ROOT/'gl_engine/data/ind_wi_match.json').read_text())['players']]
        scenario = dict(id='test', name='Test', tag='TEST', script='Test',
                        target_c=pool[0]['id'], target_vc=pool[1]['id'], credit_min=75, credit_max=100)
        result = UniversalMatchEngine()._solve_cp_sat_team(pool, scenario, [], 'IND', 'WI')
        self.assertIsNotNone(result)
        self.assertIn('provenance', result)

    def test_edgeforge_generated_lineup_has_provenance(self):
        import json
        from edgeforge.models.schemas import Player, DataProvenance
        from edgeforge.optimize.rank_optimizer import RankOptimizer, OptimizerConfig
        rows = json.loads((ROOT/'gl_engine/data/ind_wi_match.json').read_text())['players']
        players = [Player(id=p['id'], name=p['name'], team=p['team'], role=p['role'], credits=p['credits'], projected_points=40,
                          projected_ownership=20, provenance=DataProvenance(source='unavailable')) for p in rows]
        cfg = OptimizerConfig(n_portfolios=1, n_sims=30, min_unspent=0, max_unspent=30, min_csp=0, min_differentials=0)
        result = RankOptimizer(config=cfg, seed=42).optimize(players, fixture_id='test')
        self.assertEqual(len(result.lineups), 1)
        self.assertIn('provenance', result.lineups[0])
        self.assertTrue(all('provenance' in p for p in result.lineups[0]['players']))
