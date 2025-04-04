#!/usr/bin/env python3
"""
Enhanced base service class for MCP tool services.
"""
import logging
import os
import time
import threading
from typing import Dict, Any, Optional, Union, Callable, List, Tuple
from abc import ABC, abstractmethod

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls: int, period: float):
        """
        Initialize the rate limiter.
        
        Args:
            calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.timestamps = []
        self.lock = threading.Lock()
    
    def check_limit(self) -> bool:
        """
        Check if the rate limit allows another call.
        
        Returns:
            True if allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            # Clean up old timestamps
            self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            # Check if we've hit the limit
            if len(self.timestamps) >= self.calls:
                return False
                
            # Add current timestamp
            self.timestamps.append(now)
            return True
    
    def wait_if_needed(self) -> float:
        """
        Wait if rate limited and return the wait time.
        
        Returns:
            Time spent waiting in seconds
        """
        with self.lock:
            now = time.time()
            # Clean up old timestamps
            self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            # If we haven't hit the limit, no wait needed
            if len(self.timestamps) < self.calls:
                self.timestamps.append(now)
                return 0.0
            
            # Calculate required wait time
            oldest = min(self.timestamps)
            wait_time = oldest + self.period - now
            
            if wait_time > 0:
                time.sleep(wait_time)
                
            # Update timestamps
            self.timestamps = self.timestamps[1:]  # Remove oldest
            self.timestamps.append(now + wait_time)  # Add new timestamp
            
            return wait_time

class ToolServiceBase(ABC):
    """Enhanced base class for all tool services"""
    
    def __init__(self):
        """Initialize the base service"""
        self.initialized = False
        self.logger = logging.getLogger(self.__class__.__name__)
        self._rate_limiters = {}
        self._cached_env_vars = {}
    
    def initialize(self) -> bool:
        """
        Initialize the service. Should be overridden by subclasses.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.initialized = True
        return True
    
    def _is_initialized(self) -> bool:
        """
        Check if the service is properly initialized.
        
        Returns:
            bool: True if initialized, raises ValueError otherwise
        """
        if not self.initialized:
            class_name = self.__class__.__name__
            raise ValueError(f"{class_name} is not properly initialized.")
        return True
    
    def get_env_var(self, var_name: str, required: bool = False, 
                   default: Optional[str] = None, cache: bool = True) -> Optional[str]:
        """
        Get environment variable with enhanced features.
        
        Args:
            var_name: Name of the environment variable
            required: Whether the variable is required
            default: Default value if not set
            cache: Whether to cache the result
            
        Returns:
            The value of the environment variable, default, or None
            
        Raises:
            ValueError: If the variable is required but not set
        """
        # Return cached value if available
        if cache and var_name in self._cached_env_vars:
            return self._cached_env_vars[var_name]
            
        # Get value from environment
        value = os.environ.get(var_name, default)
        
        # Validate if required
        if required and value is None:
            raise ValueError(f"Required environment variable {var_name} is not set")
        
        # Cache if requested
        if cache:
            self._cached_env_vars[var_name] = value
            
        return value
    
    def create_rate_limiter(self, name: str, calls: int, period: float) -> RateLimiter:
        """
        Create a named rate limiter.
        
        Args:
            name: Identifier for the rate limiter
            calls: Maximum number of calls in the period
            period: Time period in seconds
            
        Returns:
            The created rate limiter
        """
        limiter = RateLimiter(calls, period)
        self._rate_limiters[name] = limiter
        return limiter
    
    def get_rate_limiter(self, name: str) -> Optional[RateLimiter]:
        """
        Get a rate limiter by name.
        
        Args:
            name: Name of the rate limiter
            
        Returns:
            The rate limiter or None if not found
        """
        return self._rate_limiters.get(name)
    
    def apply_rate_limit(self, name: str, calls: int, period: float, wait: bool = True) -> float:
        """
        Apply rate limiting to the current operation.
        
        Args:
            name: Identifier for the rate limit
            calls: Maximum number of calls in the period
            period: Time period in seconds
            wait: Whether to wait if rate limited
            
        Returns:
            Time spent waiting if wait=True, 0 otherwise
            
        Raises:
            ValueError: If wait=False and rate limited
        """
        # Get or create rate limiter
        limiter = self._rate_limiters.get(name)
        if not limiter:
            limiter = self.create_rate_limiter(name, calls, period)
        
        # Apply rate limiting
        if wait:
            return limiter.wait_if_needed()
        elif not limiter.check_limit():
            raise ValueError(f"Rate limit exceeded for {name}")
        
        return 0.0
    
    def validate_input(self, value: Any, validators: List[Callable[[Any], Tuple[bool, str]]]) -> None:
        """
        Validate input using a list of validator functions.
        
        Args:
            value: The value to validate
            validators: List of validator functions, each returning (is_valid, error_message)
            
        Raises:
            ValueError: If validation fails
        """
        for validator in validators:
            is_valid, message = validator(value)
            if not is_valid:
                raise ValueError(message)
