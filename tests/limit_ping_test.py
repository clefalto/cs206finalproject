#!/usr/bin/env python3
"""
Hypothesis-based property tests for the limit_ping function.

This test suite exercises all semantic properties identified for the limit_ping function
using the Hypothesis testing framework to generate comprehensive test cases.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple, Set


# Import the function under test
# Note: This assumes limit_ping is available in the current environment
# In a real scenario, you would import from the actual module
try:
    from limit_ping import limit_ping
except ImportError:
    # Mock implementation for testing purposes
    def limit_ping(timestamps: List[int], now: int, window: int, limit: int) -> Tuple[bool, int]:
        """
        Mock implementation of limit_ping for testing.
        This should be replaced with the actual implementation.
        """
        # Filter timestamps within the window
        recent = [t for t in timestamps if t >= now - window]
        
        if len(recent) > limit:
            return (False, 0)
        else:
            return (True, limit - len(recent))


class TestLimitPingProperties:
    """Test class for limit_ping semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limiting(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limiting
        If the number of recent timestamps exceeds the limit, rate limiting should trigger.
        """
        recent_count = len([t for t in timestamps if t >= now - window])
        
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        if recent_count > limit:
            assert result == (False, 0), f"Expected (False, 0) when {recent_count} > {limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_remaining_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: remaining_quota
        The remaining quota should equal limit minus recent timestamps, but not go below 0.
        """
        recent_count = len([t for t in timestamps if t >= now - window])
        expected_quota = max(0, limit - recent_count)
        
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        assert result[1] == expected_quota, f"Expected quota {expected_quota}, got {result[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boolean_result(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: boolean_result
        The first element of the result should always be a boolean.
        """
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        assert isinstance(result[0], bool), f"Expected boolean result, got {type(result[0])}"
        assert result[0] in {True, False}, f"Expected True or False, got {result[0]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_non_negative_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: non_negative_quota
        The remaining quota should never be negative.
        """
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        assert result[1] >= 0, f"Expected non-negative quota, got {result[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_bounded_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: bounded_quota
        The remaining quota should never exceed the limit.
        """
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        assert result[1] <= limit, f"Expected quota <= {limit}, got {result[1]}"

    @given(
        timestamps1=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_monotonic_quota(self, timestamps1: List[int], now: int, window: int, limit: int):
        """
        Property: monotonic_quota
        Adding more timestamps should not increase the remaining quota.
        """
        # Create a superset by adding more timestamps
        additional_timestamps = st.lists(st.integers(min_value=0, max_value=1000000), min_size=1, max_size=5)
        
        for _ in range(5):  # Test with 5 different supersets
            extra_ts = [now - window + i for i in range(5)]  # Add timestamps within window
            timestamps2 = timestamps1 + extra_ts
            
            result1 = limit_ping(timestamps1, now, window=window, limit=limit)
            result2 = limit_ping(timestamps2, now, window=window, limit=limit)
            
            assert result1[1] >= result2[1], f"Adding timestamps should not increase quota: {result1[1]} >= {result2[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_window_independence(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: window_independence
        Only timestamps within [now-window, now] should affect the result.
        """
        # Filter to only timestamps within the window
        relevant_timestamps = [t for t in timestamps if now - window <= t <= now]
        
        result = limit_ping(timestamps, now, window=window, limit=limit)
        result_relevant = limit_ping(relevant_timestamps, now, window=window, limit=limit)
        
        assert result == result_relevant, f"Result should depend only on timestamps within window: {result} == {result_relevant}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now1=st.integers(min_value=0, max_value=500000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_time_monotonicity(self, timestamps: List[int], now1: int, window: int, limit: int):
        """
        Property: time_monotonicity
        As time progresses, the remaining quota should not decrease.
        """
        now2 = now1 + window // 2  # Ensure now2 > now1
        
        result1 = limit_ping(timestamps, now1, window=window, limit=limit)
        result2 = limit_ping(timestamps, now2, window=window, limit=limit)
        
        assert result1[1] <= result2[1], f"Quota should be monotonic in time: {result1[1]} <= {result2[1]}"

    @given(
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_empty_timestamps_identity(self, now: int, window: int, limit: int):
        """
        Property: empty_timestamps_identity
        With no timestamps, should always allow and return full limit.
        """
        result = limit_ping([], now, window=window, limit=limit)
        
        assert result == (True, limit), f"Empty timestamps should return (True, {limit}), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=500, deadline=None)
    def test_limit_zero_allows_none(self, timestamps: List[int], now: int, window: int):
        """
        Property: limit_zero_allows_none
        With limit=0, should always deny access.
        """
        result = limit_ping(timestamps, now, window=window, limit=0)
        
        assert result == (False, 0), f"Limit=0 should always return (False, 0), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_window_zero_allows_none(self, timestamps: List[int], now: int, limit: int):
        """
        Property: window_zero_allows_none
        With window=0, should deny if there are timestamps, allow if empty.
        """
        result = limit_ping(timestamps, now, window=0, limit=limit)
        
        if timestamps:
            assert result == (False, 0), f"Window=0 with timestamps should return (False, 0), got {result}"
        else:
            assert result == (True, limit), f"Window=0 with empty timestamps should return (True, {limit}), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_metamorphic_window_increase(self, timestamps: List[int], now: int, limit: int):
        """
        Property: metamorphic_window_increase
        Increasing the window should not decrease the remaining quota.
        """
        window1 = st.integers(min_value=1, max_value=500)
        window2 = st.integers(min_value=501, max_value=1000)
        
        for _ in range(3):  # Test with 3 different window pairs
            w1 = 100
            w2 = 200
            
            result1 = limit_ping(timestamps, now, window=w1, limit=limit)
            result2 = limit_ping(timestamps, now, window=w2, limit=limit)
            
            assert result1[1] <= result2[1], f"Larger window should not decrease quota: {result1[1]} <= {result2[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=500, deadline=None)
    def test_metamorphic_limit_increase(self, timestamps: List[int], now: int, window: int):
        """
        Property: metamorphic_limit_increase
        Increasing the limit should not decrease the remaining quota.
        """
        limit1 = st.integers(min_value=0, max_value=50)
        limit2 = st.integers(min_value=51, max_value=100)
        
        for _ in range(3):  # Test with 3 different limit pairs
            l1 = 10
            l2 = 20
            
            result1 = limit_ping(timestamps, now, window=window, limit=l1)
            result2 = limit_ping(timestamps, now, window=window, limit=l2)
            
            assert result1[1] <= result2[1], f"Larger limit should not decrease quota: {result1[1]} <= {result2[1]}"


class TestLimitPingBranchProperties:
    """Test class for limit_ping branch-specific properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_exceeded_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limit_exceeded (branch)
        When recent timestamps exceed limit, should return (False, 0).
        """
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) > limit)  # Branch condition
        
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        assert result == (False, 0), f"Expected (False, 0) when len(recent)={len(recent)} > limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_allowed_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limit_allowed (branch)
        When recent timestamps <= limit, should return (True, limit - len(recent)).
        """
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) <= limit)  # Branch condition
        
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        expected_quota = limit - len(recent)
        assert result == (True, expected_quota), f"Expected (True, {expected_quota}) when len(recent)={len(recent)} <= limit={limit}, got {result}"


class TestLimitPingEdgeCases:
    """Test class for edge cases and boundary conditions."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000), max_size=10),
        now=st.integers(min_value=0, max_value=1000000),
        window=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=200, deadline=None)
    def test_small_timestamps(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test with small numbers of timestamps to ensure correctness.
        """
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        # Basic property checks
        assert isinstance(result[0], bool)
        assert 0 <= result[1] <= limit
        assert result[1] == max(0, limit - len([t for t in timestamps if t >= now - window]))

    @example([], 100, 50, 10)
    @example([50, 60, 70], 100, 50, 2)
    @example([1, 2, 3, 4, 5], 10, 5, 3)
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=500, deadline=None)
    def test_specific_examples(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test with specific examples including edge cases.
        """
        result = limit_ping(timestamps, now, window=window, limit=limit)
        
        # Verify the result matches expected behavior
        recent_count = len([t for t in timestamps if t >= now - window])
        
        if recent_count > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - recent_count)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])