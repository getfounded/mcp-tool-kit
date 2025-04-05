#!/usr/bin/env python3
"""
Unit tests for base service functionality.
"""
import pytest
import os
import time
from unittest.mock import patch, MagicMock

from app.tools.base.service import ToolServiceBase, RateLimiter


def test_rate_limiter_check_limit():
    """Test rate limiter check_limit functionality"""
    # Create rate limiter with 3 calls per second
    limiter = RateLimiter(calls=3, period=1.0)

    # First 3 calls should be allowed
    assert limiter.check_limit() == True
    assert limiter.check_limit() == True
    assert limiter.check_limit() == True

    # 4th call should be rejected
    assert limiter.check_limit() == False

    # Wait for rate limit period to expire
    time.sleep(1.1)

    # Now should allow calls again
    assert limiter.check_limit() == True


def test_rate_limiter_wait_if_needed():
    """Test rate limiter wait_if_needed functionality"""
    # Create rate limiter with 2 calls per second
    limiter = RateLimiter(calls=2, period=1.0)

    # First 2 calls should return 0 wait time
    assert limiter.wait_if_needed() == 0.0
    assert limiter.wait_if_needed() == 0.0

    # 3rd call should require waiting
    start = time.time()
    wait_time = limiter.wait_if_needed()
    elapsed = time.time() - start

    # Wait time should be positive
    assert wait_time > 0.0
    # Actual elapsed time should be close to wait time
    assert abs(elapsed - wait_time) < 0.1


class TestToolServiceBase:

    def test_initialization(self):
        """Test basic initialization of service base class"""
        service = ToolServiceBase()
        assert service.initialized == False

        # Initialize service
        result = service.initialize()
        assert result == True
        assert service.initialized == True

    def test_is_initialized_check(self):
        """Test initialized check"""
        service = ToolServiceBase()

        # Should raise error if not initialized
        with pytest.raises(ValueError, match="is not properly initialized"):
            service._is_initialized()

        # Initialize and check again
        service.initialize()
        assert service._is_initialized() == True

    def test_get_env_var(self, monkeypatch):
        """Test environment variable retrieval"""
        service = ToolServiceBase()

        # Set a test environment variable
        monkeypatch.setenv("TEST_ENV_VAR", "test_value")

        # Retrieve the variable
        value = service.get_env_var("TEST_ENV_VAR")
        assert value == "test_value"

        # Test with default value
        value = service.get_env_var("NONEXISTENT_VAR", default="default_value")
        assert value == "default_value"

        # Test with required flag
        with pytest.raises(ValueError, match="Required environment variable"):
            service.get_env_var("NONEXISTENT_VAR", required=True)

    def test_get_env_var_caching(self, monkeypatch):
        """Test environment variable caching"""
        service = ToolServiceBase()

        # Set initial value
        monkeypatch.setenv("CACHED_VAR", "initial_value")

        # Retrieve and cache the variable
        value1 = service.get_env_var("CACHED_VAR", cache=True)
        assert value1 == "initial_value"

        # Change the environment variable
        monkeypatch.setenv("CACHED_VAR", "new_value")

        # Should still return cached value
        value2 = service.get_env_var("CACHED_VAR", cache=True)
        assert value2 == "initial_value"

        # With cache=False, should get new value
        value3 = service.get_env_var("CACHED_VAR", cache=False)
        assert value3 == "new_value"

    def test_create_and_get_rate_limiter(self):
        """Test creating and retrieving rate limiters"""
        service = ToolServiceBase()

        # Create a rate limiter
        limiter = service.create_rate_limiter("test_limiter", 10, 60)
        assert isinstance(limiter, RateLimiter)

        # Retrieve the rate limiter
        retrieved_limiter = service.get_rate_limiter("test_limiter")
        assert retrieved_limiter is limiter

        # Non-existent limiter should return None
        assert service.get_rate_limiter("nonexistent") is None

    def test_apply_rate_limit(self):
        """Test applying rate limiting to operations"""
        service = ToolServiceBase()

        # Apply rate limit with wait=True
        wait_time = service.apply_rate_limit("test_limit", 5, 1, wait=True)
        assert wait_time == 0.0  # First call should not wait

        # Create multiple calls to exceed limit
        for _ in range(5):
            service.apply_rate_limit("test_limit", 5, 1, wait=True)

        # Next call should wait
        start = time.time()
        wait_time = service.apply_rate_limit("test_limit", 5, 1, wait=True)
        elapsed = time.time() - start
        assert wait_time > 0.0
        assert abs(elapsed - wait_time) < 0.1

        # Test with wait=False (should raise error when limit exceeded)
        service = ToolServiceBase()  # Fresh service

        # First calls should succeed
        for _ in range(5):
            service.apply_rate_limit("test_limit2", 5, 1, wait=False)

        # Next call should raise error
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            service.apply_rate_limit("test_limit2", 5, 1, wait=False)

    def test_validate_input(self):
        """Test input validation functionality"""
        service = ToolServiceBase()

        # Define some validator functions that return (is_valid, message)
        def validate_not_empty(value):
            return (value != "", "Value cannot be empty")

        def validate_length(value):
            return (len(value) >= 3, "Value must be at least 3 characters")

        # Valid input should pass all validators
        service.validate_input("test", [validate_not_empty, validate_length])

        # Empty string should fail first validator
        with pytest.raises(ValueError, match="Value cannot be empty"):
            service.validate_input("", [validate_not_empty, validate_length])

        # Short string should fail second validator
        with pytest.raises(ValueError, match="Value must be at least 3 characters"):
            service.validate_input("ab", [validate_not_empty, validate_length])
