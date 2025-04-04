#!/usr/bin/env python3
"""
Time utilities implementation using the decorator pattern.
"""
from typing import Dict, Any

from app.tools.base.registry import register_tool
from app.tools.time.time_service import TimeService

@register_tool(
    category="utility",
    service_class=TimeService,
    description="Get current time in specified timezone"
)
async def get_current_time(self, timezone: str) -> Dict[str, Any]:
    """
    Get current time in specified timezone.
    
    Retrieves the current time, date, and timezone information for the specified timezone.
    
    Args:
        timezone: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')
    
    Returns:
        Dictionary with current time information
    """
    try:
        return await self.get_current_time(timezone)
    except Exception as e:
        return {"error": f"Error processing time query: {str(e)}"}

@register_tool(
    category="utility",
    service_class=TimeService,
    description="Convert time between timezones"
)
async def convert_time(
    self,
    source_timezone: str,
    time: str,
    target_timezone: str
) -> Dict[str, Any]:
    """
    Convert time between timezones.
    
    Converts a specified time from one timezone to another, providing detailed
    information about both times and the time difference.
    
    Args:
        source_timezone: Source timezone name (e.g., 'America/New_York')
        time: Time to convert in HH:MM or HH:MM:SS format [24-hour]
        target_timezone: Target timezone name (e.g., 'Europe/London')
    
    Returns:
        Dictionary with time conversion result
    """
    try:
        return await self.convert_time(source_timezone, time, target_timezone)
    except Exception as e:
        return {"error": f"Error processing time conversion: {str(e)}"}
