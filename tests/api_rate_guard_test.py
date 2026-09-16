"""
Comprehensive Hypothesis-based tests for api_rate_guard function.

This test file exercises all semantic properties identified in 
properties/api_rate_guard_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats, composite
from typing import List, Tuple


# Import the function under test
# Note: The actual import path may need to be adjusted based on project structure
# For now, we'll assume the function is available in the current context
# or will be imported from the dataset/python_programs directory

def api_rate_guard(timestamps, now, *, window=60, limit=100):
    """
    Simple rate guard for API calls.
    """
    cutoff = now - window
    recent = [t for t in timestamps if t >= cutoff]

    # BUG: boundary check allows one extra request.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)


# Strategy for generating valid timestamps
@composite
def valid_timestamps(draw, max_length=1000):
    """Generate a list of timestamps with reasonable constraints."""
    now = draw(floats(min_value=0, max_value=1e9))
    # Generate timestamps that could be in the past or recent
    timestamps = draw(lists(
        floats(min_value=0, max_value=now + 1000), 
        max_size=max_length
    ))
    return sorted(timestamps), now


class TestApiRateGuardProperties:
    """Test class for all semantic properties of api_rate_guard."""

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_return_type_consistency(self, timestamps, now, window, limit):
        """Property: return_type_consistency - Function returns tuple of length 2."""
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert isinstance(result, tuple)
        assert len(result) == 2

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_boolean_first_element(self, timestamps, now, window, limit):
        """Property: boolean_first_element - First element of return tuple is boolean."""
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert isinstance(result[0], bool)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_non_negative_second_element(self, timestamps, now, window, limit):
        """Property: non_negative_second_element - Second element of return tuple is non-negative."""
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert result[1] >= 0

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_limit_respect(self, timestamps, now, window, limit):
        """Property: limit_respect - Second element never exceeds the limit."""
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert result[1] <= limit

    @given(
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_empty_timestamps_allowed(self, now, window, limit):
        """Property: empty_timestamps_allowed - Empty timestamps list is handled correctly."""
        result = api_rate_guard([], now, window=window, limit=limit)
        assert result == (True, limit)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_window_boundary_consistency(self, timestamps, now, window, limit):
        """Property: window_boundary_consistency - Recent timestamps are within window, others are not."""
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # All recent timestamps should be >= cutoff
        for t in recent:
            assert t >= cutoff
        
        # All non-recent timestamps should be < cutoff
        for t in timestamps:
            if t not in recent:
                assert t < cutoff

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_rate_limit_exceeded_branch(self, timestamps, now, window, limit):
        """Property: rate_limit_exceeded - When len(recent) > limit, returns (False, 0)."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) > limit)
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert result == (False, 0)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_rate_limit_allowed_branch(self, timestamps, now, window, limit):
        """Property: rate_limit_allowed - When len(recent) <= limit, returns (True, limit - len(recent))."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) <= limit)
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        expected_quota = limit - len(recent)
        assert result == (True, expected_quota)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_boundary_bug_invariant(self, timestamps, now, window, limit):
        """Property: boundary_bug_invariant - When len(recent) == limit, returns (True, 0)."""
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) == limit)
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        assert result == (True, 0)

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now1=floats(min_value=0, max_value=1e9),
        now2=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_time_monotonicity(self, timestamps, now1, now2, window, limit):
        """Property: time_monotonicity - Later now values give equal or higher quota."""
        assume(now1 <= now2)
        
        result1 = api_rate_guard(timestamps, now1, window=window, limit=limit)
        result2 = api_rate_guard(timestamps, now2, window=window, limit=limit)
        
        # Later time should give equal or higher quota
        assert result1[1] <= result2[1]

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window1=integers(min_value=1, max_value=3600),
        window2=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_window_parameter_effect(self, timestamps, now, window1, window2, limit):
        """Property: window_parameter_effect - Larger window gives equal or higher quota."""
        assume(window1 <= window2)
        
        result1 = api_rate_guard(timestamps, now, window=window1, limit=limit)
        result2 = api_rate_guard(timestamps, now, window=window2, limit=limit)
        
        # Larger window should give equal or higher quota
        assert result1[1] <= result2[1]

    @given(
        timestamps=lists(floats(min_value=0, max_value=1e9), max_size=1000),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit1=integers(min_value=0, max_value=1000),
        limit2=integers(min_value=0, max_value=1000)
    )
    def test_limit_parameter_effect(self, timestamps, now, window, limit1, limit2):
        """Property: limit_parameter_effect - Larger limit gives equal or higher quota."""
        assume(limit1 <= limit2)
        
        result1 = api_rate_guard(timestamps, now, window=window, limit=limit1)
        result2 = api_rate_guard(timestamps, now, window=window, limit=limit2)
        
        # Larger limit should give equal or higher quota
        assert result1[1] <= result2[1]

    @given(
        timestamps1=lists(floats(min_value=0, max_value=1e9), max_size=500),
        timestamps2=lists(floats(min_value=0, max_value=1e9), max_size=500),
        now=floats(min_value=0, max_value=1e9),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=0, max_value=1000)
    )
    def test_monotonic_quota_decrease(self, timestamps1, timestamps2, now, window, limit):
        """Property: monotonic_quota_decrease - More timestamps give equal or lower quota."""
        assume(len(timestamps1) <= len(timestamps2))
        
        result1 = api_rate_guard(timestamps1, now, window=window, limit=limit)
        result2 = api_rate_guard(timestamps2, now, window=window, limit=limit)
        
        # More timestamps should give equal or lower quota
        assert result1[1] >= result2[1]


class TestApiRateGuardEdgeCases:
    """Additional edge case tests for api_rate_guard."""

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
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        
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
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
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
        
        result = api_rate_guard(timestamps, now, window=window, limit=limit)
        
        # Only timestamps >= cutoff should be counted as recent
        recent_count = sum(1 for t in timestamps if t >= cutoff)
        
        if recent_count > limit:
            assert result == (False, 0)
        else:
            assert result == (True, limit - recent_count)


if __name__ == "__main__":
    # This allows running the tests with python -m pytest
    pytest.main([__file__, "-v"])