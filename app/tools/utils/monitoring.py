#!/usr/bin/env python3
"""
Monitoring and telemetry utilities for MCP tools.

This module provides utilities for performance tracking, usage statistics,
error tracking, and reporting for MCP tools.
"""
import time
import logging
import functools
import threading
import json
import os
import platform
import uuid
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import traceback

logger = logging.getLogger(__name__)

# Global in-memory storage for metrics
_execution_metrics = []
_execution_metrics_lock = threading.Lock()

# Maximum number of metrics to store in memory
_MAX_METRICS = 1000

# Constants
_METRICS_FILE = os.environ.get("MCP_METRICS_FILE", "metrics.jsonl")
_ENABLE_TELEMETRY = os.environ.get("MCP_ENABLE_TELEMETRY", "false").lower() == "true"
_TELEMETRY_ENDPOINT = os.environ.get("MCP_TELEMETRY_ENDPOINT", None)
_TELEMETRY_API_KEY = os.environ.get("MCP_TELEMETRY_API_KEY", None)
_SYSTEM_ID = os.environ.get("MCP_SYSTEM_ID", str(uuid.uuid4()))

def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor tool performance.
    
    Args:
        func: The function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        status = "success"
        error_details = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            error_details = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            log_execution(
                tool_name=func.__name__,
                execution_time=execution_time,
                status=status,
                error_details=error_details
            )
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        status = "success"
        error_details = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            error_details = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            log_execution(
                tool_name=func.__name__,
                execution_time=execution_time,
                status=status,
                error_details=error_details
            )
    
    # Choose the appropriate wrapper based on the function type
    if asyncio_is_coroutine_function(func):
        return async_wrapper
    else:
        return sync_wrapper

def asyncio_is_coroutine_function(func):
    """Check if a function is a coroutine function (for asyncio compatibility)"""
    import inspect
    return inspect.iscoroutinefunction(func)

def log_execution(tool_name: str, execution_time: float, status: str, 
                error_details: Optional[str] = None) -> None:
    """
    Log tool execution details.
    
    Args:
        tool_name: Name of the tool
        execution_time: Time taken for execution in seconds
        status: Execution status ("success" or "error")
        error_details: Optional error details if status is "error"
    """
    timestamp = datetime.now().isoformat()
    
    # Create the metric record
    metric = {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "execution_time": execution_time,
        "status": status,
        "system_id": _SYSTEM_ID,
        "hostname": socket.gethostname(),
        "platform": platform.platform()
    }
    
    if error_details:
        metric["error_details"] = error_details
    
    # Log to console
    if status == "success":
        logger.info(f"Tool {tool_name} executed in {execution_time:.4f}s")
    else:
        logger.error(f"Tool {tool_name} failed in {execution_time:.4f}s: {error_details}")
    
    # Store in memory
    with _execution_metrics_lock:
        _execution_metrics.append(metric)
        
        # Trim if exceeding max size
        if len(_execution_metrics) > _MAX_METRICS:
            _execution_metrics.pop(0)
    
    # Write to file if configured
    if _METRICS_FILE:
        try:
            with open(_METRICS_FILE, "a") as f:
                f.write(json.dumps(metric) + "\n")
        except Exception as e:
            logger.error(f"Failed to write metrics to file: {e}")
    
    # Send telemetry if enabled
    if _ENABLE_TELEMETRY and _TELEMETRY_ENDPOINT and _TELEMETRY_API_KEY:
        try:
            send_telemetry(metric)
        except Exception as e:
            logger.error(f"Failed to send telemetry: {e}")

def send_telemetry(metric: Dict[str, Any]) -> None:
    """
    Send telemetry data to configured endpoint.
    
    Args:
        metric: Metric data to send
    """
    if not _ENABLE_TELEMETRY or not _TELEMETRY_ENDPOINT or not _TELEMETRY_API_KEY:
        return
    
    try:
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_TELEMETRY_API_KEY}"
        }
        
        response = requests.post(
            _TELEMETRY_ENDPOINT,
            headers=headers,
            json=metric,
            timeout=2  # Short timeout to not block execution
        )
        
        if response.status_code >= 400:
            logger.warning(f"Telemetry API returned error: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Failed to send telemetry: {e}")

def get_execution_metrics(
    tool_name: Optional[str] = None, 
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get execution metrics, optionally filtered.
    
    Args:
        tool_name: Optional filter by tool name
        status: Optional filter by status
        limit: Maximum number of records to return
        
    Returns:
        List of metric records
    """
    with _execution_metrics_lock:
        filtered_metrics = _execution_metrics.copy()
    
    # Apply filters
    if tool_name:
        filtered_metrics = [m for m in filtered_metrics if m["tool_name"] == tool_name]
    
    if status:
        filtered_metrics = [m for m in filtered_metrics if m["status"] == status]
    
    # Sort by timestamp (most recent first) and apply limit
    filtered_metrics.sort(key=lambda m: m["timestamp"], reverse=True)
    return filtered_metrics[:limit]

def get_execution_statistics(tool_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get execution statistics for tools.
    
    Args:
        tool_name: Optional filter by tool name
        
    Returns:
        Dictionary with execution statistics
    """
    with _execution_metrics_lock:
        metrics = _execution_metrics.copy()
    
    # Apply tool filter if specified
    if tool_name:
        metrics = [m for m in metrics if m["tool_name"] == tool_name]
    
    if not metrics:
        return {
            "total_executions": 0,
            "success_rate": 0,
            "avg_execution_time": 0,
            "min_execution_time": 0,
            "max_execution_time": 0
        }
    
    # Calculate statistics
    total = len(metrics)
    successful = len([m for m in metrics if m["status"] == "success"])
    execution_times = [m["execution_time"] for m in metrics]
    
    return {
        "total_executions": total,
        "success_rate": successful / total if total > 0 else 0,
        "avg_execution_time": sum(execution_times) / total if total > 0 else 0,
        "min_execution_time": min(execution_times) if execution_times else 0,
        "max_execution_time": max(execution_times) if execution_times else 0,
        "error_count": total - successful,
        "tools_count": len(set(m["tool_name"] for m in metrics))
    }

def clear_metrics() -> None:
    """Clear all stored metrics from memory."""
    with _execution_metrics_lock:
        _execution_metrics.clear()

def format_execution_error(e: Exception, include_traceback: bool = True) -> Dict[str, Any]:
    """
    Format an exception for consistent error reporting.
    
    Args:
        e: The exception to format
        include_traceback: Whether to include the traceback
        
    Returns:
        Dictionary with formatted error details
    """
    error_info = {
        "error_type": type(e).__name__,
        "error_message": str(e),
        "timestamp": datetime.now().isoformat()
    }
    
    if include_traceback:
        error_info["traceback"] = traceback.format_exc()
    
    return error_info


class PerformanceTracker:
    """
    Context manager for tracking performance of code blocks.
    
    Example:
        with PerformanceTracker("operation_name") as tracker:
            # Do some operation
            result = perform_operation()
            tracker.add_metadata("result_size", len(result))
    """
    
    def __init__(self, operation_name: str):
        """
        Initialize the performance tracker.
        
        Args:
            operation_name: Name of the operation being tracked
        """
        self.operation_name = operation_name
        self.start_time = None
        self.metadata = {}
    
    def __enter__(self):
        """Start tracking time when entering the context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log performance when exiting the context."""
        execution_time = time.time() - self.start_time
        
        status = "success"
        error_details = None
        
        if exc_type is not None:
            status = "error"
            error_details = str(exc_val)
        
        # Create metric with additional metadata
        metric = {
            "timestamp": datetime.now().isoformat(),
            "operation_name": self.operation_name,
            "execution_time": execution_time,
            "status": status,
            "system_id": _SYSTEM_ID,
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "metadata": self.metadata
        }
        
        if error_details:
            metric["error_details"] = error_details
        
        # Log to console
        if status == "success":
            logger.info(f"Operation {self.operation_name} completed in {execution_time:.4f}s")
        else:
            logger.error(f"Operation {self.operation_name} failed in {execution_time:.4f}s: {error_details}")
        
        # Store in memory
        with _execution_metrics_lock:
            _execution_metrics.append(metric)
            
            # Trim if exceeding max size
            if len(_execution_metrics) > _MAX_METRICS:
                _execution_metrics.pop(0)
        
        # Don't suppress exceptions
        return False
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the performance tracking.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
