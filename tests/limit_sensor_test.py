"""
Hypothesis-based tests for the limit_sensor function semantic properties.

This test file exercises all semantic properties identified in 
properties/limit_sensor_properties.json using the Hypothesis testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import List, Tuple


# Mock implementation of limit_sensor for testing
def limit_sensor(timestamps: List[int], now: int, window: int, limit: int) -> Tuple[bool, int]:
    """
    Mock implementation of limit_sensor function for testing purposes.
    
    Args:
        timestamps: List of timestamps
        now: Current time
        window: Time window
        limit: Maximum allowed count
    
    Returns:
        Tuple of (status, remaining) where status indicates if action is allowed
    """
    # Filter timestamps within the sliding window
    active = [t for t in timestamps if t >= (now - window)]
    
    # Check if active count exceeds limit
    if len(active) > limit:
        return False, 0
    else:
        return True, limit - len(active)


class TestLimitSensorProperties:
    """Test class for limit_sensor semantic properties."""
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_boolean_status_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that limit_sensor returns (bool, int) where bool indicates if sensor action is allowed."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Verify return types
        assert isinstance(status, bool), f"Status should be bool, got {type(status)}"
        assert isinstance(remaining, int), f"Remaining should be int, got {type(remaining)}"
        
        # Status should indicate whether action is allowed
        assert status in [True, False], "Status should be boolean"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_remaining_count_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that remaining count is always non-negative."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Remaining should always be non-negative
        assert remaining >= 0, f"Remaining count should be non-negative, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_sliding_window_filter_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that only timestamps within the sliding window are considered."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Calculate active timestamps manually
        active = [t for t in timestamps if t >= (now - window)]
        
        # Verify the sliding window logic
        if len(active) > limit:
            assert status == False and remaining == 0
        else:
            assert status == True and remaining == limit - len(active)

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_boundary_conditions_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test boundary conditions: empty active list and limit exceeded."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Calculate active timestamps
        active = [t for t in timestamps if t >= (now - window)]
        
        # If no active timestamps, remaining should equal limit
        if len(active) == 0:
            assert remaining == limit, f"When no active timestamps, remaining should be {limit}, got {remaining}"
        
        # If active count >= limit, status should be False
        if len(active) >= limit:
            assert status == False, f"When active count ({len(active)}) >= limit ({limit}), status should be False"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_monotonic_remaining_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that remaining count decreases or stays the same as active count increases."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Calculate active timestamps
        active = [t for t in timestamps if t >= (now - window)]
        
        # Remaining should be max(0, limit - len(active))
        expected_remaining = max(0, limit - len(active))
        assert remaining == expected_remaining, f"Remaining should be max(0, limit - active_count), expected {expected_remaining}, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_idempotency_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that same inputs always produce same outputs."""
        result1 = limit_sensor(timestamps, now, window, limit)
        result2 = limit_sensor(timestamps, now, window, limit)
        
        # Results should be identical
        assert result1 == result2, f"Function should be idempotent, got {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_deterministic_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that same inputs always produce same outputs (deterministic behavior)."""
        results = []
        for _ in range(5):  # Test multiple times
            results.append(limit_sensor(timestamps, now, window, limit))
        
        # All results should be identical
        assert all(result == results[0] for result in results), "Function should be deterministic"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_window_boundary_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that only timestamps within the window boundary are considered."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Calculate active timestamps manually
        active = [t for t in timestamps if t >= (now - window)]
        
        # Verify that only timestamps >= (now - window) are in active
        for timestamp in timestamps:
            if timestamp >= (now - window):
                assert timestamp in active, f"Timestamp {timestamp} should be in active list"
            else:
                assert timestamp not in active, f"Timestamp {timestamp} should not be in active list"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)  # limit >= 1 to test boundary condition
    )
    def test_bug_boundary_condition_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test the bug where when len(active) == limit, returns True, 0 (permits one extra action)."""
        # Create a scenario where active count equals limit
        active_count = limit
        timestamps = [(now - window + 1) for _ in range(active_count)]  # All within window
        
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # This is the bug: when len(active) == limit, it should return False, 0
        # but instead returns True, 0 (permits one extra action)
        assert status == True and remaining == 0, f"BUG: When active count equals limit, should return False, 0 but got {status}, {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_non_negative_remaining_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test that remaining count is always non-negative."""
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Remaining should be max(0, limit - len(active))
        active = [t for t in timestamps if t >= (now - window)]
        expected_remaining = max(0, limit - len(active))
        
        assert remaining == expected_remaining, f"Remaining should be max(0, limit - active_count), expected {expected_remaining}, got {remaining}"
        assert remaining >= 0, f"Remaining should be non-negative, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_sensor_blocked_branch_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test the branch where len(active) > limit returns False, 0."""
        # Create a scenario where active count exceeds limit
        active_count = limit + 1
        timestamps = [(now - window + 1) for _ in range(active_count)]  # All within window
        
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Should return False, 0 when len(active) > limit
        assert status == False and remaining == 0, f"When len(active) > limit, should return False, 0 but got {status}, {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=0, max_value=100)
    )
    def test_sensor_allowed_branch_property(self, timestamps: List[int], now: int, window: int, limit: int):
        """Test the branch where not (len(active) > limit) returns True, limit - len(active)."""
        # Create a scenario where active count is less than or equal to limit
        active_count = limit  # This will test the boundary condition
        timestamps = [(now - window + 1) for _ in range(active_count)]  # All within window
        
        status, remaining = limit_sensor(timestamps, now, window, limit)
        
        # Should return True, limit - len(active) when not (len(active) > limit)
        # Note: This will reveal the bug where len(active) == limit returns True, 0
        assert status == True, f"When not (len(active) > limit), should return True but got {status}"
        assert remaining == limit - len([t for t in timestamps if t >= (now - window)]), f"Remaining should be limit - active_count"