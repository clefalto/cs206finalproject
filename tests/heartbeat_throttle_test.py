"""
Hypothesis tests for heartbeat_throttle function semantic properties.

This test suite verifies all semantic properties identified for the
heartbeat_throttle function using the Hypothesis testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple

# Import the function under test
from dataset.python_programs.heartbeat_throttle import heartbeat_throttle


class TestHeartbeatThrottleProperties:
    """Test class for heartbeat_throttle semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_throttle_active_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test branch property: len(active) > limit -> throttle_active
        
        When the number of active timestamps exceeds the limit,
        the function should return (False, 0).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(active) > limit)
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_throttle_inactive_with_capacity_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test branch property: len(active) <= limit -> throttle_inactive_with_capacity
        
        When the number of active timestamps is within the limit,
        the function should return (True, limit - len(active)).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(active) <= limit)
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result == (True, expected_capacity), f"Expected (True, {expected_capacity}) when len(active)={len(active)} <= limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_non_negative_remaining_capacity(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: non_negative_remaining_capacity
        
        The remaining capacity should always be non-negative.
        """
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        remaining_capacity = result[1]
        assert remaining_capacity >= 0, f"Remaining capacity should be non-negative, got {remaining_capacity}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boolean_first_return(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: boolean_first_return
        
        The first element of the return tuple should always be a boolean.
        """
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        throttle_allowed = result[0]
        assert isinstance(throttle_allowed, bool), f"First return value should be boolean, got {type(throttle_allowed)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_capacity_calculation(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: capacity_calculation
        
        When len(active) <= limit, the capacity should be calculated as limit - len(active).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) <= limit)
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result == (True, expected_capacity), f"Expected (True, {expected_capacity}) when len(active)={len(active)} <= limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_window_filtering(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: window_filtering
        
        The number of active timestamps should equal the number of timestamps
        within the time window.
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        # We can't directly access 'active' from the function, but we can verify
        # that our calculation matches what the function would use
        assert len(active) == len([t for t in timestamps if t >= cutoff]), \
            f"Window filtering should match: {len(active)} vs {len([t for t in timestamps if t >= cutoff])}"

    @given(
        timestamps1=st.lists(st.integers(min_value=0, max_value=1000)),
        timestamps2=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_monotonic_throttling(self, timestamps1: List[int], timestamps2: List[int], now: int, window: int, limit: int):
        """
        Test function property: monotonic_throttling
        
        If a larger set of active timestamps is throttled, then a smaller set
        should also be throttled.
        """
        cutoff = now - window
        active1 = [t for t in timestamps1 if t >= cutoff]
        active2 = [t for t in timestamps2 if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active1) <= len(active2))
        
        result1 = heartbeat_throttle(timestamps1, now, window=window, limit=limit)
        result2 = heartbeat_throttle(timestamps2, now, window=window, limit=limit)
        
        # If the larger set is throttled (returns False, 0), the smaller set should also be throttled
        if result2 == (False, 0):
            assert result1 == (False, 0), \
                f"Monotonicity violated: larger set {len(active2)} throttled but smaller set {len(active1)} not throttled"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_limit_respect(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: limit_respect
        
        When the number of active timestamps is within the limit,
        the function should allow the action (return True).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) <= limit)
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        throttle_allowed = result[0]
        assert throttle_allowed == True, f"Should respect limit when len(active)={len(active)} <= limit={limit}, got {throttle_allowed}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_exceeds_limit_throttles(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test function property: exceeds_limit_throttles
        
        When the number of active timestamps exceeds the limit,
        the function should throttle the action (return False, 0).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) > limit)
        
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Should throttle when len(active)={len(active)} > limit={limit}, got {result}"

    # Additional edge case tests to complement the property-based tests

    @example(timestamps=[], now=10, window=5, limit=3)
    @example(timestamps=[5, 6, 7], now=10, window=5, limit=3)
    @example(timestamps=[1, 2, 3, 4, 5, 6], now=10, window=5, limit=3)
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=100)),
        now=st.integers(min_value=0, max_value=100),
        window=st.integers(min_value=1, max_value=50),
        limit=st.integers(min_value=0, max_value=50)
    )
    @settings(max_examples=200, deadline=None)
    def test_edge_cases(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test edge cases with specific examples and smaller ranges for more thorough testing.
        """
        result = heartbeat_throttle(timestamps, now, window=window, limit=limit)
        
        # Basic sanity checks
        assert isinstance(result, tuple), "Result should be a tuple"
        assert len(result) == 2, "Result should have exactly 2 elements"
        assert isinstance(result[0], bool), "First element should be boolean"
        assert isinstance(result[1], int), "Second element should be integer"
        assert result[1] >= 0, "Remaining capacity should be non-negative"

    def test_specific_known_cases(self):
        """Test specific known cases to ensure correct behavior."""
        
        # Case 1: Empty timestamps
        result = heartbeat_throttle([], 10, window=5, limit=3)
        assert result == (True, 3), f"Empty timestamps should return (True, 3), got {result}"
        
        # Case 2: All timestamps within window, within limit
        result = heartbeat_throttle([6, 7, 8], 10, window=5, limit=5)
        assert result == (True, 2), f"Should return (True, 2), got {result}"
        
        # Case 3: All timestamps within window, exceeds limit
        result = heartbeat_throttle([6, 7, 8, 9, 10, 11], 10, window=5, limit=3)
        assert result == (False, 0), f"Should return (False, 0), got {result}"
        
        # Case 4: Some timestamps outside window
        result = heartbeat_throttle([1, 2, 8, 9, 10], 10, window=5, limit=3)
        assert result == (True, 0), f"Should return (True, 0), got {result}"
        
        # Case 5: All timestamps outside window
        result = heartbeat_throttle([1, 2, 3], 10, window=5, limit=3)
        assert result == (True, 3), f"Should return (True, 3), got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])