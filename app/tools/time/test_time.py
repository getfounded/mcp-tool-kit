#!/usr/bin/env python3
"""
Tests for Time tools.
"""
import pytest
import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from zoneinfo import ZoneInfo

from app.tools.time.time_service import TimeService
from app.tools.time.time_tools import get_current_time, convert_time

class TestTimeTools:
    """Test case for time tools."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        # Initialize service
        cls.service = TimeService()
        cls.service.initialized = True
    
    @pytest.mark.asyncio
    async def test_get_current_time(self):
        """Test get_current_time function."""
        # Test with UTC timezone
        result = await get_current_time(self.service, "UTC")
        
        # Verify result structure
        assert "timezone" in result
        assert result["timezone"] == "UTC"
        assert "datetime" in result
        assert "formatted" in result
        assert "date" in result
        assert "time" in result
        assert "is_dst" in result
        assert "unix_timestamp" in result
        
        # Test with non-existent timezone
        result = await get_current_time(self.service, "NonExistentTZ")
        assert "error" in result
        assert "Invalid timezone" in result["error"]
    
    @pytest.mark.asyncio
    async def test_convert_time(self):
        """Test convert_time function."""
        # Test with valid timezones and time
        result = await convert_time(self.service, "UTC", "12:00", "America/New_York")
        
        # Verify result structure
        assert "source" in result
        assert "target" in result
        assert "time_difference" in result
        assert "hours_difference" in result
        assert "minutes_difference" in result
        assert "same_day" in result
        
        # Verify source timezone
        assert result["source"]["timezone"] == "UTC"
        assert result["source"]["time"] == "12:00:00"
        
        # Verify target timezone
        assert result["target"]["timezone"] == "America/New_York"
        
        # Verify time difference (may vary due to DST)
        assert isinstance(result["hours_difference"], float)
        
        # Test with HH:MM:SS format
        result = await convert_time(self.service, "UTC", "14:30:45", "Europe/London")
        assert result["source"]["time"] == "14:30:45"
        
        # Test with invalid time format
        result = await convert_time(self.service, "UTC", "invalid", "Europe/London")
        assert "error" in result
        assert "Invalid time format" in result["error"]
        
        # Test with invalid timezone
        result = await convert_time(self.service, "UTC", "12:00", "NonExistentTZ")
        assert "error" in result
        assert "Invalid timezone" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_zoneinfo(self):
        """Test get_zoneinfo method."""
        # Test with valid timezone
        zone_info = self.service.get_zoneinfo("UTC")
        assert isinstance(zone_info, ZoneInfo)
        assert str(zone_info) == "UTC"
        
        # Test with invalid timezone
        with pytest.raises(ValueError):
            self.service.get_zoneinfo("NonExistentTZ")
    
    @pytest.mark.asyncio
    @patch.object(TimeService, 'get_zoneinfo')
    @patch('datetime.datetime')
    async def test_time_conversion_fixed_time(self, mock_datetime, mock_get_zoneinfo):
        """Test time conversion with mocked datetime for consistent results."""
        # Create mock ZoneInfo objects
        mock_utc = MagicMock()
        mock_utc.__str__.return_value = "UTC"
        
        mock_est = MagicMock()
        mock_est.__str__.return_value = "America/New_York"
        
        # Configure mock ZoneInfo to return our mock objects
        mock_get_zoneinfo.side_effect = lambda tz: mock_utc if tz == "UTC" else mock_est
        
        # Configure mock datetime
        mock_now = MagicMock()
        mock_now.year = 2023
        mock_now.month = 1
        mock_now.day = 1
        mock_datetime.now.return_value = mock_now
        
        # Create mock datetime objects for source and target times
        mock_source_time = MagicMock()
        mock_source_time.isoformat.return_value = "2023-01-01T12:00:00+00:00"
        mock_source_time.strftime.side_effect = lambda fmt: "2023-01-01 12:00:00 UTC+0000" if "%Z" in fmt else "12:00:00" if "%H" in fmt else "2023-01-01"
        mock_source_time.dst.return_value = None
        mock_source_time.date.return_value = "2023-01-01"
        
        mock_target_time = MagicMock()
        mock_target_time.isoformat.return_value = "2023-01-01T07:00:00-05:00"
        mock_target_time.strftime.side_effect = lambda fmt: "2023-01-01 07:00:00 EST-0500" if "%Z" in fmt else "07:00:00" if "%H" in fmt else "2023-01-01"
        mock_target_time.dst.return_value = None
        mock_target_time.date.return_value = "2023-01-01"
        
        # Configure mock datetime.strptime to return a time object
        mock_parsed_time = MagicMock()
        mock_parsed_time.hour = 12
        mock_parsed_time.minute = 0
        mock_datetime.strptime.return_value = mock_parsed_time
        
        # Configure mock datetime constructor to return our mock times
        mock_datetime.side_effect = lambda year, month, day, hour, minute, tzinfo=None: mock_source_time
        
        # Configure mock astimezone to return mock_target_time
        mock_source_time.astimezone.return_value = mock_target_time
        
        # Configure mock utcoffset
        mock_source_time.utcoffset.return_value = datetime.timedelta(hours=0)
        mock_target_time.utcoffset.return_value = datetime.timedelta(hours=-5)
        
        # Test the conversion
        with patch.object(self.service, 'get_zoneinfo', mock_get_zoneinfo):
            result = await convert_time(self.service, "UTC", "12:00", "America/New_York")
        
        # Verify the result
        assert result["source"]["timezone"] == "UTC"
        assert result["target"]["timezone"] == "America/New_York"
        assert result["time_difference"] == "-5h"
        assert result["hours_difference"] == -5
        assert result["minutes_difference"] == -300
        assert result["same_day"] is True

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
