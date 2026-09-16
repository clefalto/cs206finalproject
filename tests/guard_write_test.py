"""
Comprehensive Hypothesis-based tests for guard_write function.

This test file exercises all semantic properties identified in 
properties/guard_write_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats, composite
from typing import List, Tuple


def guard_write(timestamps, now, *, window=5, limit=3):
    """
    Rate limiter for write events.
    """
    window_start = now - window
    recent = [t for t in timestamps if t >= window_start]

    # BUG: allows exactly-at-limit traffic.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)


class TestGuardWriteProperties:
    """Test class for all semantic properties of guard_write."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_rejection_on_exceed_limit(self, timestamps, now, window, limit):
        """
        Property: rejection_on_exceed_limit
        When len(recent) > limit, guard_write returns (False, 0).
        """
        result = guard_write(timestamps, now, window=window, limit=limit)
        
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        if len(recent) > limit:
            assert result == (False, 0)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_acceptance_with_remaining_capacity(self, timestamps, now, window, limit):
        """
        Property: acceptance_with_remaining_capacity
        When len(recent) <= limit, guard_write returns (True, limit - len(recent)).
        """
        result = guard_write(timestamps, now, window=window, limit=limit)
        
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        if len(recent) <= limit:
            expected_remaining = limit - len(recent)
            assert result == (True, expected_remaining)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_rate_limiting(self, timestamps, now, window, limit):
        """
        Property: rate_limiting
        When len([t for t in timestamps if t >= now - window]) <= limit,
        guard_write returns True for the first element.
        """
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count <= limit)
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        assert result[0] == True

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_remaining_capacity_calculation(self, timestamps, now, window, limit):
        """
        Property: remaining_capacity_calculation
        When len([t for t in timestamps if t >= now - window]) <= limit,
        guard_write returns (limit - len(recent)) for the second element.
        """
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count <= limit)
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        expected_remaining = limit - recent_count
        assert result[1] == expected_remaining

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_window_filtering(self, timestamps, now, window, limit):
        """
        Property: window_filtering
        guard_write depends only on timestamps >= now - window.
        """
        result = guard_write(timestamps, now, window=window, limit=limit)
        
        window_start = now - window
        recent_timestamps = [t for t in timestamps if t >= window_start]
        
        # Create a modified timestamps list with only recent timestamps
        # and timestamps that are definitely outside the window
        filtered_timestamps = recent_timestamps + [window_start - 1000] * 10
        
        result_filtered = guard_write(filtered_timestamps, now, window=window, limit=limit)
        
        assert result == result_filtered

    @given(
        timestamps1=lists(floats(min_value=0, max_value=1e9), max_size=500),
        timestamps2=lists(floats(min_value=0, max_value=1e9), max_size=500),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_monotonic_restriction(self, timestamps1, timestamps2, now, window, limit):
        """
        Property: monotonic_restriction
        If len([t for t in timestamps1 if t >= now - window]) <= len([t for t in timestamps2 if t >= now - window]),
        then guard_write(timestamps1, now, window, limit)[0] >= guard_write(timestamps2, now, window, limit)[0].
        """
        window_start = now - window
        recent_count1 = len([t for t in timestamps1 if t >= window_start])
        recent_count2 = len([t for t in timestamps2 if t >= window_start])
        
        assume(recent_count1 <= recent_count2)
        
        result1 = guard_write(timestamps1, now, window=window, limit=limit)
        result2 = guard_write(timestamps2, now, window=window, limit=limit)
        
        # If timestamps1 has fewer or equal recent timestamps, it should have equal or higher acceptance
        assert result1[0] >= result2[0]

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_bounded_remaining_capacity(self, timestamps, now, window, limit):
        """
        Property: bounded_remaining_capacity
        When guard_write returns True, the remaining capacity is between 0 and limit.
        """
        result = guard_write(timestamps, now, window=window, limit=limit)
        
        if result[0] == True:  # If accepted
            remaining_capacity = result[1]
            assert 0 <= remaining_capacity <= limit

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_exact_capacity_when_empty(self, timestamps, now, window, limit):
        """
        Property: exact_capacity_when_empty
        When len([t for t in timestamps if t >= now - window]) == 0,
        guard_write returns (True, limit).
        """
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count == 0)
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_zero_capacity_on_exceed(self, timestamps, now, window, limit):
        """
        Property: zero_capacity_on_exceed
        When len([t for t in timestamps if t >= now - window]) > limit,
        guard_write returns (False, 0).
        """
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count > limit)
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        assert result == (False, 0)


class TestGuardWriteEdgeCases:
    """Additional edge case tests for guard_write."""

    @given(
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_empty_timestamps(self, now, window, limit):
        """Test with empty timestamps list."""
        result = guard_write([], now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=100, max_value=1e9),
        window=integers(min_value=1, max_value=50),
        limit=integers(min_value=1, max_value=50)
    )
    def test_boundary_conditions(self, timestamps, now, window, limit):
        """Test boundary conditions around the window cutoff."""
        window_start = now - window
        
        # Test with timestamps exactly at boundary
        boundary_timestamps = [window_start - 1, window_start, window_start + 1]
        
        result = guard_write(boundary_timestamps, now, window=window, limit=limit)
        
        # Only timestamps >= window_start should be counted as recent
        recent_count = sum(1 for t in boundary_timestamps if t >= window_start)
        
        if recent_count > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - recent_count)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_all_timestamps_in_window(self, timestamps, now, window, limit):
        """Test when all timestamps are within the window."""
        # Ensure all timestamps are recent
        window_start = now - window
        recent_timestamps = [t for t in timestamps if t >= window_start]
        assume(len(recent_timestamps) == len(timestamps))
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        
        if len(timestamps) > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - len(timestamps))

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_no_timestamps_in_window(self, timestamps, now, window, limit):
        """Test when no timestamps are within the window."""
        # Ensure no timestamps are recent
        window_start = now - window
        recent_timestamps = [t for t in timestamps if t >= window_start]
        assume(len(recent_timestamps) == 0)
        
        result = guard_write(timestamps, now, window=window, limit=limit)
        assert result == (True, limit)


class TestGuardWriteParameterEffects:
    """Test how different parameters affect the guard_write function."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window1=integers(min_value=1, max_value=50),
        window2=integers(min_value=1, max_value=50),
        limit=integers(min_value=0, max_value=50)
    )
    def test_window_parameter_effect(self, timestamps, now, window1, window2, limit):
        """Test that larger window gives equal or higher quota."""
        assume(window1 <= window2)
        
        result1 = guard_write(timestamps, now, window=window1, limit=limit)
        result2 = guard_write(timestamps, now, window=window2, limit=limit)
        
        # Larger window should give equal or higher quota
        assert result1[1] <= result2[1]

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=100),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=50),
        limit1=integers(min_value=0, max_value=50),
        limit2=integers(min_value=0, max_value=50)
    )
    def test_limit_parameter_effect(self, timestamps, now, window, limit1, limit2):
        """Test that larger limit gives equal or higher quota."""
        assume(limit1 <= limit2)
        
        result1 = guard_write(timestamps, now, window=window, limit=limit1)
        result2 = guard_write(timestamps, now, window=window, limit=limit2)
        
        # Larger limit should give equal or higher quota
        assert result1[1] <= result2[1]

    @given(
        timestamps1=lists(floats(min_value=0, max_value=1e9), max_size=50),
        timestamps2=lists(floats(min_value=0, max_value=1e9), max_size=50),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=50),
        limit=integers(min_value=0, max_value=50)
    )
    def test_monotonic_quota_decrease(self, timestamps1, timestamps2, now, window, limit):
        """Test that more timestamps give equal or lower quota."""
        assume(len(timestamps1) <= len(timestamps2))
        
        result1 = guard_write(timestamps1, now, window=window, limit=limit)
        result2 = guard_write(timestamps2, now, window=window, limit=limit)
        
        # More timestamps should give equal or lower quota
        assert result1[1] >= result2[1]


if __name__ == "__main__":
    # This allows running the tests with python -m pytest
    pytest.main([__file__, "-v"])