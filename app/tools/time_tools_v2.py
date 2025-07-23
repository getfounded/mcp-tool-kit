#!/usr/bin/env python3
"""Time tools for timezone conversion and current time retrieval."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Callable
from zoneinfo import ZoneInfo
from pydantic import BaseModel
import logging

from app.tools.base_tool import BaseTool
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)


class TimeResult(BaseModel):
    timezone: str
    datetime: str
    is_dst: bool


class TimeConversionResult(BaseModel):
    source: TimeResult
    target: TimeResult
    time_difference: str


class TimeTools(BaseTool):
    """Time tools for working with timezones and time conversion."""
    
    def __init__(self):
        super().__init__()
        
    def get_name(self) -> str:
        return "Time Tools"
        
    def get_description(self) -> str:
        return "Tools for getting current time in different timezones and converting time between timezones"
        
    def get_dependencies(self) -> List[str]:
        return ["pydantic"]
        
    def get_tools(self) -> Dict[str, Callable]:
        return {
            "get_current_time": self.get_current_time,
            "convert_time": self.convert_time
        }
        
    def _get_zoneinfo(self, timezone_name: str) -> ZoneInfo:
        """Get ZoneInfo object for a timezone name."""
        try:
            return ZoneInfo(timezone_name)
        except Exception as e:
            raise ValueError(f"Invalid timezone: {str(e)}")
            
    async def get_current_time(self, timezone: str, ctx: Context = None) -> str:
        """Get current time in specified timezone.
        
        Args:
            timezone: Timezone name (e.g., 'America/New_York', 'Europe/London')
            
        Returns:
            JSON string with timezone, datetime, and DST information
        """
        try:
            timezone_obj = self._get_zoneinfo(timezone)
            current_time = datetime.now(timezone_obj)
            
            result = TimeResult(
                timezone=timezone,
                datetime=current_time.isoformat(timespec="seconds"),
                is_dst=bool(current_time.dst()),
            )
            
            return json.dumps(result.model_dump(), indent=2)
        except Exception as e:
            logger.error(f"Error getting current time: {str(e)}")
            return f"Error processing time query: {str(e)}"
            
    async def convert_time(self, source_timezone: str, time: str, target_timezone: str, ctx: Context = None) -> str:
        """Convert time between timezones.
        
        Args:
            source_timezone: Source timezone (e.g., 'America/New_York')
            time: Time in HH:MM format (24-hour)
            target_timezone: Target timezone (e.g., 'Europe/London')
            
        Returns:
            JSON string with source and target time information
        """
        try:
            source_timezone_obj = self._get_zoneinfo(source_timezone)
            target_timezone_obj = self._get_zoneinfo(target_timezone)
            
            # Parse time
            try:
                parsed_time = datetime.strptime(time, "%H:%M").time()
            except ValueError:
                raise ValueError("Invalid time format. Expected HH:MM [24-hour format]")
                
            # Create datetime objects
            now = datetime.now(source_timezone_obj)
            source_time = datetime(
                now.year,
                now.month,
                now.day,
                parsed_time.hour,
                parsed_time.minute,
                tzinfo=source_timezone_obj,
            )
            
            # Convert to target timezone
            target_time = source_time.astimezone(target_timezone_obj)
            
            # Calculate time difference
            source_offset = source_time.utcoffset() or timedelta()
            target_offset = target_time.utcoffset() or timedelta()
            hours_difference = (target_offset - source_offset).total_seconds() / 3600
            
            if hours_difference.is_integer():
                time_diff_str = f"{hours_difference:+.1f}h"
            else:
                # For fractional hours like Nepal's UTC+5:45
                time_diff_str = f"{hours_difference:+.2f}".rstrip("0").rstrip(".") + "h"
                
            result = TimeConversionResult(
                source=TimeResult(
                    timezone=source_timezone,
                    datetime=source_time.isoformat(timespec="seconds"),
                    is_dst=bool(source_time.dst()),
                ),
                target=TimeResult(
                    timezone=target_timezone,
                    datetime=target_time.isoformat(timespec="seconds"),
                    is_dst=bool(target_time.dst()),
                ),
                time_difference=time_diff_str,
            )
            
            return json.dumps(result.model_dump(), indent=2)
        except Exception as e:
            logger.error(f"Error converting time: {str(e)}")
            return f"Error processing time conversion: {str(e)}"