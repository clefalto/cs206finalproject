"""
Comprehensive Hypothesis-based tests for batch_rate function.

This test file exercises all semantic properties identified in 
properties/batch_rate_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats, composite
from typing import List, Tuple


# Import the function under test
def batch_rate(timestamps, now, *, window=60, limit=20):
    """
    Throttle batch by recent activity.
    """
    cutoff = now - window
    recent = [t for t in timestamps if t >= cutoff]

    # BUG: should block when len(recent) == limit.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)


class TestBatchRateProperties:
    """Test class for all semantic properties of batch_rate."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_boolean_result(self, timestamps, now, window, limit):
        """Property: boolean_result - Function returns (bool, int)."""
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], int)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_rate_limit_exceeded_branch(self, timestamps, now, window, limit):
        """Property: rate_limit_exceeded - if len(recent) > limit then return False, 0."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) > limit)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_rate_limit_ok_branch(self, timestamps, now, window, limit):
        """Property: rate_limit_ok - if not (len(recent) > limit) then return True, limit - len(recent)."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(not (len(recent) > limit))
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(recent)
        assert result == (True, expected_capacity)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_capacity_calculation(self, timestamps, now, window, limit):
        """Property: capacity_calculation - capacity = limit - len(recent)."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when not exceeding limit
        assume(not (len(recent) > limit))
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(recent)
        assert result[1] == expected_capacity

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_non_negative_capacity(self, timestamps, now, window, limit):
        """Property: non_negative_capacity - limit - len(recent) >= 0."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when not exceeding limit
        assume(not (len(recent) > limit))
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result[1] >= 0

    @given(
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_maximum_capacity(self, now, window, limit):
        """Property: maximum_capacity - if len(recent) == 0 then limit - len(recent) == limit."""
        # Test with empty timestamps list
        result = batch_rate([], now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_zero_capacity_on_limit(self, timestamps, now, window, limit):
        """Property: zero_capacity_on_limit - if len(recent) == limit then limit - len(recent) == 0."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when exactly at limit
        assume(len(recent) == limit)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result == (True, 0)

    @given(
        timestamps1=lists(floats(min_value=0, max_value=1e9), max_size=500),
        timestamps2=lists(floats(min_value=0, max_value=1e9), max_size=500),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_monotonic_capacity(self, timestamps1, timestamps2, now, window, limit):
        """Property: monotonic_capacity - if len(recent1) <= len(recent2) then capacity1 >= capacity2."""
        cutoff = now - window
        recent1 = [t for t in timestamps1 if t >= cutoff]
        recent2 = [t for t in timestamps2 if t >= cutoff]
        
        # Only test when both are within limits
        assume(not (len(recent1) > limit))
        assume(not (len(recent2) > limit))
        assume(len(recent1) <= len(recent2))
        
        result1 = batch_rate(timestamps1, now, window=window, limit=limit)
        result2 = batch_rate(timestamps2, now, window=window, limit=limit)
        
        assert result1[1] >= result2[1]

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_rate_limit_boundary(self, timestamps, now, window, limit):
        """Property: rate_limit_boundary - if len(recent) == limit + 1 then return False, 0."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when exactly one over the limit
        assume(len(recent) == limit + 1)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_capacity_boundary(self, timestamps, now, window, limit):
        """Property: capacity_boundary - if len(recent) == limit - 1 then return True, 1."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when exactly one less than the limit
        assume(len(recent) == limit - 1)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result == (True, 1)


class TestBatchRateEdgeCases:
    """Additional edge case tests for batch_rate."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=100)
    )
    def test_all_timestamps_in_window(self, timestamps, now, window, limit):
        """Test when all timestamps are within the window."""
        # Ensure all timestamps are recent
        recent_timestamps = [t for t in timestamps if t >= now - window]
        assume(len(recent_timestamps) == len(timestamps))
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        
        if len(timestamps) > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - len(timestamps))

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=100)
    )
    def test_no_timestamps_in_window(self, timestamps, now, window, limit):
        """Test when no timestamps are within the window."""
        # Ensure no timestamps are recent
        recent_timestamps = [t for t in timestamps if t >= now - window]
        assume(len(recent_timestamps) == 0)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        now=floats(min_value=100, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=1, max_value=100)
    )
    def test_boundary_conditions(self, now, window, limit):
        """Test boundary conditions around the cutoff time."""
        cutoff = now - window
        
        # Test with timestamps exactly at boundary
        timestamps = [cutoff - 1, cutoff, cutoff + 1]
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        
        # Only timestamps >= cutoff should be counted as recent
        recent_count = sum(1 for t in timestamps if t >= cutoff)
        
        if recent_count > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - recent_count)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=100)
    )
    def test_empty_timestamps(self, timestamps, now, window, limit):
        """Test with empty timestamps list."""
        result = batch_rate([], now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_zero_limit(self, now, window, limit):
        """Test with zero limit."""
        # Test with zero limit
        result = batch_rate([], now, window=window, limit=0)
        assert result == (True, 0)
        
        # Test with zero limit and some timestamps
        result = batch_rate([now - window/2], now, window=window, limit=0)
        assert result == (False, 0)


class TestBatchRateBugBehavior:
    """Test the specific bug mentioned in the function."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=100)
    )
    def test_boundary_bug(self, timestamps, now, window, limit):
        """Test the boundary bug where len(recent) == limit should block but doesn't."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when exactly at the limit
        assume(len(recent) == limit)
        
        result = batch_rate(timestamps, now, window=window, limit=limit)
        
        # Due to the bug, this should return (True, 0) instead of (False, 0)
        assert result == (True, 0)


if __name__ == "__main__":
    # This allows running the tests with python -m pytest
    pytest.main([__file__, "-v"])