#!/usr/bin/env python3
"""
Tests for YFinance tools.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime
import json

from app.tools.base.registry import get_all_tools, clear_registry
from app.tools.yfinance.service import YFinanceService
from app.tools.yfinance.tools import (
    yfinance_get_ticker_info,
    yfinance_get_historical_data,
    yfinance_get_financials,
    yfinance_get_balance_sheet,
    yfinance_get_options
)


class TestYFinanceTools(unittest.TestCase):
    """Test cases for YFinance tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Set up environment variables
        os.environ['YFINANCE_THROTTLE_CALLS'] = '5'
        os.environ['YFINANCE_THROTTLE_PERIOD'] = '60'

        # Initialize service
        cls.service = YFinanceService()

        # Create mock yfinance module
        cls.mock_yf = MagicMock()
        cls.service.yf = cls.mock_yf
        cls.service.initialized = True

        # Set up rate limiter
        cls.service.create_rate_limiter("yfinance_api", 5, 60)

    def setUp(self):
        """Set up individual test."""
        # Create mock ticker
        self.mock_ticker = MagicMock()
        self.service.yf.Ticker.return_value = self.mock_ticker

    def test_get_ticker_info(self):
        """Test get_ticker_info method."""
        # Set up mock return values
        self.mock_ticker.info = {
            'symbol': 'AAPL',
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }

        # Call method
        result = yfinance_get_ticker_info(self.service, 'AAPL')

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['info']['longName'], 'Apple Inc.')

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')

    def test_get_historical_data(self):
        """Test get_historical_data method."""
        # Set up mock return values
        mock_history = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [148.0, 149.0, 150.0],
            'Close': [153.0, 154.0, 155.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range(start='2023-01-01', periods=3))

        self.mock_ticker.history.return_value = mock_history

        # Call method
        result = yfinance_get_historical_data(
            self.service, 'AAPL', period='1mo')

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['period'], '1mo')
        self.assertEqual(len(result['data']), 3)

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')
        self.mock_ticker.history.assert_called_once_with(
            period='1mo', interval='1d')

    def test_get_historical_data_with_dates(self):
        """Test get_historical_data method with date range."""
        # Set up mock return values
        mock_history = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [148.0, 149.0, 150.0],
            'Close': [153.0, 154.0, 155.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range(start='2023-01-01', periods=3))

        self.mock_ticker.history.return_value = mock_history

        # Call method
        result = yfinance_get_historical_data(
            self.service,
            'AAPL',
            start='2023-01-01',
            end='2023-01-03'
        )

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['period'], '2023-01-01 to 2023-01-03')
        self.assertEqual(len(result['data']), 3)

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')
        self.mock_ticker.history.assert_called_once_with(
            start='2023-01-01',
            end='2023-01-03',
            interval='1d'
        )

    def test_get_financials(self):
        """Test get_financials method."""
        # Set up mock return values
        mock_financials = pd.DataFrame({
            '2023-01-01': [100000000, 50000000, 50000000],
            '2022-01-01': [90000000, 45000000, 45000000],
            '2021-01-01': [80000000, 40000000, 40000000]
        }, index=['Revenue', 'Expenses', 'Net Income'])

        self.mock_ticker.financials = mock_financials

        # Call method
        result = yfinance_get_financials(self.service, 'AAPL')

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['period'], 'annual')

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')

    def test_get_balance_sheet(self):
        """Test get_balance_sheet method."""
        # Set up mock return values
        mock_balance_sheet = pd.DataFrame({
            '2023-01-01': [200000000, 100000000, 100000000],
            '2022-01-01': [180000000, 90000000, 90000000],
            '2021-01-01': [160000000, 80000000, 80000000]
        }, index=['Assets', 'Liabilities', 'Equity'])

        self.mock_ticker.balance_sheet = mock_balance_sheet

        # Call method
        result = yfinance_get_balance_sheet(self.service, 'AAPL')

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['period'], 'annual')

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')

    def test_get_options(self):
        """Test get_options method."""
        # Set up mock return values
        self.mock_ticker.options = ['2023-01-20', '2023-02-17', '2023-03-17']

        # Mock option chain
        mock_chain = MagicMock()
        mock_chain.calls = pd.DataFrame({
            'strike': [150, 155, 160],
            'lastPrice': [10.5, 8.2, 6.1],
            'bid': [10.4, 8.1, 6.0],
            'ask': [10.6, 8.3, 6.2],
            'volume': [1000, 800, 600],
            'openInterest': [5000, 4000, 3000]
        })
        mock_chain.puts = pd.DataFrame({
            'strike': [150, 155, 160],
            'lastPrice': [5.2, 7.5, 9.8],
            'bid': [5.1, 7.4, 9.7],
            'ask': [5.3, 7.6, 9.9],
            'volume': [800, 1000, 1200],
            'openInterest': [4000, 5000, 6000]
        })

        self.mock_ticker.option_chain.return_value = mock_chain

        # Call method
        result = yfinance_get_options(self.service, 'AAPL')

        # Verify results
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['expiration_date'], '2023-01-20')
        self.assertEqual(len(result['available_dates']), 3)
        self.assertEqual(len(result['calls']), 3)
        self.assertEqual(len(result['puts']), 3)

        # Verify mock calls
        self.service.yf.Ticker.assert_called_once_with('AAPL')
        self.mock_ticker.option_chain.assert_called_once_with('2023-01-20')

    def test_error_handling(self):
        """Test error handling."""
        # Mock a failure
        self.mock_ticker.info.side_effect = Exception("API error")

        # Call method
        result = yfinance_get_ticker_info(self.service, 'AAPL')

        # Verify error is returned
        self.assertIn('error', result)
        self.assertIn('API error', result['error'])


if __name__ == '__main__':
    unittest.main()
