# Time Tool

## Overview
The Time Tool provides utilities for working with time across different timezones. It allows you to get the current time in any timezone and convert times between different timezones, making it easy to work with global time data.

## Features
- Get current time in any timezone
- Convert times between different timezones
- Detailed timezone information including UTC offset
- Support for all standard IANA timezone names

## Usage Examples

### Getting Current Time

```python
# Get current time in New York
result = await get_current_time(timezone="America/New_York")
print(result)

# Get current time in Tokyo
result = await get_current_time(timezone="Asia/Tokyo")
print(result)

# Get current time in London
result = await get_current_time(timezone="Europe/London")
print(result)
```

Example response:
```json
{
  "timezone": "America/New_York",
  "datetime": "2023-10-15T14:30:45",
  "date": "2023-10-15",
  "time": "14:30:45",
  "utc_offset": "-04:00",
  "is_dst": true,
  "day_of_week": "Sunday",
  "day_of_year": 288,
  "week_of_year": 41,
  "timestamp": 1697392245
}
```

### Converting Time Between Timezones

```python
# Convert 9:00 AM New York time to London time
result = await convert_time(
    source_timezone="America/New_York",
    time="09:00",
    target_timezone="Europe/London"
)
print(result)

# Convert 15:30 Tokyo time to Los Angeles time
result = await convert_time(
    source_timezone="Asia/Tokyo",
    time="15:30",
    target_timezone="America/Los_Angeles"
)
print(result)

# Convert time with seconds precision
result = await convert_time(
    source_timezone="Europe/Berlin",
    time="18:45:30",
    target_timezone="Asia/Dubai"
)
print(result)
```

Example response:
```json
{
  "source": {
    "timezone": "America/New_York",
    "time": "09:00:00",
    "utc_offset": "-04:00",
    "is_dst": true
  },
  "target": {
    "timezone": "Europe/London",
    "time": "14:00:00",
    "utc_offset": "+01:00",
    "is_dst": true
  },
  "difference": {
    "hours": 5,
    "minutes": 0,
    "total_minutes": 300
  }
}
```

## API Reference

### get_current_time
Get current time in specified timezone.

**Parameters:**
- `timezone`: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')

**Returns:**
- Dictionary with current time information including:
  - `timezone`: The timezone name
  - `datetime`: ISO format datetime string
  - `date`: Date in YYYY-MM-DD format
  - `time`: Time in HH:MM:SS format
  - `utc_offset`: Offset from UTC
  - `is_dst`: Whether Daylight Saving Time is in effect
  - `day_of_week`: Name of the day of week
  - `day_of_year`: Day of year (1-366)
  - `week_of_year`: Week of year (1-53)
  - `timestamp`: Unix timestamp

### convert_time
Convert time between timezones.

**Parameters:**
- `source_timezone`: Source timezone name (e.g., 'America/New_York')
- `time`: Time to convert in HH:MM or HH:MM:SS format [24-hour]
- `target_timezone`: Target timezone name (e.g., 'Europe/London')

**Returns:**
- Dictionary with time conversion result including:
  - `source`: Source timezone and time information
  - `target`: Target timezone and time information
  - `difference`: Time difference information

## Common Timezone Names

Here are some commonly used timezone names:

### North America
- America/New_York (Eastern Time)
- America/Chicago (Central Time)
- America/Denver (Mountain Time)
- America/Los_Angeles (Pacific Time)
- America/Anchorage (Alaska Time)
- America/Honolulu (Hawaii Time)
- America/Toronto (Eastern Time - Canada)
- America/Vancouver (Pacific Time - Canada)
- America/Mexico_City (Central Time - Mexico)

### Europe
- Europe/London (British Time)
- Europe/Paris (Central European Time)
- Europe/Berlin (Central European Time)
- Europe/Madrid (Central European Time)
- Europe/Rome (Central European Time)
- Europe/Moscow (Moscow Time)
- Europe/Athens (Eastern European Time)

### Asia
- Asia/Tokyo (Japan Time)
- Asia/Shanghai (China Time)
- Asia/Hong_Kong (Hong Kong Time)
- Asia/Singapore (Singapore Time)
- Asia/Dubai (Gulf Time)
- Asia/Kolkata (India Time)
- Asia/Jakarta (Western Indonesian Time)

### Oceania
- Australia/Sydney (Eastern Australia Time)
- Australia/Perth (Western Australia Time)
- Pacific/Auckland (New Zealand Time)

### Africa
- Africa/Johannesburg (South Africa Time)
- Africa/Cairo (Egypt Time)
- Africa/Lagos (West Africa Time)

### South America
- America/Sao_Paulo (Brasilia Time)
- America/Buenos_Aires (Argentina Time)
- America/Santiago (Chile Time)

## Error Handling
The tool provides detailed error messages for common issues:

- Invalid timezone name
- Invalid time format
- Internal time processing errors

Example error handling:
```python
result = await convert_time(
    source_timezone="Invalid/Timezone",
    time="09:00",
    target_timezone="Europe/London"
)

if "error" in result:
    print(f"An error occurred: {result['error']}")
else:
    print(f"Time in {result['target']['timezone']}: {result['target']['time']}")
```

## Limitations
- All times are handled in 24-hour format
- Historical timezone changes may not be fully represented
- Complex timezone rules during DST transitions might cause edge cases
