"""Comprehensive unit tests for DataManager"""

import os
import sys
import unittest
import datetime
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """Test suite for DataManager class"""

    def setUp(self):
        """Set up test database in temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_data.db')
        self.dm = DataManager(db_path=self.db_path)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_init_creates_database(self):
        """Test that initialization creates database file"""
        self.assertTrue(os.path.exists(self.db_path))

    def test_database_tables_created(self):
        """Test that required tables are created"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn('ohlcv_data', tables)
        self.assertIn('data_metadata', tables)

        conn.close()

    def test_cache_data(self):
        """Test caching data to database"""
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))

        self.dm._cache_data('TEST', test_data, '1d')

        cached = self.dm._get_cached_data(
            'TEST',
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 3),
            '1d'
        )

        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 3)
        self.assertAlmostEqual(cached['Close'].iloc[0], 104)

    def test_get_cached_data_empty(self):
        """Test retrieving non-existent cached data"""
        result = self.dm._get_cached_data(
            'NONEXISTENT',
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31),
            '1d'
        )

        self.assertIsNone(result)

    def test_clean_and_validate_data_removes_nans(self):
        """Test data cleaning removes NaN values"""
        test_data = pd.DataFrame({
            'Open': [100, None, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })

        cleaned = self.dm._clean_and_validate_data(test_data)

        self.assertEqual(len(cleaned), 2)
        self.assertFalse(cleaned.isnull().any().any())

    def test_clean_and_validate_data_removes_invalid_prices(self):
        """Test data cleaning removes invalid price data"""
        test_data = pd.DataFrame({
            'Open': [100, -5, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })

        cleaned = self.dm._clean_and_validate_data(test_data)

        self.assertEqual(len(cleaned), 2)
        self.assertTrue((cleaned['Open'] > 0).all())

    def test_clean_and_validate_data_removes_invalid_high_low(self):
        """Test data cleaning removes data where High < Low"""
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 95, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })

        cleaned = self.dm._clean_and_validate_data(test_data)

        self.assertEqual(len(cleaned), 2)

    def test_clean_and_validate_data_validates_ohlc_relationships(self):
        """Test that OHLC relationships are validated"""
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [110, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })

        cleaned = self.dm._clean_and_validate_data(test_data)

        self.assertEqual(len(cleaned), 2)

    def test_is_cache_complete_true(self):
        """Test cache completeness check when data is complete"""
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))

        is_complete = self.dm._is_cache_complete(
            test_data,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 3)
        )

        self.assertTrue(is_complete)

    def test_is_cache_complete_false(self):
        """Test cache completeness check when data is incomplete"""
        test_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [105, 106],
            'Low': [99, 100],
            'Close': [104, 105],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range('2024-01-01', periods=2))

        is_complete = self.dm._is_cache_complete(
            test_data,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 10)
        )

        self.assertFalse(is_complete)

    def test_is_cache_complete_empty(self):
        """Test cache completeness check with empty data"""
        test_data = pd.DataFrame()

        is_complete = self.dm._is_cache_complete(
            test_data,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31)
        )

        self.assertFalse(is_complete)

    @patch('core.data_manager.yf.download')
    def test_get_data_with_force_update(self, mock_download):
        """Test get_data with force_update flag"""
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))
        mock_download.return_value = mock_data

        result = self.dm.get_data(
            'TEST',
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 3),
            force_update=True
        )

        self.assertIsNotNone(result)
        mock_download.assert_called_once()

    def test_get_cache_stats(self):
        """Test cache statistics retrieval"""
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))

        self.dm._cache_data('TEST1', test_data, '1d')
        self.dm._cache_data('TEST2', test_data, '1d')

        stats = self.dm.get_cache_stats()

        self.assertEqual(stats['total_tickers'], 2)
        self.assertEqual(stats['total_rows'], 6)
        self.assertGreater(stats['db_size_mb'], 0)

    def test_clear_cache_specific_ticker(self):
        """Test clearing cache for specific ticker"""
        test_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [105, 106],
            'Low': [99, 100],
            'Close': [104, 105],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range('2024-01-01', periods=2))

        self.dm._cache_data('TEST1', test_data, '1d')
        self.dm._cache_data('TEST2', test_data, '1d')

        self.dm.clear_cache('TEST1')

        stats = self.dm.get_cache_stats()
        self.assertEqual(stats['total_tickers'], 1)

    def test_clear_cache_all(self):
        """Test clearing entire cache"""
        test_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [105, 106],
            'Low': [99, 100],
            'Close': [104, 105],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range('2024-01-01', periods=2))

        self.dm._cache_data('TEST1', test_data, '1d')
        self.dm._cache_data('TEST2', test_data, '1d')

        self.dm.clear_cache()

        stats = self.dm.get_cache_stats()
        self.assertEqual(stats['total_tickers'], 0)
        self.assertEqual(stats['total_rows'], 0)

    def test_get_sp500_tickers(self):
        """Test getting S&P 500 ticker list"""
        tickers = DataManager.get_sp500_tickers()

        self.assertIsInstance(tickers, list)
        self.assertGreater(len(tickers), 0)
        self.assertIn('AAPL', tickers)

    @patch('core.data_manager.yf.download')
    def test_bulk_download_success(self, mock_download):
        """Test bulk download with successful downloads"""
        mock_data = pd.DataFrame({
            'Open': [100],
            'High': [105],
            'Low': [99],
            'Close': [104],
            'Volume': [1000000]
        }, index=pd.date_range('2024-01-01', periods=1))
        mock_download.return_value = mock_data

        results = self.dm.bulk_download(
            ['TEST1', 'TEST2'],
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31)
        )

        self.assertEqual(len(results), 2)
        self.assertTrue(results['TEST1']['success'])
        self.assertTrue(results['TEST2']['success'])

    @patch('core.data_manager.yf.download')
    def test_bulk_download_with_failures(self, mock_download):
        """Test bulk download with some failures"""
        def side_effect(*args, **kwargs):
            if 'FAIL' in args[0]:
                raise ValueError("Download failed")
            return pd.DataFrame({
                'Open': [100],
                'High': [105],
                'Low': [99],
                'Close': [104],
                'Volume': [1000000]
            }, index=pd.date_range('2024-01-01', periods=1))

        mock_download.side_effect = side_effect

        results = self.dm.bulk_download(
            ['SUCCESS', 'FAIL'],
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31)
        )

        self.assertTrue(results['SUCCESS']['success'])
        self.assertFalse(results['FAIL']['success'])
        self.assertIn('error', results['FAIL'])


if __name__ == '__main__':
    unittest.main()
