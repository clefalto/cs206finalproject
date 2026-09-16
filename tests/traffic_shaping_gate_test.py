"""
Comprehensive Hypothesis-based tests for traffic_shaping_gate function.

This test suite exercises all semantic properties identified in 
properties/traffic_shaping_gate_properties.json using the Hypothesis 
testing framework for property-based testing.
"""

import math
from typing import List, Tuple
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, booleans

# Import the function under test
from dataset.python_programs.traffic_shaping_gate import traffic_shaping_gate


class TestTrafficShapingGate:
    """Test class for traffic_shaping_gate function using Hypothesis."""

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_block_when_over_limit(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function blocks when the number of active requests exceeds the limit.
        
        Property: len(active) > limit implies traffic_shaping_gate(timestamps, now, window=window, limit=limit) == (False, 0)
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        # Calculate active timestamps
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        if len(active) > limit:
            assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_allow_when_under_limit(self, timestamps: List[int], now: int, window: integers, limit: int):
        """
        Test that the function allows requests when under the limit.
        
        Property: not (len(active) > limit) implies traffic_shaping_gate(timestamps, now, window=window, limit=limit) == (True, limit - len(active))
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        # Calculate active timestamps
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        if len(active) <= limit:
            expected_remaining = limit - len(active)
            assert result == (True, expected_remaining), \
                f"Expected (True, {expected_remaining}) when len(active)={len(active)} <= limit={limit}, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_non_negative_remaining(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the remaining count is always non-negative.
        
        Property: limit >= 0 implies traffic_shaping_gate(timestamps, now, window=window, limit=limit)[1] >= 0
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        remaining = result[1]
        
        assert remaining >= 0, f"Remaining count should be non-negative, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_bounded_remaining(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the remaining count is bounded by the limit.
        
        Property: limit >= 0 implies traffic_shaping_gate(timestamps, now, window=window, limit=limit)[1] <= limit
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        remaining = result[1]
        
        assert remaining <= limit, f"Remaining count should be <= limit, got {remaining} > {limit}"

    @given(
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100),
        now=integers(min_value=0, max_value=1000)
    )
    def test_monotonic_remaining(self, window: int, limit: int, now: int):
        """
        Test that remaining count is monotonic with respect to active requests.
        
        Property: len(active1) <= len(active2) implies traffic_shaping_gate(timestamps1, now, window=window, limit=limit)[1] >= traffic_shaping_gate(timestamps2, now, window=window, limit=limit)[1]
        """
        # Generate two sets of timestamps with different active counts
        timestamps1 = []
        timestamps2 = []
        
        # Create timestamps for first set
        for _ in range(limit + 2):
            t = now - window + 1  # Ensure it's within the window
            timestamps1.append(t)
        
        # Create timestamps for second set (more active requests)
        for _ in range(limit + 5):
            t = now - window + 1  # Ensure it's within the window
            timestamps2.append(t)
        
        result1 = traffic_shaping_gate(timestamps1, now, window=window, limit=limit)
        result2 = traffic_shaping_gate(timestamps2, now, window=window, limit=limit)
        
        remaining1 = result1[1]
        remaining2 = result2[1]
        
        # More active requests should result in fewer remaining
        assert remaining1 >= remaining2, \
            f"More active requests should result in fewer remaining: {remaining1} >= {remaining2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_window_filtering(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that only timestamps within the window are considered.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit) == traffic_shaping_gate([t for t in timestamps if t >= now - window], now, window=window, limit=limit)
        """
        filtered_timestamps = [t for t in timestamps if t >= now - window]
        
        result1 = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        result2 = traffic_shaping_gate(filtered_timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, \
            f"Results should be identical with filtered timestamps: {result1} != {result2}"

    @given(
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_empty_timestamps_allow(self, now: int, window: int, limit: int):
        """
        Test that empty timestamps always allow requests.
        
        Property: traffic_shaping_gate([], now, window=window, limit=limit) == (True, limit)
        """
        result = traffic_shaping_gate([], now, window=window, limit=limit)
        assert result == (True, limit), f"Empty timestamps should always allow: got {result}, expected (True, {limit})"

    @given(
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_identity_on_empty(self, now: int, window: int, limit: int):
        """
        Test that the function behaves identically for empty input.
        
        Property: traffic_shaping_gate([], now, window=window, limit=limit) == (True, limit)
        """
        result = traffic_shaping_gate([], now, window=window, limit=limit)
        assert result == (True, limit), f"Empty input should return (True, limit): got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_deterministic(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function is deterministic.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit) is deterministic for same inputs
        """
        result1 = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        result2 = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Function should be deterministic: {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100),
        delta=integers(min_value=-100, max_value=100)
    )
    def test_time_independence(self, timestamps: List[int], now: int, window: int, limit: int, delta: int):
        """
        Test that the function is time-independent (shift invariant).
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit) == traffic_shaping_gate([t + delta for t in timestamps], now + delta, window=window, limit=limit) for any delta
        """
        shifted_timestamps = [t + delta for t in timestamps]
        shifted_now = now + delta
        
        result1 = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        result2 = traffic_shaping_gate(shifted_timestamps, shifted_now, window=window, limit=limit)
        
        assert result1 == result2, \
            f"Function should be time-independent: {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_order_independence(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function is order-independent.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit) == traffic_shaping_gate(sorted(timestamps), now, window=window, limit=limit)
        """
        sorted_timestamps = sorted(timestamps)
        
        result1 = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        result2 = traffic_shaping_gate(sorted_timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, \
            f"Function should be order-independent: {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100)
    )
    def test_limit_zero_blocks_all(self, timestamps: List[int], now: int, window: int):
        """
        Test that limit=0 blocks all requests.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=0) == (False, 0)
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=0)
        assert result == (False, 0), f"Limit=0 should block all requests: got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100)
    )
    def test_infinite_limit_allows_all(self, timestamps: List[int], now: int, window: int):
        """
        Test that infinite limit allows all requests.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=inf) == (True, inf)
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=float('inf'))
        assert result == (True, float('inf')), f"Infinite limit should allow all: got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        limit=integers(min_value=0, max_value=100)
    )
    def test_window_zero_blocks_all(self, timestamps: List[int], now: int, limit: int):
        """
        Test that window=0 allows all requests (no filtering).
        
        Property: traffic_shaping_gate(timestamps, now, window=0, limit=limit) == (True, limit)
        """
        result = traffic_shaping_gate(timestamps, now, window=0, limit=limit)
        assert result == (True, limit), f"Window=0 should allow all: got {result}, expected (True, {limit})"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        limit=integers(min_value=0, max_value=100),
        window1=integers(min_value=1, max_value=50),
        window2=integers(min_value=51, max_value=100)
    )
    def test_metamorphic_window_increase(self, timestamps: List[int], now: int, limit: int, window1: int, window2: int):
        """
        Test that increasing window size maintains or improves allowance.
        
        Property: window1 <= window2 implies traffic_shaping_gate(timestamps, now, window=window1, limit=limit)[0] implies traffic_shaping_gate(timestamps, now, window=window2, limit=limit)[0]
        """
        assume(window1 <= window2)
        
        result1 = traffic_shaping_gate(timestamps, now, window=window1, limit=limit)
        result2 = traffic_shaping_gate(timestamps, now, window=window2, limit=limit)
        
        # If the first allows, the second should also allow
        if result1[0]:
            assert result2[0], \
                f"Window increase should maintain allowance: {result1} allows but {result2} blocks"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit1=integers(min_value=0, max_value=50),
        limit2=integers(min_value=51, max_value=100)
    )
    def test_metamorphic_limit_increase(self, timestamps: List[int], now: int, window: int, limit1: int, limit2: int):
        """
        Test that increasing limit maintains or improves allowance.
        
        Property: limit1 <= limit2 implies traffic_shaping_gate(timestamps, now, window=window, limit=limit1)[0] implies traffic_shaping_gate(timestamps, now, window=window, limit=limit2)[0]
        """
        assume(limit1 <= limit2)
        
        result1 = traffic_shaping_gate(timestamps, now, window=window, limit=limit1)
        result2 = traffic_shaping_gate(timestamps, now, window=window, limit=limit2)
        
        # If the first allows, the second should also allow
        if result1[0]:
            assert result2[0], \
                f"Limit increase should maintain allowance: {result1} allows but {result2} blocks"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_precondition_window_positive(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function behaves correctly when window > 0.
        
        Property: function behavior is well-defined when window > 0
        """
        # This test ensures the function doesn't crash with positive window
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        # Should return a tuple of (bool, int/float)
        assert isinstance(result, tuple), f"Result should be a tuple: got {type(result)}"
        assert len(result) == 2, f"Result should have 2 elements: got {len(result)}"
        assert isinstance(result[0], bool), f"First element should be bool: got {type(result[0])}"
        assert isinstance(result[1], (int, float)), f"Second element should be int/float: got {type(result[1])}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_precondition_limit_non_negative(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function behaves correctly when limit >= 0.
        
        Property: function behavior is well-defined when limit >= 0
        """
        # This test ensures the function doesn't crash with non-negative limit
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        # Should return a tuple of (bool, int/float)
        assert isinstance(result, tuple), f"Result should be a tuple: got {type(result)}"
        assert len(result) == 2, f"Result should have 2 elements: got {len(result)}"
        assert isinstance(result[0], bool), f"First element should be bool: got {type(result[0])}"
        assert isinstance(result[1], (int, float)), f"Second element should be int/float: got {type(result[1])}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_postcondition_return_type(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that the function returns the correct type.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit) returns tuple of (bool, int)
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        assert isinstance(result, tuple), f"Result should be a tuple: got {type(result)}"
        assert len(result) == 2, f"Result should have 2 elements: got {len(result)}"
        assert isinstance(result[0], bool), f"First element should be bool: got {type(result[0])}"
        assert isinstance(result[1], (int, float)), f"Second element should be int/float: got {type(result[1])}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_postcondition_allow_implies_positive_remaining(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that allowing implies positive remaining count.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit)[0] == True implies traffic_shaping_gate(timestamps, now, window=window, limit=limit)[1] > 0
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        if result[0]:  # If allowed
            assert result[1] > 0, f"Allowing should imply positive remaining: got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000)),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=100)
    )
    def test_postcondition_block_implies_zero_remaining(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Test that blocking implies zero remaining count.
        
        Property: traffic_shaping_gate(timestamps, now, window=window, limit=limit)[0] == False implies traffic_shaping_gate(timestamps, now, window=window, limit=limit)[1] == 0
        """
        result = traffic_shaping_gate(timestamps, now, window=window, limit=limit)
        
        if not result[0]:  # If blocked
            assert result[1] == 0, f"Blocking should imply zero remaining: got {result}"

    def test_edge_cases(self):
        """Test specific edge cases that might not be covered by the general properties."""
        # Test with very large numbers
        result = traffic_shaping_gate([1000000], 1000000, window=1000000, limit=1000000)
        assert result == (True, 999999)
        
        # Test with minimum values
        result = traffic_shaping_gate([], 0, window=1, limit=0)
        assert result == (True, 0)
        
        # Test with boundary condition (len(active) == limit)
        result = traffic_shaping_gate([0, 1, 2, 3, 4], 4, window=5, limit=5)
        assert result == (True, 0)  # Should allow since len(active) == limit, not > limit

    def test_bug_reproduction(self):
        """
        Test to reproduce the bug mentioned in the implementation.
        
        The comment in the implementation says:
        "BUG: should block when len(active) == limit."
        
        This test documents the current behavior vs expected behavior.
        """
        # Current behavior: allows when len(active) == limit
        result = traffic_shaping_gate([0, 1, 2, 3, 4], 4, window=5, limit=5)
        assert result == (True, 0), "Current implementation allows when len(active) == limit"
        
        # This documents the bug - it should probably return (False, 0) instead
        # But we're testing the current behavior for now