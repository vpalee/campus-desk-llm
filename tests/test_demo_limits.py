import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.demo_limits import DemoBudget, DemoBusy
from app.main import app


class DemoBudgetTests(unittest.TestCase):
    def test_capacity_is_reserved_until_request_finishes(self):
        budget = DemoBudget(concurrent=1)
        with budget.slot():
            with self.assertRaises(DemoBusy):
                with budget.slot():
                    self.fail('Concurrent request should not run')
        with budget.slot():
            pass

    def test_failure_releases_capacity_but_consumes_budget(self):
        budget = DemoBudget(hourly=1)
        with self.assertRaises(RuntimeError):
            with budget.slot():
                raise RuntimeError('model failed')
        self.assertEqual(budget.active, 0)
        with self.assertRaises(DemoBusy):
            with budget.slot():
                self.fail('Failed calls still consume quota')

    def test_hourly_window_expires_at_boundary(self):
        now = [0]
        budget = DemoBudget(hourly=1, clock=lambda: now[0])
        with budget.slot():
            pass
        now[0] = 3599
        with self.assertRaises(DemoBusy) as cm:
            with budget.slot():
                pass
        self.assertEqual(cm.exception.retry_after, 1)
        now[0] = 3600
        with budget.slot():
            pass

    def test_daily_budget_survives_hourly_expiration(self):
        now = [0]
        budget = DemoBudget(hourly=1, daily=1, clock=lambda: now[0])
        with budget.slot():
            pass
        now[0] = 3600
        with self.assertRaises(DemoBusy) as cm:
            with budget.slot():
                pass
        self.assertEqual(cm.exception.retry_after, 82800)
        now[0] = 86400
        with budget.slot():
            pass

    def test_http_budget_rejects_before_model_and_keeps_health_available(self):
        budget = DemoBudget(hourly=1)
        with patch.dict(os.environ, {'PUBLIC_DEMO':'1'}), patch('app.main.demo_budget', budget), patch('app.main.agent.run', return_value={'status':'answered'}) as run:
            with TestClient(app) as client:
                self.assertEqual(client.post('/api/ask', json={'question':'wifi help'}).status_code, 200)
                rejected = client.post('/api/ask', json={'question':'wifi help'})
                self.assertEqual(rejected.status_code, 429)
                self.assertGreater(int(rejected.headers['retry-after']), 0)
                self.assertEqual(client.get('/api/health').status_code, 200)
                self.assertEqual(run.call_count, 1)


if __name__ == '__main__':
    unittest.main()
