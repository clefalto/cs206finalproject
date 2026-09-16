"""
Hypothesis tests for notification_gate function semantic properties.

This test file exercises all semantic properties identified in
properties/notification_gate_properties.json using the Hypothesis testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple

# Import the function under test
from dataset.python_programs.notification_gate import notification_gate


class TestNotificationGateProperties:
    """Test class for notification_gate semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boolean_result(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: boolean_result
        Formal: type(notification_gate(timestamps, now, window=window, limit=limit)[0]) == bool
        """
        assume(limit >= 0)
        result = notification_gate(timestamps, now, window=window, limit=limit)
        assert isinstance(result[0], bool), f"First element should be bool, got {type(result[0])}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_non_negative_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: non_negative_quota
        Formal: notification_gate(timestamps, now, window=window, limit=limit)[1] >= 0
        """
        assume(limit >= 0)
        result = notification_gate(timestamps, now, window=window, limit=limit)
        quota = result[1]
        assert quota >= 0, f"Quota should be non-negative, got {quota}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_limit_bound(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: limit_bound
        Formal: notification_gate(timestamps, now, window=window, limit=limit)[1] <= limit
        """
        assume(limit >= 0)
        result = notification_gate(timestamps, now, window=window, limit=limit)
        quota = result[1]
        assert quota <= limit, f"Quota {quota} should not exceed limit {limit}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_remaining_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: remaining_quota
        Formal: notification_gate(timestamps, now, window=window, limit=limit)[1] == max(0, limit - len([t for t in timestamps if t >= now - window]))
        """
        assume(limit >= 0)
        result = notification_gate(timestamps, now, window=window, limit=limit)
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        expected_quota = max(0, limit - recent_count)
        assert result[1] == expected_quota, f"Quota should be max(0, limit - recent_count) = {expected_quota}, got {result[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limiting(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limiting
        Formal: if len([t for t in timestamps if t >= now - window]) > limit then notification_gate(timestamps, now, window=window, limit=limit) == (False, 0)
        """
        assume(limit >= 0)
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count > limit)  # Only test when condition is met
        
        result = notification_gate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"When recent_count > limit, should return (False, 0), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_exact_at_limit_allowed(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: exact_at_limit_allowed
        Formal: if len([t for t in timestamps if t >= now - window]) == limit then notification_gate(timestamps, now, window=window, limit=limit) == (True, 0)
        """
        assume(limit >= 0)
        window_start = now - window
        recent_count = len([t for t in timestamps if t >= window_start])
        
        assume(recent_count == limit)  # Only test when condition is met
        
        result = notification_gate(timestamps, now, window=window, limit=limit)
        assert result == (True, 0), f"When recent_count == limit, should return (True, 0), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_window_filtering(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: window_filtering
        Formal: notification_gate(timestamps, now, window=window, limit=limit) depends only on timestamps within [now - window, now]
        """
        assume(limit >= 0)
        window_start = now - window
        
        # Filter to only timestamps within the window
        filtered_timestamps = [t for t in timestamps if window_start <= t <= now]
        
        result1 = notification_gate(timestamps, now, window=window, limit=limit)
        result2 = notification_gate(filtered_timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Results should be the same when filtering to window: {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_monotonic_quota(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: monotonic_quota
        Formal: adding older timestamps (outside window) does not change the result
        """
        assume(limit >= 0)
        window_start = now - window
        
        # Create additional timestamps that are outside the window (older)
        older_timestamps = [t for t in range(window_start - 100, window_start) if t not in timestamps]
        
        if older_timestamps:
            # Add some older timestamps
            extended_timestamps = timestamps + older_timestamps[:10]  # Add up to 10 older timestamps
            
            result1 = notification_gate(timestamps, now, window=window, limit=limit)
            result2 = notification_gate(extended_timestamps, now, window=window, limit=limit)
            
            assert result1 == result2, f"Adding older timestamps should not change result: {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_time_independence(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: time_independence
        Formal: shifting all timestamps and now by the same amount does not change the result
        """
        assume(limit >= 0)
        
        # Choose a shift amount
        shift = st.integers(min_value=-100, max_value=100).example()
        
        shifted_timestamps = [t + shift for t in timestamps]
        shifted_now = now + shift
        
        result1 = notification_gate(timestamps, now, window=window, limit=limit)
        result2 = notification_gate(shifted_timestamps, shifted_now, window=window, limit=limit)
        
        assert result1 == result2, f"Shifting timestamps and now should not change result: {result1} != {result2}"


class TestNotificationGateBranchProperties:
    """Test class for notification_gate branch-specific properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_exceeded_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limit_exceeded (branch)
        Condition: len(recent) > limit
        Formal: notification_gate(timestamps, now, window=window, limit=limit) == (False, 0)
        """
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        assume(len(recent) > limit)  # Branch condition
        
        result = notification_gate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Branch condition len(recent) > limit should return (False, 0), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_allowed_branch(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: rate_limit_allowed (branch)
        Condition: not (len(recent) > limit)
        Formal: notification_gate(timestamps, now, window=window, limit=limit) == (True, limit - len(recent))
        """
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        assume(not (len(recent) > limit))  # Branch condition (equivalent to len(recent) <= limit)
        
        result = notification_gate(timestamps, now, window=window, limit=limit)
        expected_quota = limit - len(recent)
        assert result == (True, expected_quota), f"Branch condition not (len(recent) > limit) should return (True, {expected_quota}), got {result}"


class TestNotificationGateEdgeCases:
    """Test edge cases and specific scenarios for notification_gate."""

    @example(timestamps=[], now=0, window=10, limit=5)
    @example(timestamps=[0, 1, 2, 3, 4], now=10, window=10, limit=5)
    @example(timestamps=[0, 1, 2, 3, 4, 5], now=10, window=10, limit=5)
    @example(timestamps=[10, 10, 10, 10, 10], now=10, window=10, limit=5)
    @example(timestamps=[0, 0, 0, 0, 0], now=10, window=10, limit=5)
    @example(timestamps=[5, 6, 7, 8, 9], now=10, window=5, limit=3)
    @example(timestamps=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], now=10, window=3, limit=2)
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_edge_cases(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test specific edge cases and boundary conditions.
        """
        assume(limit >= 0)
        result = notification_gate(timestamps, now, window=window, limit=limit)
        
        # Basic property checks
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], int)
        assert result[1] >= 0
        assert result[1] <= limit
        
        # Check the logic consistency
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        if len(recent) > limit:
            assert result == (False, 0), f"Expected (False, 0) when len(recent)={len(recent)} > limit={limit}, got {result}"
        else:
            expected_quota = limit - len(recent)
            assert result == (True, expected_quota), f"Expected (True, {expected_quota}) when len(recent)={len(recent)} <= limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=500, deadline=None)
    def test_deterministic(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function is deterministic (same inputs always produce same outputs).
        """
        assume(limit >= 0)
        result1 = notification_gate(timestamps, now, window=window, limit=limit)
        result2 = notification_gate(timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Function should be deterministic: {result1} != {result2}"


class TestNotificationGateBugDetection:
    """Test class to detect the specific bug mentioned in the implementation."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_bug_detection_exact_limit(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test to detect the bug where exactly-at-limit traffic is allowed.
        The comment in the code says "BUG: allows exactly-at-limit traffic."
        This test documents this behavior as part of the current implementation.
        """
        assume(limit >= 0)
        window_start = now - window
        recent = [t for t in timestamps if t >= window_start]
        
        assume(len(recent) == limit)  # Exactly at the limit
        
        result = notification_gate(timestamps, now, window=window, limit=limit)
        
        # According to the bug comment, this should return (True, 0) when exactly at limit
        # This test documents the current behavior
        assert result == (True, 0), f"At exactly limit, should return (True, 0) due to bug, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])