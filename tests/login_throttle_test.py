"""
Hypothesis tests for the login_throttle function semantic properties.
Tests all 12 semantic properties identified in properties/login_throttle_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from dataset.python_programs.login_throttle import login_throttle


class TestLoginThrottleProperties:
    """Test class for login_throttle semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_block_on_excess_attempts_branch_property(self, timestamps, now, window, limit):
        """
        Branch property: if len(recent) > limit then (False, 0)
        """
        # Filter timestamps to get recent ones
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) > limit)
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        assert result == (False, 0), f"Result {result} should be (False, 0) when len(recent) > limit"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_allow_on_within_limit_branch_property(self, timestamps, now, window, limit):
        """
        Branch property: if not (len(recent) > limit) then (True, limit - len(recent))
        """
        # Filter timestamps to get recent ones
        recent = [t for t in timestamps if t >= now - window]
        
        assume(not (len(recent) > limit))
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        expected_allowance = limit - len(recent)
        assert result == (True, expected_allowance), f"Result {result} should be (True, {expected_allowance}) when within limit"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_monotonic_allowance_function_property(self, timestamps, now, window, limit):
        """
        Function property: allowance == limit - len(recent) when len(recent) <= limit
        """
        # Filter timestamps to get recent ones
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) <= limit)
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        expected_allowance = limit - len(recent)
        
        assert result[1] == expected_allowance, f"Allowance {result[1]} should equal limit - len(recent) = {expected_allowance}"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_block_on_limit_exceeded_function_property(self, timestamps, now, window, limit):
        """
        Function property: (False, 0) when len(recent) > limit
        """
        # Filter timestamps to get recent ones
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) > limit)
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        assert result == (False, 0), f"Result {result} should be (False, 0) when len(recent) > limit"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_non_negative_allowance_function_property(self, timestamps, now, window, limit):
        """
        Function property: allowance >= 0 when len(recent) <= limit
        """
        # Filter timestamps to get recent ones
        recent = [t for t in timestamps if t >= now - window]
        
        assume(len(recent) <= limit)
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        assert result[1] >= 0, f"Allowance {result[1]} should be >= 0"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_window_filtering_function_property(self, timestamps, now, window, limit):
        """
        Function property: len([t for t in timestamps if t >= now - window]) == len(recent)
        """
        # This property verifies that the function correctly filters timestamps
        # by the window parameter
        expected_recent = [t for t in timestamps if t >= now - window]
        
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        # The function should use exactly these filtered timestamps
        # We can't directly access 'recent' from the function, but we can verify
        # the filtering logic by checking the allowance calculation
        expected_allowance = limit - len(expected_recent)
        if len(expected_recent) <= limit:
            assert result[1] == expected_allowance, f"Allowance should match filtered count"
        else:
            assert result == (False, 0), f"Should block when filtered count exceeds limit"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_deterministic_output_function_property(self, timestamps, now, window, limit):
        """
        Function property: result is deterministic for same inputs
        """
        result1 = login_throttle(timestamps, now, window=window, limit=limit)
        result2 = login_throttle(timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Results should be deterministic: {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now1=st.integers(min_value=0),
        now2=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_time_monotonicity_function_property(self, timestamps, now1, now2, window, limit):
        """
        Function property: allowance increases with time (now2 >= now1)
        """
        assume(now2 >= now1)
        
        result1 = login_throttle(timestamps, now1, window=window, limit=limit)
        result2 = login_throttle(timestamps, now2, window=window, limit=limit)
        
        # As time increases, older timestamps fall out of the window,
        # so allowance should not decrease
        assert result2[1] >= result1[1], f"Allowance should be monotonic in time: {result2[1]} < {result1[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit1=st.integers(min_value=1),
        limit2=st.integers(min_value=1)
    )
    def test_limit_monotonicity_function_property(self, timestamps, now, window, limit1, limit2):
        """
        Function property: allowance increases with limit (limit2 >= limit1)
        """
        assume(limit2 >= limit1)
        
        result1 = login_throttle(timestamps, now, window=window, limit=limit1)
        result2 = login_throttle(timestamps, now, window=window, limit=limit2)
        
        # Higher limit should give higher or equal allowance
        assert result2[1] >= result1[1], f"Allowance should be monotonic in limit: {result2[1]} < {result1[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window1=st.integers(min_value=1),
        window2=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_window_monotonicity_function_property(self, timestamps, now, window1, window2, limit):
        """
        Function property: allowance decreases with window size (window2 >= window1)
        """
        assume(window2 >= window1)
        
        result1 = login_throttle(timestamps, now, window=window1, limit=limit)
        result2 = login_throttle(timestamps, now, window=window2, limit=limit)
        
        # Larger window includes more recent timestamps, so allowance should not increase
        assert result2[1] <= result1[1], f"Allowance should be monotonic in window: {result2[1]} > {result1[1]}"

    @given(
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_empty_timestamps_identity_function_property(self, now, window, limit):
        """
        Function property: (True, limit) when timestamps is empty
        """
        result = login_throttle([], now, window=window, limit=limit)
        
        assert result == (True, limit), f"Result {result} should be (True, limit) for empty timestamps"

    @given(
        timestamps=st.lists(st.integers(min_value=0), min_size=0),
        now=st.integers(min_value=0),
        window=st.integers(min_value=1),
        limit=st.integers(min_value=1)
    )
    def test_max_allowance_bound_function_property(self, timestamps, now, window, limit):
        """
        Function property: allowance <= limit
        """
        result = login_throttle(timestamps, now, window=window, limit=limit)
        
        assert result[1] <= limit, f"Allowance {result[1]} should be <= limit {limit}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])