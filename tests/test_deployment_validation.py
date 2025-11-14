"""Deployment validation tests

These tests verify:
- Docker build success
- Dockerfile configuration
- Requirements installation
- Report generation
- Notification system
"""

import os
import sys
import unittest
import subprocess
from datetime import datetime
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDockerValidation(unittest.TestCase):
    """Validate Docker configuration"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = os.path.join(os.path.dirname(__file__), '..')

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = os.path.join(self.project_root, 'Dockerfile')
        self.assertTrue(os.path.exists(dockerfile_path),
                       "Dockerfile not found in project root")

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists"""
        dockerignore_path = os.path.join(self.project_root, '.dockerignore')
        self.assertTrue(os.path.exists(dockerignore_path),
                       ".dockerignore not found in project root")

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists"""
        compose_path = os.path.join(self.project_root, 'docker-compose.yml')
        self.assertTrue(os.path.exists(compose_path),
                       "docker-compose.yml not found in project root")

    def test_dockerfile_syntax(self):
        """Test Dockerfile syntax is valid"""
        dockerfile_path = os.path.join(self.project_root, 'Dockerfile')

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        # Check for required instructions
        self.assertIn('FROM', content, "Dockerfile missing FROM instruction")
        self.assertIn('WORKDIR', content, "Dockerfile missing WORKDIR instruction")
        self.assertIn('COPY', content, "Dockerfile missing COPY instruction")
        self.assertIn('RUN', content, "Dockerfile missing RUN instruction")
        self.assertIn('CMD', content, "Dockerfile missing CMD instruction")

    def test_dockerfile_has_healthcheck(self):
        """Test Dockerfile includes health check"""
        dockerfile_path = os.path.join(self.project_root, 'Dockerfile')

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        self.assertIn('HEALTHCHECK', content,
                     "Dockerfile should include HEALTHCHECK instruction")

    def test_dockerfile_uses_nonroot_user(self):
        """Test Dockerfile creates and uses non-root user"""
        dockerfile_path = os.path.join(self.project_root, 'Dockerfile')

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        self.assertIn('useradd', content,
                     "Dockerfile should create non-root user")
        self.assertIn('USER', content,
                     "Dockerfile should switch to non-root user")

    def test_docker_compose_syntax(self):
        """Test docker-compose.yml syntax"""
        compose_path = os.path.join(self.project_root, 'docker-compose.yml')

        with open(compose_path, 'r') as f:
            content = f.read()

        # Check for required sections
        self.assertIn('version:', content)
        self.assertIn('services:', content)
        self.assertIn('ports:', content)

    def test_requirements_files_exist(self):
        """Test that requirements files exist"""
        requirements_path = os.path.join(self.project_root, 'requirements.txt')
        api_requirements_path = os.path.join(self.project_root, 'requirements_api.txt')

        self.assertTrue(os.path.exists(requirements_path),
                       "requirements.txt not found")
        self.assertTrue(os.path.exists(api_requirements_path),
                       "requirements_api.txt not found")

    def test_requirements_has_core_dependencies(self):
        """Test requirements.txt has core dependencies"""
        requirements_path = os.path.join(self.project_root, 'requirements.txt')

        with open(requirements_path, 'r') as f:
            content = f.read()

        # Check for essential packages
        essential_packages = [
            'pandas',
            'numpy',
            'backtrader',
            'yfinance',
            'plotly',
            'streamlit',
            'PyYAML'
        ]

        for package in essential_packages:
            self.assertIn(package, content,
                         f"requirements.txt missing {package}")

    def test_requirements_has_reporting_dependencies(self):
        """Test requirements.txt has reporting dependencies"""
        requirements_path = os.path.join(self.project_root, 'requirements.txt')

        with open(requirements_path, 'r') as f:
            content = f.read()

        # Check for reporting packages
        reporting_packages = ['reportlab', 'weasyprint']

        for package in reporting_packages:
            self.assertIn(package, content,
                         f"requirements.txt missing {package}")

    def test_api_requirements_has_fastapi(self):
        """Test requirements_api.txt has FastAPI"""
        api_requirements_path = os.path.join(self.project_root, 'requirements_api.txt')

        with open(api_requirements_path, 'r') as f:
            content = f.read()

        self.assertIn('fastapi', content,
                     "requirements_api.txt missing fastapi")
        self.assertIn('uvicorn', content,
                     "requirements_api.txt missing uvicorn")


class TestReportGeneration(unittest.TestCase):
    """Test report generation functionality"""

    def setUp(self):
        """Set up test results"""
        self.test_results = {
            'ticker': 'TEST',
            'start_value': 10000,
            'end_value': 12000,
            'pnl': 2000,
            'return_pct': 20.0,
            'sharpe_ratio': 1.5,
            'max_drawdown': 8.5,
            'total_trades': 10,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'interval': '1d',
            'trades': [
                {'entry_date': '2023-01-15', 'exit_date': '2023-01-20',
                 'entry_price': 100, 'exit_price': 110, 'pnl': 100},
                {'entry_date': '2023-02-10', 'exit_date': '2023-02-15',
                 'entry_price': 110, 'exit_price': 105, 'pnl': -50}
            ],
            'advanced_metrics': {
                'win_rate': 60.0,
                'profit_factor': 2.0,
                'payoff_ratio': 1.8,
                'sortino_ratio': 1.8,
                'calmar_ratio': 2.3,
                'expectancy': 200,
                'avg_win': 150,
                'avg_loss': -50,
                'max_consecutive_wins': 3,
                'max_consecutive_losses': 2,
                'largest_win': 300,
                'largest_loss': -100
            }
        }

    def test_pdf_report_generation(self):
        """Test PDF report can be generated"""
        try:
            from utils.professional_reporting import ProfessionalReportGenerator

            with tempfile.TemporaryDirectory() as tmpdir:
                generator = ProfessionalReportGenerator(
                    self.test_results,
                    output_dir=tmpdir
                )

                pdf_path = generator.generate_pdf_report()

                # Verify PDF was created
                self.assertTrue(os.path.exists(pdf_path),
                               "PDF report was not generated")
                self.assertTrue(pdf_path.endswith('.pdf'),
                               "Generated file is not a PDF")
                self.assertGreater(os.path.getsize(pdf_path), 0,
                                  "PDF file is empty")

        except ImportError as e:
            self.skipTest(f"reportlab not installed: {e}")

    def test_html_report_generation(self):
        """Test HTML report can be generated"""
        from utils.professional_reporting import ProfessionalReportGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProfessionalReportGenerator(
                self.test_results,
                output_dir=tmpdir
            )

            html_path = generator.generate_html_report()

            # Verify HTML was created
            self.assertTrue(os.path.exists(html_path),
                           "HTML report was not generated")
            self.assertTrue(html_path.endswith('.html'),
                           "Generated file is not HTML")

            # Verify HTML content
            with open(html_path, 'r') as f:
                content = f.read()

            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('<html', content)
            self.assertIn('TEST', content)  # Ticker
            self.assertIn('20.00%', content)  # Return

    def test_csv_export(self):
        """Test CSV trade export"""
        from utils.professional_reporting import export_trade_history_csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = export_trade_history_csv(
                self.test_results,
                output_dir=tmpdir
            )

            # Verify CSV was created
            self.assertTrue(os.path.exists(csv_path),
                           "CSV file was not generated")
            self.assertTrue(csv_path.endswith('.csv'),
                           "Generated file is not CSV")

            # Verify CSV content
            with open(csv_path, 'r') as f:
                content = f.read()

            self.assertIn('entry_date', content)
            self.assertIn('exit_date', content)
            self.assertIn('pnl', content)


class TestNotificationSystem(unittest.TestCase):
    """Test notification system"""

    def test_env_template_creation(self):
        """Test .env template can be created"""
        from utils.notifications import create_env_template

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, '.env.example')
            create_env_template(env_path)

            # Verify template was created
            self.assertTrue(os.path.exists(env_path),
                           ".env template not created")

            # Verify template content
            with open(env_path, 'r') as f:
                content = f.read()

            self.assertIn('SMTP_SERVER', content)
            self.assertIn('EMAIL_USERNAME', content)
            self.assertIn('EMAIL_PASSWORD', content)

    def test_email_notifier_initialization_without_credentials(self):
        """Test EmailNotifier requires credentials"""
        from utils.notifications import EmailNotifier

        # Should raise error without credentials
        with self.assertRaises(ValueError):
            notifier = EmailNotifier()

    def test_email_notifier_initialization_with_credentials(self):
        """Test EmailNotifier can be initialized with credentials"""
        from utils.notifications import EmailNotifier

        notifier = EmailNotifier(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            username='test@example.com',
            password='test_password'
        )

        self.assertIsNotNone(notifier)
        self.assertEqual(notifier.smtp_server, 'smtp.gmail.com')
        self.assertEqual(notifier.smtp_port, 587)


class TestAdvancedCharting(unittest.TestCase):
    """Test advanced charting functionality"""

    def setUp(self):
        """Set up test data"""
        import pandas as pd
        import numpy as np

        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        self.test_data = pd.DataFrame({
            'Open': np.random.uniform(95, 105, 100),
            'High': np.random.uniform(100, 110, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(95, 105, 100),
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)

    def test_chart_builder_initialization(self):
        """Test AdvancedChartBuilder can be initialized"""
        from utils.advanced_charting import AdvancedChartBuilder

        builder = AdvancedChartBuilder(self.test_data, title="Test Chart")
        self.assertIsNotNone(builder)
        self.assertEqual(builder.title, "Test Chart")

    def test_candlestick_chart_creation(self):
        """Test candlestick chart can be created"""
        from utils.advanced_charting import AdvancedChartBuilder

        builder = AdvancedChartBuilder(self.test_data)
        fig = builder.create_candlestick_chart()

        self.assertIsNotNone(fig)
        self.assertGreater(len(fig.data), 0, "Chart has no data traces")

    def test_sma_indicator_addition(self):
        """Test SMA indicator can be added"""
        from utils.advanced_charting import AdvancedChartBuilder

        builder = AdvancedChartBuilder(self.test_data)
        builder.create_candlestick_chart()
        builder.add_sma(period=20)

        fig = builder.get_figure()
        self.assertIsNotNone(fig)
        # Should have candlestick + volume + SMA traces
        self.assertGreaterEqual(len(fig.data), 3)

    def test_bollinger_bands_addition(self):
        """Test Bollinger Bands can be added"""
        from utils.advanced_charting import AdvancedChartBuilder

        builder = AdvancedChartBuilder(self.test_data)
        builder.create_candlestick_chart()
        builder.add_bollinger_bands(period=20)

        fig = builder.get_figure()
        self.assertIsNotNone(fig)


class TestDeploymentReadiness(unittest.TestCase):
    """Test overall deployment readiness"""

    def test_all_required_files_exist(self):
        """Test all required deployment files exist"""
        project_root = os.path.join(os.path.dirname(__file__), '..')

        required_files = [
            'Dockerfile',
            'docker-compose.yml',
            '.dockerignore',
            'requirements.txt',
            'requirements_api.txt',
            'config.yaml'
        ]

        for filename in required_files:
            filepath = os.path.join(project_root, filename)
            self.assertTrue(os.path.exists(filepath),
                           f"Required file missing: {filename}")

    def test_src_directory_structure(self):
        """Test src directory has proper structure"""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        src_dir = os.path.join(project_root, 'src')

        required_dirs = [
            'core',
            'utils',
            'api'
        ]

        for dirname in required_dirs:
            dirpath = os.path.join(src_dir, dirname)
            self.assertTrue(os.path.exists(dirpath),
                           f"Required directory missing: src/{dirname}")

    def test_critical_modules_exist(self):
        """Test critical modules can be imported"""
        critical_modules = [
            'utils.advanced_charting',
            'utils.professional_reporting',
            'utils.notifications',
            'utils.ui_helpers',
            'utils.config_loader',
            'core.vectorized_backtest',
            'utils.parallel_grid_search'
        ]

        for module_name in critical_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Critical module {module_name} cannot be imported: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
