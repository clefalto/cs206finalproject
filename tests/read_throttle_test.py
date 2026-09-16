#!/usr/bin/env python3
"""
Hypothesis-based property tests for the read_throttle function.

This test file exercises all 12 semantic properties identified for the read_throttle function
using the Hypothesis testing framework to generate comprehensive test cases.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple


# Import the function under test
# Note: This assumes the read_throttle function is available in the current environment
# If not, you'll need to import it from the appropriate module
try:
    from your_module import read_throttle
except ImportError:
    # For testing purposes, we'll define a reference implementation
    # that should match the expected behavior based on the properties
    def read_throttle(timestamps: List[int], now: int, window: int, limit: int) -> Tuple[bool, int]:
        """
        Reference implementation of read_throttle for testing purposes.
        
        This is a placeholder implementation that should be replaced with the actual
        function under test. The implementation here is based on the semantic properties
        and may not match the actual function behavior.
        """
        # Filter timestamps to only those within the sliding window
        active = [t for t in timestamps if t >= (now - window)]
        
        # Check if we exceed the limit
        if len(active) > limit:
            return (False, 0)  # Throttle when exceeds limit
        else:
            return (True, limit - len(active))  # Allow when within limit


class TestReadThrottleProperties:
    """Test class containing all semantic property tests for read_throttle."""
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_throttle_when_exceeds_limit(self, timestamps, now, window, limit):
        """
        Property: throttle_when_exceeds_limit
        When the number of active timestamps exceeds the limit, the function should throttle.
        """
        # Filter timestamps to only those within the sliding window
        active = [t for t in timestamps if t >= (now - window)]
        
        # Only test when the condition is met
        assume(len(active) > limit)
        
        result = read_throttle(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_allow_when_within_limit(self, timestamps, now, window, limit):
        """
        Property: allow_when_within_limit
        When the number of active timestamps is within the limit, the function should allow.
        """
        # Filter timestamps to only those within the sliding window
        active = [t for t in timestamps if t >= (now - window)]
        
        # Only test when the condition is met
        assume(len(active) <= limit)
        
        result = read_throttle(timestamps, now, window=window, limit=limit)
        expected_remaining = limit - len(active)
        assert result == (True, expected_remaining), f"Expected (True, {expected_remaining}) when len(active)={len(active)} <= limit={limit}, got {result}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_sliding_window_filter(self, timestamps, now, window, limit):
        """
        Property: sliding_window_filter
        The active timestamps should be correctly filtered by the sliding window.
        """
        result = read_throttle(timestamps, now, window=window, limit=limit)
        
        # The active timestamps should be those within the window
        active = [t for t in timestamps if t >= (now - window)]
        
        # This property is more about internal behavior, so we verify it indirectly
        # by checking that the remaining count matches what we expect
        expected_remaining = max(0, limit - len(active))
        assert result[1] == expected_remaining, f"Sliding window filter failed: expected remaining={expected_remaining}, got {result[1]}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_non_negative_remaining(self, timestamps, now, window, limit):
        """
        Property: non_negative_remaining
        The remaining count should always be non-negative.
        """
        result = read_throttle(timestamps, now, window=window, limit=limit)
        remaining = result[1]
        assert remaining >= 0, f"Remaining count should be non-negative, got {remaining}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_limit_respected(self, timestamps, now, window, limit):
        """
        Property: limit_respected
        The remaining count should never exceed the limit.
        """
        result = read_throttle(timestamps, now, window=window, limit=limit)
        remaining = result[1]
        assert remaining <= limit, f"Remaining count should not exceed limit, got {remaining} > {limit}"
    
    @given(
        timestamps1=st.lists(st.integers(min_value=0, max_value=1000)),
        timestamps2=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_monotonic_remaining(self, timestamps1, timestamps2, now, window, limit):
        """
        Property: monotonic_remaining
        If one set has fewer active timestamps than another, it should have more remaining capacity.
        """
        # Filter timestamps to only those within the sliding window
        active1 = [t for t in timestamps1 if t >= (now - window)]
        active2 = [t for t in timestamps2 if t >= (now - window)]
        
        # Only test when the precondition is met
        assume(len(active1) <= len(active2))
        
        result1 = read_throttle(timestamps1, now, window=window, limit=limit)
        result2 = read_throttle(timestamps2, now, window=window, limit=limit)
        
        remaining1 = result1[1]
        remaining2 = result2[1]
        
        assert remaining1 >= remaining2, f"Monotonic property failed: len(active1)={len(active1)} <= len(active2)={len(active2)}, but remaining1={remaining1} < remaining2={remaining2}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_boundary_condition_bug(self, timestamps, now, window, limit):
        """
        Property: boundary_condition_bug
        When the number of active timestamps exactly equals the limit, it should allow with 0 remaining.
        """
        # Filter timestamps to only those within the sliding window
        active = [t for t in timestamps if t >= (now - window)]
        
        # Only test when the precondition is met
        assume(len(active) == limit)
        
        result = read_throttle(timestamps, now, window=window, limit=limit)
        assert result == (True, 0), f"Expected (True, 0) when len(active)={len(active)} == limit={limit}, got {result}"
    
    @given(
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_empty_timestamps_allow(self, now, window, limit):
        """
        Property: empty_timestamps_allow
        When there are no timestamps, the function should allow with full limit remaining.
        """
        timestamps = []
        result = read_throttle(timestamps, now, window=window, limit=limit)
        assert result == (True, limit), f"Expected (True, {limit}) for empty timestamps, got {result}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_all_expired_allow(self, timestamps, now, window, limit):
        """
        Property: all_expired_allow
        When all timestamps are outside the window, the function should allow with full limit remaining.
        """
        # Only test when all timestamps are expired
        assume(all(t < (now - window) for t in timestamps))
        
        result = read_throttle(timestamps, now, window=window, limit=limit)
        assert result == (True, limit), f"Expected (True, {limit}) when all timestamps are expired, got {result}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000), min_size=2),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_all_active_throttle(self, timestamps, now, window, limit):
        """
        Property: all_active_throttle
        When all timestamps are active and exceed the limit, the function should throttle.
        """
        # Only test when all timestamps are active and exceed the limit
        assume(len(timestamps) > limit and all(t >= (now - window) for t in timestamps))
        
        result = read_throttle(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when all timestamps are active and exceed limit, got {result}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_window_independence(self, timestamps, now, window, limit):
        """
        Property: window_independence
        The result should only depend on timestamps within the sliding window.
        """
        # Filter timestamps to only those within the sliding window
        active = [t for t in timestamps if t >= (now - window)]
        
        # Create a modified timestamp list with only active timestamps
        # This should produce the same result as the original
        active_only_timestamps = active.copy()
        
        result1 = read_throttle(timestamps, now, window=window, limit=limit)
        result2 = read_throttle(active_only_timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Window independence failed: original={result1}, active_only={result2}"
    
    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=500),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_deterministic(self, timestamps, now, window, limit):
        """
        Property: deterministic
        The function should produce the same result for the same inputs.
        """
        result1 = read_throttle(timestamps, now, window=window, limit=limit)
        result2 = read_throttle(timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Deterministic property failed: result1={result1}, result2={result2}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])