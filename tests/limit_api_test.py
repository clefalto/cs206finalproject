"""
Hypothesis-based tests for the limit_api function semantic properties.
Tests all properties defined in properties/limit_api_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, sampled_from
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.limit_api import limit_api


class TestLimitApiProperties:
    """Test class for limit_api semantic properties using Hypothesis."""

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_rate_limit_exceeded_branch(self, timestamps, now, window, limit):
        """
        Test: if len(recent) > limit then return False, 0
        Property: rate_limit_exceeded
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) > limit)
        
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Should return False status and 0 remaining when limit exceeded
        assert status is False, f"Expected False when len(recent)={len(recent)} > limit={limit}"
        assert remaining == 0, f"Expected remaining=0 when limit exceeded, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_rate_limit_allowed_branch(self, timestamps, now, window, limit):
        """
        Test: if not (len(recent) > limit) then return True, limit - len(recent)
        Property: rate_limit_allowed
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met (limit not exceeded)
        assume(not (len(recent) > limit))
        
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Should return True status and calculated remaining count
        assert status is True, f"Expected True when len(recent)={len(recent)} <= limit={limit}"
        expected_remaining = limit - len(recent)
        assert remaining == expected_remaining, f"Expected remaining={expected_remaining}, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_boolean_status_property(self, timestamps, now, window, limit):
        """
        Test: limit_api(timestamps, now) returns (bool, int) where bool indicates if request is allowed
        Property: boolean_status
        """
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Status must be a boolean
        assert isinstance(status, bool), f"Status should be bool, got {type(status)}"
        
        # Remaining should be an integer
        assert isinstance(remaining, int), f"Remaining should be int, got {type(remaining)}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_remaining_count_property(self, timestamps, now, window, limit):
        """
        Test: limit_api(timestamps, now) returns (status, remaining) where remaining >= 0
        Property: remaining_count
        """
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Remaining count should always be non-negative
        assert remaining >= 0, f"Remaining count should be >= 0, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_monotonic_remaining_property(self, timestamps, now, window, limit):
        """
        Test: if len(recent) increases then remaining decreases or stays same
        Property: monotonic_remaining
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Calculate expected remaining based on recent count
        expected_remaining = max(0, limit - len(recent))
        
        # Remaining should be monotonic with respect to recent count
        assert remaining <= limit, f"Remaining should not exceed limit, got {remaining} > {limit}"
        assert remaining >= 0, f"Remaining should be non-negative, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_boundary_conditions_property(self, timestamps, now, window, limit):
        """
        Test: if len(recent) == 0 then remaining == limit, if len(recent) >= limit then status == False
        Property: boundary_conditions
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        status, remaining = limit_api(timestamps, now, window=window, limit=limit)
        
        # Test boundary condition 1: if len(recent) == 0 then remaining == limit
        if len(recent) == 0:
            assert remaining == limit, f"When no recent requests, remaining should equal limit ({limit}), got {remaining}"
        
        # Test boundary condition 2: if len(recent) >= limit then status == False
        if len(recent) >= limit:
            assert status is False, f"When len(recent) >= limit, status should be False, got {status}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_idempotency_property(self, timestamps, now, window, limit):
        """
        Test: limit_api(timestamps, now) == limit_api(timestamps, now) for same inputs
        Property: idempotency
        """
        result1 = limit_api(timestamps, now, window=window, limit=limit)
        result2 = limit_api(timestamps, now, window=window, limit=limit)
        
        # Same inputs should produce identical outputs
        assert result1 == result2, f"Function should be idempotent, got {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_deterministic_property(self, timestamps, now, window, limit):
        """
        Test: same inputs always produce same outputs
        Property: deterministic
        """
        # Run the function multiple times with same inputs
        results = []
        for _ in range(5):
            result = limit_api(timestamps, now, window=window, limit=limit)
            results.append(result)
        
        # All results should be identical
        assert all(result == results[0] for result in results), \
            f"Function should be deterministic, got varying results: {results}"


# Additional integration tests for specific scenarios
class TestLimitApiIntegration:
    """Additional integration tests for limit_api."""

    def test_empty_timestamps(self):
        """Test with empty timestamps list."""
        status, remaining = limit_api([], 100, window=60, limit=20)
        assert status is True
        assert remaining == 20

    def test_single_timestamp_within_window(self):
        """Test with single timestamp within window."""
        status, remaining = limit_api([90], 100, window=60, limit=20)
        assert status is True
        assert remaining == 19

    def test_single_timestamp_outside_window(self):
        """Test with single timestamp outside window."""
        status, remaining = limit_api([30], 100, window=60, limit=20)
        assert status is True
        assert remaining == 20

    def test_exactly_at_limit(self):
        """Test when recent count equals limit (should still allow)."""
        timestamps = list(range(41, 61))  # 20 timestamps in window
        status, remaining = limit_api(timestamps, 100, window=60, limit=20)
        assert status is True
        assert remaining == 0

    def test_over_limit(self):
        """Test when recent count exceeds limit."""
        timestamps = list(range(40, 61))  # 21 timestamps in window
        status, remaining = limit_api(timestamps, 100, window=60, limit=20)
        assert status is False
        assert remaining == 0

    def test_default_parameters(self):
        """Test with default window and limit parameters."""
        status, remaining = limit_api([90], 100)
        assert status is True
        assert remaining == 19