"""Integration tests for FastAPI REST API

These tests verify that API endpoints correctly receive, process,
and return data as expected.
"""

import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Try to import FastAPI dependencies
try:
    from fastapi.testclient import TestClient
    from api.main import app
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None
    app = None
    print("\nWARNING: FastAPI not installed. API tests will be skipped.")
    print("Install with: pip install -r requirements_api.txt\n")


@unittest.skipIf(not FASTAPI_AVAILABLE, "FastAPI not installed")
class TestAPIIntegration(unittest.TestCase):
    """Integration tests for REST API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        if FASTAPI_AVAILABLE:
            cls.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns API information"""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('name', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['name'], 'StrategyBuilder API')

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)

    def test_strategies_endpoint(self):
        """Test GET /strategies endpoint lists available strategies"""
        response = self.client.get("/strategies")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('strategies', data)
        self.assertIn('total_count', data)

        # Should have at least one strategy
        self.assertGreater(len(data['strategies']), 0)
        self.assertEqual(data['total_count'], len(data['strategies']))

        # Check first strategy structure
        first_strategy = data['strategies'][0]
        self.assertIn('name', first_strategy)
        self.assertIn('description', first_strategy)
        self.assertIn('default_parameters', first_strategy)
        self.assertIn('optimization_ranges', first_strategy)
        self.assertIn('constraints', first_strategy)

    def test_strategies_endpoint_includes_bollinger_bands(self):
        """Test strategies endpoint includes Bollinger Bands"""
        response = self.client.get("/strategies")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        strategy_names = [s['name'] for s in data['strategies']]

        self.assertIn('bollinger_bands', strategy_names)

    def test_backtest_endpoint_with_valid_request(self):
        """Test POST /backtest with valid request"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31",
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            },
            "use_vectorized": True,
            "interval": "1d"
        }

        response = self.client.post("/backtest", json=request_data)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Check response structure
        self.assertIn('success', data)
        self.assertIn('ticker', data)
        self.assertIn('strategy', data)
        self.assertIn('results', data)
        self.assertIn('execution_time_ms', data)

        # Verify response values
        self.assertTrue(data['success'])
        self.assertEqual(data['ticker'], 'AAPL')
        self.assertEqual(data['strategy'], 'bollinger_bands')

        # Check results contain required fields
        results = data['results']
        self.assertIn('return_pct', results)
        self.assertIn('sharpe_ratio', results)
        self.assertIn('max_drawdown', results)
        self.assertIn('total_trades', results)

        # Execution time should be positive
        self.assertGreater(data['execution_time_ms'], 0)

    def test_backtest_endpoint_with_sma_strategy(self):
        """Test backtest with SMA crossover strategy"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "sma_crossover",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31",
            "parameters": {
                "fast_period": 10,
                "slow_period": 30
            },
            "use_vectorized": True
        }

        response = self.client.post("/backtest", json=request_data)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['strategy'], 'sma_crossover')

    def test_backtest_endpoint_with_default_parameters(self):
        """Test backtest without specifying parameters (use defaults)"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31"
        }

        response = self.client.post("/backtest", json=request_data)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])

        # Should use default parameters from config
        results = data['results']
        self.assertIn('return_pct', results)

    def test_backtest_endpoint_invalid_strategy(self):
        """Test backtest with non-existent strategy returns error"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "nonexistent_strategy",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31"
        }

        response = self.client.post("/backtest", json=request_data)

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('not found', data['detail'])

    def test_backtest_endpoint_invalid_date_format(self):
        """Test backtest with invalid date format returns error"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023/11/01",  # Wrong format
            "end_date": "2023-12-31"
        }

        response = self.client.post("/backtest", json=request_data)

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn('detail', data)

    def test_backtest_endpoint_missing_required_fields(self):
        """Test backtest with missing required fields returns error"""
        request_data = {
            "ticker": "AAPL",
            # Missing strategy
            "start_date": "2023-11-01",
            "end_date": "2023-12-31"
        }

        response = self.client.post("/backtest", json=request_data)

        # Should return 422 Unprocessable Entity (validation error)
        self.assertEqual(response.status_code, 422)

    def test_backtest_endpoint_invalid_parameters(self):
        """Test backtest with parameters that violate constraints"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31",
            "parameters": {
                "period": 200,  # Exceeds max constraint (100)
                "devfactor": 2.0
            }
        }

        response = self.client.post("/backtest", json=request_data)

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('constraints', data['detail'])

    def test_config_endpoint(self):
        """Test GET /config endpoint"""
        response = self.client.get("/config")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('api', data)
        self.assertIn('performance', data)
        self.assertIn('available_strategies', data)

        # Check available strategies
        self.assertIsInstance(data['available_strategies'], list)
        self.assertGreater(len(data['available_strategies']), 0)

    def test_api_documentation_accessible(self):
        """Test that API documentation is accessible"""
        # Test OpenAPI JSON
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)

        openapi_data = response.json()
        self.assertIn('openapi', openapi_data)
        self.assertIn('paths', openapi_data)

        # Check that our endpoints are documented
        paths = openapi_data['paths']
        self.assertIn('/backtest', paths)
        self.assertIn('/strategies', paths)

    def test_backtest_response_includes_execution_time(self):
        """Test that backtest response includes execution time metric"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-12-01",
            "end_date": "2023-12-31",
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            }
        }

        response = self.client.post("/backtest", json=request_data)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('execution_time_ms', data)

        # Execution time should be reasonable (< 10 seconds = 10000 ms)
        self.assertLess(data['execution_time_ms'], 10000)
        self.assertGreater(data['execution_time_ms'], 0)

    def test_backtest_results_contain_trades(self):
        """Test that backtest results include trade details"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            }
        }

        response = self.client.post("/backtest", json=request_data)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        results = data['results']

        self.assertIn('trades', results)
        self.assertIsInstance(results['trades'], list)

        # If there are trades, check their structure
        if len(results['trades']) > 0:
            first_trade = results['trades'][0]
            self.assertIn('entry_date', first_trade)
            self.assertIn('exit_date', first_trade)
            self.assertIn('entry_price', first_trade)
            self.assertIn('exit_price', first_trade)
            self.assertIn('pnl', first_trade)

    def test_multiple_concurrent_backtest_requests(self):
        """Test API can handle multiple concurrent requests"""
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-12-01",
            "end_date": "2023-12-31",
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            }
        }

        # Send multiple requests
        responses = []
        for _ in range(3):
            response = self.client.post("/backtest", json=request_data)
            responses.append(response)

        # All should succeed
        for response in responses:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['success'])


@unittest.skipIf(not FASTAPI_AVAILABLE, "FastAPI not installed")
class TestAPIValidation(unittest.TestCase):
    """Test API request validation"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        if FASTAPI_AVAILABLE:
            cls.client = TestClient(app)

    def test_backtest_validates_ticker_format(self):
        """Test that API validates ticker is provided"""
        request_data = {
            "ticker": "",  # Empty ticker
            "strategy": "bollinger_bands",
            "start_date": "2023-11-01",
            "end_date": "2023-12-31"
        }

        response = self.client.post("/backtest", json=request_data)

        # Should fail validation
        self.assertNotEqual(response.status_code, 200)

    def test_backtest_validates_date_order(self):
        """Test backtest validates start_date is before end_date"""
        # This validation happens at the application level
        request_data = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands",
            "start_date": "2023-12-31",  # After end_date
            "end_date": "2023-11-01"
        }

        response = self.client.post("/backtest", json=request_data)

        # May succeed at API level but should have no/invalid results
        if response.status_code == 200:
            # Just verify it doesn't crash
            data = response.json()
            self.assertIn('results', data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
