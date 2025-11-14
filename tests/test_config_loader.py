"""Unit tests for ConfigLoader"""

import os
import sys
import unittest
import tempfile
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """Test suite for ConfigLoader class"""

    def setUp(self):
        """Set up test configuration file"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yaml')

        test_config = {
            'data_manager': {
                'cache_path': './test_cache.db',
                'update_schedule': 'daily'
            },
            'strategies': {
                'bollinger_bands': {
                    'default_params': {'period': 20}
                }
            },
            'walk_forward': {
                'train_period_months': 12,
                'test_period_months': 3
            }
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_load_config(self):
        """Test loading configuration from file"""
        loader = ConfigLoader(self.config_path)

        self.assertIsNotNone(loader.config)
        self.assertIn('data_manager', loader.config)

    def test_get_simple_key(self):
        """Test getting simple configuration key"""
        loader = ConfigLoader(self.config_path)

        value = loader.get('data_manager.cache_path')

        self.assertEqual(value, './test_cache.db')

    def test_get_nested_key(self):
        """Test getting nested configuration key"""
        loader = ConfigLoader(self.config_path)

        value = loader.get('strategies.bollinger_bands.default_params.period')

        self.assertEqual(value, 20)

    def test_get_with_default(self):
        """Test getting non-existent key with default"""
        loader = ConfigLoader(self.config_path)

        value = loader.get('nonexistent.key', default='default_value')

        self.assertEqual(value, 'default_value')

    def test_get_data_manager_config(self):
        """Test getting data manager configuration"""
        loader = ConfigLoader(self.config_path)

        config = loader.get_data_manager_config()

        self.assertIsInstance(config, dict)
        self.assertEqual(config['cache_path'], './test_cache.db')

    def test_get_strategy_config(self):
        """Test getting strategy-specific configuration"""
        loader = ConfigLoader(self.config_path)

        config = loader.get_strategy_config('bollinger_bands')

        self.assertIsInstance(config, dict)
        self.assertIn('default_params', config)

    def test_get_walk_forward_config(self):
        """Test getting walk-forward configuration"""
        loader = ConfigLoader(self.config_path)

        config = loader.get_walk_forward_config()

        self.assertEqual(config['train_period_months'], 12)
        self.assertEqual(config['test_period_months'], 3)

    def test_load_nonexistent_file(self):
        """Test loading configuration from nonexistent file"""
        loader = ConfigLoader('/nonexistent/path/config.yaml')

        self.assertIsNotNone(loader.config)
        self.assertIn('data_manager', loader.config)

    def test_default_config(self):
        """Test default configuration is valid"""
        loader = ConfigLoader('/nonexistent/config.yaml')
        default = loader._get_default_config()

        self.assertIn('data_manager', default)
        self.assertIn('backtesting', default)
        self.assertIn('walk_forward', default)


if __name__ == '__main__':
    unittest.main()
