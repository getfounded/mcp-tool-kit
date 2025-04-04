#!/usr/bin/env python3
"""
YFinance service implementation for stock market data.
"""
import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from app.tools.base.service import ToolServiceBase

class YFinanceService(ToolServiceBase):
    """Service to handle YFinance operations with enhanced features"""

    def __init__(self):
        """Initialize the YFinance service"""
        super().__init__()
        self.yf = None
        self.throttle_calls = 5  # Default throttle settings
        self.throttle_period = 60  # Default 60 seconds
        
    def initialize(self) -> bool:
        """
        Initialize the YFinance service with configuration.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Import yfinance module
            import yfinance as yf
            self.yf = yf
            
            # Get throttle configuration from environment
            self.throttle_calls = int(self.get_env_var("YFINANCE_THROTTLE_CALLS", default="5"))
            self.throttle_period = float(self.get_env_var("YFINANCE_THROTTLE_PERIOD", default="60"))
            
            # Create rate limiter
            self.create_rate_limiter("yfinance_api", self.throttle_calls, self.throttle_period)
            
            self.logger.info(f"YFinance service initialized with rate limit: {self.throttle_calls} calls per {self.throttle_period}s")
            self.initialized = True
            return True
            
        except ImportError:
            self.logger.error("yfinance library not installed. Please install with 'pip install yfinance'")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize YFinance service: {e}")
            return False
    
    def _sanitize_data(self, data: Any) -> Any:
        """
        Convert data to JSON-serializable format.
        
        Args:
            data: Data to sanitize
            
        Returns:
            JSON-serializable data
        """
        if isinstance(data, pd.DataFrame):
            # Reset index if it's a date or complex object
            if not isinstance(data.index, pd.RangeIndex):
                data = data.reset_index()

            # Handle NaN values
            return json.loads(data.replace({np.nan: None}).to_json(orient='records', date_format='iso'))

        elif isinstance(data, pd.Series):
            return json.loads(data.replace({np.nan: None}).to_json())

        elif isinstance(data, dict):
            # Recursively convert each value
            return {k: self._sanitize_data(v) for k, v in data.items()}

        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]

        elif isinstance(data, (np.integer, np.floating)):
            return int(data) if isinstance(data, np.integer) else float(data)

        elif isinstance(data, (datetime, np.datetime64)):
            return data.isoformat()

        elif pd.isna(data):
            return None

        return data

    def get_ticker_info(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get basic information about a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with ticker information
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)
            info = ticker.info

            # Clean up data for JSON serialization
            cleaned_info = self._sanitize_data(info)

            return {
                "symbol": ticker_symbol,
                "info": cleaned_info
            }
        except Exception as e:
            self.logger.error(f"Error retrieving ticker info: {e}")
            return {"error": f"Error retrieving ticker info: {str(e)}"}

    def get_historical_data(
        self, 
        ticker_symbol: str, 
        period: str = "1mo", 
        interval: str = "1d", 
        start: Optional[str] = None, 
        end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical market data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            period: Data period to download
            interval: Data interval
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with historical data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            # If start and end dates are provided, use them instead of period
            if start and end:
                history = ticker.history(
                    start=start, end=end, interval=interval)
            else:
                history = ticker.history(period=period, interval=interval)

            # Clean up data for JSON serialization
            cleaned_history = self._sanitize_data(history)

            return {
                "symbol": ticker_symbol,
                "period": period if not (start and end) else f"{start} to {end}",
                "interval": interval,
                "data": cleaned_history
            }
        except Exception as e:
            self.logger.error(f"Error retrieving historical data: {e}")
            return {"error": f"Error retrieving historical data: {str(e)}"}
    
    def get_financials(self, ticker_symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get income statement data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            quarterly: If True, get quarterly data instead of annual
            
        Returns:
            Dictionary with financial data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                financials = ticker.quarterly_financials
            else:
                financials = ticker.financials

            # Clean up data for JSON serialization
            cleaned_financials = self._sanitize_data(financials)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "financials": cleaned_financials
            }
        except Exception as e:
            self.logger.error(f"Error retrieving financials: {e}")
            return {"error": f"Error retrieving financials: {str(e)}"}
    
    def get_balance_sheet(self, ticker_symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get balance sheet data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            quarterly: If True, get quarterly data instead of annual
            
        Returns:
            Dictionary with balance sheet data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                balance_sheet = ticker.quarterly_balance_sheet
            else:
                balance_sheet = ticker.balance_sheet

            # Clean up data for JSON serialization
            cleaned_balance_sheet = self._sanitize_data(balance_sheet)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "balance_sheet": cleaned_balance_sheet
            }
        except Exception as e:
            self.logger.error(f"Error retrieving balance sheet: {e}")
            return {"error": f"Error retrieving balance sheet: {str(e)}"}
    
    def get_cashflow(self, ticker_symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get cash flow data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            quarterly: If True, get quarterly data instead of annual
            
        Returns:
            Dictionary with cash flow data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                cashflow = ticker.quarterly_cashflow
            else:
                cashflow = ticker.cashflow

            # Clean up data for JSON serialization
            cleaned_cashflow = self._sanitize_data(cashflow)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "cashflow": cleaned_cashflow
            }
        except Exception as e:
            self.logger.error(f"Error retrieving cashflow: {e}")
            return {"error": f"Error retrieving cashflow: {str(e)}"}
    
    def get_earnings(self, ticker_symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get earnings data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            quarterly: If True, get quarterly data instead of annual
            
        Returns:
            Dictionary with earnings data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                earnings = ticker.quarterly_earnings
            else:
                earnings = ticker.earnings

            # Clean up data for JSON serialization
            cleaned_earnings = self._sanitize_data(earnings)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "earnings": cleaned_earnings
            }
        except Exception as e:
            self.logger.error(f"Error retrieving earnings: {e}")
            return {"error": f"Error retrieving earnings: {str(e)}"}
    
    def get_major_holders(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get major shareholders for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with major shareholders data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)
            major_holders = ticker.major_holders

            # Clean up data for JSON serialization
            cleaned_holders = self._sanitize_data(major_holders)

            return {
                "symbol": ticker_symbol,
                "major_holders": cleaned_holders
            }
        except Exception as e:
            self.logger.error(f"Error retrieving major holders: {e}")
            return {"error": f"Error retrieving major holders: {str(e)}"}
    
    def get_institutional_holders(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get institutional shareholders for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with institutional shareholders data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)
            institutional_holders = ticker.institutional_holders

            # Clean up data for JSON serialization
            cleaned_holders = self._sanitize_data(institutional_holders)

            return {
                "symbol": ticker_symbol,
                "institutional_holders": cleaned_holders
            }
        except Exception as e:
            self.logger.error(f"Error retrieving institutional holders: {e}")
            return {"error": f"Error retrieving institutional holders: {str(e)}"}
    
    def get_recommendations(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get analyst recommendations for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with analyst recommendations
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)
            recommendations = ticker.recommendations

            # Clean up data for JSON serialization
            cleaned_recommendations = self._sanitize_data(recommendations)

            return {
                "symbol": ticker_symbol,
                "recommendations": cleaned_recommendations
            }
        except Exception as e:
            self.logger.error(f"Error retrieving recommendations: {e}")
            return {"error": f"Error retrieving recommendations: {str(e)}"}
    
    def get_calendar(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get earnings calendar for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with earnings calendar data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)
            calendar = ticker.calendar

            # Clean up data for JSON serialization
            cleaned_calendar = self._sanitize_data(calendar)

            return {
                "symbol": ticker_symbol,
                "calendar": cleaned_calendar
            }
        except Exception as e:
            self.logger.error(f"Error retrieving calendar: {e}")
            return {"error": f"Error retrieving calendar: {str(e)}"}
    
    def get_options(self, ticker_symbol: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get options chain data for a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            date: Options expiration date (YYYY-MM-DD)
            
        Returns:
            Dictionary with options data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            # Get available expiration dates if no date specified
            expiration_dates = ticker.options

            if not expiration_dates:
                return {
                    "symbol": ticker_symbol,
                    "error": "No options data available for this ticker"
                }

            # Use the first available date if none specified
            selected_date = date if date and date in expiration_dates else expiration_dates[0]

            # Get options chain for the selected date
            calls = ticker.option_chain(selected_date).calls
            puts = ticker.option_chain(selected_date).puts

            # Clean up data for JSON serialization
            cleaned_calls = self._sanitize_data(calls)
            cleaned_puts = self._sanitize_data(puts)

            return {
                "symbol": ticker_symbol,
                "expiration_date": selected_date,
                "available_dates": expiration_dates,
                "calls": cleaned_calls,
                "puts": cleaned_puts
            }
        except Exception as e:
            self.logger.error(f"Error retrieving options data: {e}")
            return {"error": f"Error retrieving options data: {str(e)}"}
    
    def get_news(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get recent news about a ticker.
        
        Args:
            ticker_symbol: The stock ticker symbol
            
        Returns:
            Dictionary with news articles
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            ticker = self.yf.Ticker(ticker_symbol)

            # Some versions of yfinance have news, others don't
            if hasattr(ticker, 'news'):
                news = ticker.news

                # Clean up data for JSON serialization
                cleaned_news = self._sanitize_data(news)

                return {
                    "symbol": ticker_symbol,
                    "news": cleaned_news
                }
            else:
                return {
                    "symbol": ticker_symbol,
                    "error": "News not available in this version of yfinance"
                }
        except Exception as e:
            self.logger.error(f"Error retrieving news: {e}")
            return {"error": f"Error retrieving news: {str(e)}"}
    
    def search_ticker(self, query: str) -> Dict[str, Any]:
        """
        Search for ticker symbols matching a query.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with search results
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            # yfinance doesn't have a built-in search function, but we can use Ticker to get summary
            try:
                ticker = self.yf.Ticker(query)
                if 'symbol' in ticker.info:
                    # This is a valid ticker
                    return {
                        "query": query,
                        "results": [
                            {
                                "symbol": ticker.info['symbol'],
                                "name": ticker.info.get('longName', ''),
                                "exchange": ticker.info.get('exchange', '')
                            }
                        ]
                    }
                else:
                    return {"query": query, "results": []}
            except:
                return {"query": query, "results": []}
        except Exception as e:
            self.logger.error(f"Error searching ticker: {e}")
            return {"error": f"Error searching ticker: {str(e)}"}
    
    def download_data(
        self, 
        tickers: Union[str, List[str]], 
        period: str = "1mo", 
        interval: str = "1d", 
        start: Optional[str] = None, 
        end: Optional[str] = None, 
        group_by: str = "ticker", 
        threads: bool = True
    ) -> Dict[str, Any]:
        """
        Download historical market data for multiple tickers.
        
        Args:
            tickers: Single ticker string or list of ticker symbols
            period: Data period to download
            interval: Data interval
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            group_by: How to group the data
            threads: Whether to use multi-threading
            
        Returns:
            Dictionary with downloaded data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("yfinance_api", self.throttle_calls, self.throttle_period)
        
        try:
            # Convert single ticker to list if needed
            if isinstance(tickers, str):
                tickers = [tickers]

            # If start and end dates are provided, use them instead of period
            if start and end:
                data = self.yf.download(
                    tickers=tickers,
                    start=start,
                    end=end,
                    interval=interval,
                    group_by=group_by,
                    threads=threads
                )
            else:
                data = self.yf.download(
                    tickers=tickers,
                    period=period,
                    interval=interval,
                    group_by=group_by,
                    threads=threads
                )

            # Clean up data for JSON serialization
            cleaned_data = self._sanitize_data(data)

            return {
                "tickers": tickers,
                "period": period if not (start and end) else f"{start} to {end}",
                "interval": interval,
                "data": cleaned_data
            }
        except Exception as e:
            self.logger.error(f"Error downloading data: {e}")
            return {"error": f"Error downloading data: {str(e)}"}
