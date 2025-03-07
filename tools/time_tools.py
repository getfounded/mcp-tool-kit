#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel
import logging

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Time tools MCP reference set")


class TimeTools(str, Enum):
    GET_CURRENT_TIME = "get_current_time"
    CONVERT_TIME = "convert_time"


class TimeResult(BaseModel):
    timezone: str
    datetime: str
    is_dst: bool


class TimeConversionResult(BaseModel):
    source: TimeResult
    target: TimeResult
    time_difference: str


class TimeToolsService:
    """Service to handle time operations"""

    def get_local_tz(self, local_tz_override: str | None = None) -> ZoneInfo:
        if local_tz_override:
            return ZoneInfo(local_tz_override)

        # Get local timezone from datetime.now()
        tzinfo = datetime.now().astimezone(tz=None).tzinfo
        if tzinfo is not None:
            return ZoneInfo(str(tzinfo))
        raise ValueError("Could not determine local timezone - tzinfo is None")

    def get_zoneinfo(self, timezone_name: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone_name)
        except Exception as e:
            raise ValueError(f"Invalid timezone: {str(e)}")

    async def get_current_time(self, timezone: str) -> str:
        """Get current time in specified timezone"""
        try:
            timezone_obj = self.get_zoneinfo(timezone)
            current_time = datetime.now(timezone_obj)

            result = TimeResult(
                timezone=timezone,
                datetime=current_time.isoformat(timespec="seconds"),
                is_dst=bool(current_time.dst()),
            )

            return json.dumps(result.model_dump(), indent=2)
        except Exception as e:
            return f"Error processing time query: {str(e)}"

    async def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """Convert time between timezones"""
        try:
            source_timezone_obj = self.get_zoneinfo(source_timezone)
            target_timezone_obj = self.get_zoneinfo(target_timezone)

            try:
                parsed_time = datetime.strptime(time, "%H:%M").time()
            except ValueError:
                raise ValueError(
                    "Invalid time format. Expected HH:MM [24-hour format]")

            now = datetime.now(source_timezone_obj)
            source_time = datetime(
                now.year,
                now.month,
                now.day,
                parsed_time.hour,
                parsed_time.minute,
                tzinfo=source_timezone_obj,
            )

            target_time = source_time.astimezone(target_timezone_obj)
            source_offset = source_time.utcoffset() or timedelta()
            target_offset = target_time.utcoffset() or timedelta()
            hours_difference = (
                target_offset - source_offset).total_seconds() / 3600

            if hours_difference.is_integer():
                time_diff_str = f"{hours_difference:+.1f}h"
            else:
                # For fractional hours like Nepal's UTC+5:45
                time_diff_str = f"{hours_difference:+.2f}".rstrip(
                    "0").rstrip(".") + "h"

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
            return f"Error processing time conversion: {str(e)}"

# Tool function definitions that will be registered with MCP


async def get_current_time(timezone: str, ctx: Context = None) -> str:
    """Get current time in specified timezone"""
    try:
        return await _get_time_tools().get_current_time(timezone)
    except Exception as e:
        return f"Error processing time query: {str(e)}"


async def convert_time(source_timezone: str, time: str, target_timezone: str, ctx: Context = None) -> str:
    """Convert time between timezones"""
    try:
        return await _get_time_tools().convert_time(source_timezone, time, target_timezone)
    except Exception as e:
        return f"Error processing time conversion: {str(e)}"

# Tool registration and initialization
_time_tools_instance = None


def initialize_time_tools():
    """Initialize the time tools"""
    global _time_tools_instance
    _time_tools_instance = TimeToolsService()
    return _time_tools_instance


def _get_time_tools():
    """Get or initialize the time tools"""
    global _time_tools_instance
    if _time_tools_instance is None:
        _time_tools_instance = initialize_time_tools()
    return _time_tools_instance


def get_time_tools():
    """Get a dictionary of all time tools for registration with MCP"""
    return {
        TimeTools.GET_CURRENT_TIME: get_current_time,
        TimeTools.CONVERT_TIME: convert_time
    }
