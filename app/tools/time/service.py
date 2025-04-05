#!/usr/bin/env python3
"""
Time utilities service for timezone conversions and time information.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo
import logging

from app.tools.base.service import ToolServiceBase


class TimeService(ToolServiceBase):
    """Service to handle time operations with enhanced features"""

    def __init__(self):
        """Initialize the time service"""
        super().__init__()

    def initialize(self) -> bool:
        """
        Initialize the time service.

        Returns:
            bool: True if initialization was successful
        """
        try:
            # Verify that zoneinfo module is working
            ZoneInfo("UTC")

            self.logger.info("Time service initialized successfully")
            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize time service: {e}")
            return False

    def get_local_tz(self, local_tz_override: Optional[str] = None) -> ZoneInfo:
        """
        Get local timezone.

        Args:
            local_tz_override: Optional timezone override

        Returns:
            ZoneInfo object for the timezone

        Raises:
            ValueError: If timezone cannot be determined
        """
        self._is_initialized()

        if local_tz_override:
            return ZoneInfo(local_tz_override)

        # Get local timezone from datetime.now()
        tzinfo = datetime.now().astimezone(tz=None).tzinfo
        if tzinfo is not None:
            return ZoneInfo(str(tzinfo))
        raise ValueError("Could not determine local timezone - tzinfo is None")

    def get_zoneinfo(self, timezone_name: str) -> ZoneInfo:
        """
        Get ZoneInfo object for a timezone.

        Args:
            timezone_name: Name of the timezone

        Returns:
            ZoneInfo object for the timezone

        Raises:
            ValueError: If timezone is invalid
        """
        self._is_initialized()

        try:
            return ZoneInfo(timezone_name)
        except Exception as e:
            raise ValueError(f"Invalid timezone: {str(e)}")

    async def get_current_time(self, timezone: str) -> Dict[str, Any]:
        """
        Get current time in specified timezone.

        Args:
            timezone: Name of the timezone

        Returns:
            Dictionary with timezone and time information

        Raises:
            ValueError: If timezone is invalid
        """
        self._is_initialized()

        try:
            timezone_obj = self.get_zoneinfo(timezone)
            current_time = datetime.now(timezone_obj)

            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")

            result = {
                "timezone": timezone,
                "datetime": current_time.isoformat(timespec="seconds"),
                "formatted": formatted_time,
                "date": current_time.strftime("%Y-%m-%d"),
                "time": current_time.strftime("%H:%M:%S"),
                "is_dst": bool(current_time.dst()),
                "unix_timestamp": int(current_time.timestamp())
            }

            return result
        except Exception as e:
            self.logger.error(f"Error processing time query: {e}")
            raise ValueError(f"Error processing time query: {str(e)}")

    async def convert_time(
        self,
        source_timezone: str,
        time: str,
        target_timezone: str
    ) -> Dict[str, Any]:
        """
        Convert time between timezones.

        Args:
            source_timezone: Source timezone name
            time: Time string in HH:MM format
            target_timezone: Target timezone name

        Returns:
            Dictionary with conversion result

        Raises:
            ValueError: If conversion fails
        """
        self._is_initialized()

        try:
            source_timezone_obj = self.get_zoneinfo(source_timezone)
            target_timezone_obj = self.get_zoneinfo(target_timezone)

            # Parse time string
            try:
                # First try ISO format
                try:
                    parsed_time = datetime.fromisoformat(time)
                    # If time string has no timezone info, add source timezone
                    if parsed_time.tzinfo is None:
                        parsed_time = parsed_time.replace(
                            tzinfo=source_timezone_obj)
                except ValueError:
                    # Then try HH:MM format
                    try:
                        parsed_time_obj = datetime.strptime(
                            time, "%H:%M").time()
                        # Use current date with the parsed time
                        now = datetime.now(source_timezone_obj)
                        parsed_time = datetime(
                            now.year,
                            now.month,
                            now.day,
                            parsed_time_obj.hour,
                            parsed_time_obj.minute,
                            tzinfo=source_timezone_obj,
                        )
                    except ValueError:
                        # Try more formats
                        try:
                            parsed_time_obj = datetime.strptime(
                                time, "%H:%M:%S").time()
                            now = datetime.now(source_timezone_obj)
                            parsed_time = datetime(
                                now.year,
                                now.month,
                                now.day,
                                parsed_time_obj.hour,
                                parsed_time_obj.minute,
                                parsed_time_obj.second,
                                tzinfo=source_timezone_obj,
                            )
                        except ValueError:
                            raise ValueError(
                                "Invalid time format. Expected HH:MM or HH:MM:SS [24-hour format] or ISO format"
                            )
            except Exception as e:
                self.logger.error(f"Error parsing time: {e}")
                raise ValueError(f"Error parsing time: {str(e)}")

            # Convert to target timezone
            target_time = parsed_time.astimezone(target_timezone_obj)

            # Calculate time difference
            source_offset = parsed_time.utcoffset() or timedelta()
            target_offset = target_time.utcoffset() or timedelta()
            hours_difference = (
                target_offset - source_offset).total_seconds() / 3600

            if hours_difference.is_integer():
                time_diff_str = f"{hours_difference:+.1f}h".replace(".0", "")
            else:
                # For fractional hours like Nepal's UTC+5:45
                time_diff_str = f"{hours_difference:+.2f}".rstrip(
                    "0").rstrip(".") + "h"

            # Format results
            source_result = {
                "timezone": source_timezone,
                "datetime": parsed_time.isoformat(timespec="seconds"),
                "formatted": parsed_time.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
                "date": parsed_time.strftime("%Y-%m-%d"),
                "time": parsed_time.strftime("%H:%M:%S"),
                "is_dst": bool(parsed_time.dst())
            }

            target_result = {
                "timezone": target_timezone,
                "datetime": target_time.isoformat(timespec="seconds"),
                "formatted": target_time.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
                "date": target_time.strftime("%Y-%m-%d"),
                "time": target_time.strftime("%H:%M:%S"),
                "is_dst": bool(target_time.dst())
            }

            result = {
                "source": source_result,
                "target": target_result,
                "time_difference": time_diff_str,
                "hours_difference": hours_difference,
                "minutes_difference": hours_difference * 60,
                "same_day": parsed_time.date() == target_time.date()
            }

            return result
        except Exception as e:
            self.logger.error(f"Error processing time conversion: {e}")
            raise ValueError(f"Error processing time conversion: {str(e)}")
