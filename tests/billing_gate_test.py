"""
Hypothesis tests for billing_gate function semantic properties.

This test file exercises all semantic properties identified in
properties/billing_gate_properties.json using the Hypothesis testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple

# Import the function under test
from dataset.python_programs.billing_gate import billing_gate


class TestBillingGateProperties:
    """Test class for billing_gate semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boolean_return(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: boolean_return
        Formal: billing_gate(timestamps, now) returns (bool, int)
        """
        result = billing_gate(timestamps, now, window=window, limit=limit)
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 2, f"Expected tuple of length 2, got {len(result)}"
        assert isinstance(result[0], bool), f"Expected bool as first element, got {type(result[0])}"
        assert isinstance(result[1], int), f"Expected int as second element, got {type(result[1])}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_non_negative_capacity(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: non_negative_capacity
        Formal: billing_gate(timestamps, now)[1] >= 0
        """
        result = billing_gate(timestamps, now, window=window, limit=limit)
        capacity = result[1]
        assert capacity >= 0, f"Capacity should be non-negative, got {capacity}"

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
        Formal: billing_gate(timestamps, now)[1] <= limit
        """
        result = billing_gate(timestamps, now, window=window, limit=limit)
        capacity = result[1]
        assert capacity <= limit, f"Capacity {capacity} should not exceed limit {limit}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_deterministic(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: deterministic
        Formal: for same inputs, billing_gate(timestamps, now) always returns same output
        """
        result1 = billing_gate(timestamps, now, window=window, limit=limit)
        result2 = billing_gate(timestamps, now, window=window, limit=limit)
        assert result1 == result2, f"Function should be deterministic: {result1} != {result2}"

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
        Formal: billing_gate(timestamps, now) depends only on len(active) and limit, not on specific timestamp values
        """
        # Calculate active timestamps
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Create equivalent scenario with different timestamp values but same active count
        if len(active) > 0:
            # Create new timestamps where all active timestamps are shifted but maintain the same count
            new_active = [now - window + i for i in range(len(active))]
            new_timestamps = new_active + [0] * (len(timestamps) - len(active))  # inactive timestamps set to 0
        else:
            # If no active timestamps, create scenario with no active timestamps
            new_timestamps = [0] * len(timestamps)
        
        result1 = billing_gate(timestamps, now, window=window, limit=limit)
        result2 = billing_gate(new_timestamps, now, window=window, limit=limit)
        
        assert result1 == result2, f"Results should be the same regardless of specific timestamp values: {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_capacity_monotonicity(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: capacity_monotonicity
        Formal: if len(active1) <= len(active2) then billing_gate(timestamps1, now)[1] >= billing_gate(timestamps2, now)[1]
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Create a scenario with fewer or equal active timestamps
        if len(active) > 0:
            # Remove some active timestamps to create a scenario with fewer active items
            reduced_active_count = len(active) - 1
            new_timestamps = [now - window + i for i in range(reduced_active_count)] + [0] * (len(timestamps) - reduced_active_count)
            
            result1 = billing_gate(timestamps, now, window=window, limit=limit)
            result2 = billing_gate(new_timestamps, now, window=window, limit=limit)
            
            capacity1 = result1[1]
            capacity2 = result2[1]
            
            assert capacity2 >= capacity1, f"Capacity should be monotonic: fewer active items should give equal or greater capacity. {capacity2} < {capacity1}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_limit_exceeded_rejection(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: limit_exceeded_rejection
        Formal: if len(active) > limit then return False, 0
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        assume(len(active) > limit)  # Only test when condition is met
        
        result = billing_gate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"When len(active) > limit, should return (False, 0), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_limit_not_exceeded_approval(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: limit_not_exceeded_approval
        Formal: if not (len(active) > limit) then return True, limit - len(active)
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        assume(not (len(active) > limit))  # Only test when condition is met (len(active) <= limit)
        
        result = billing_gate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result == (True, expected_capacity), f"When len(active) <= limit, should return (True, {expected_capacity}), got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_capacity_return(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: capacity_return
        Formal: if not (len(active) > limit) then billing_gate(timestamps, now)[1] == limit - len(active)
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        assume(not (len(active) > limit))  # Only test when condition is met (len(active) <= limit)
        
        result = billing_gate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result[1] == expected_capacity, f"Capacity should be limit - len(active) = {expected_capacity}, got {result[1]}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=1000, deadline=None)
    def test_zero_capacity_on_rejection(self, timestamps: List[int], now: int, window: int, limit: int):
        """
        Property: zero_capacity_on_rejection
        Formal: if len(active) > limit then billing_gate(timestamps, now)[1] == 0
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        assume(len(active) > limit)  # Only test when condition is met
        
        result = billing_gate(timestamps, now, window=window, limit=limit)
        assert result[1] == 0, f"When len(active) > limit, capacity should be 0, got {result[1]}"


class TestBillingGateEdgeCases:
    """Test edge cases and specific scenarios for billing_gate."""

    @example(timestamps=[], now=0, window=10, limit=5)
    @example(timestamps=[0, 1, 2, 3, 4], now=10, window=10, limit=5)
    @example(timestamps=[0, 1, 2, 3, 4, 5], now=10, window=10, limit=5)
    @example(timestamps=[10, 10, 10, 10, 10], now=10, window=10, limit=5)
    @example(timestamps=[0, 0, 0, 0, 0], now=10, window=10, limit=5)
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
        result = billing_gate(timestamps, now, window=window, limit=limit)
        
        # Basic property checks
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], int)
        assert result[1] >= 0
        assert result[1] <= limit
        
        # Check the logic consistency
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        if len(active) > limit:
            assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"
        else:
            expected_capacity = limit - len(active)
            assert result == (True, expected_capacity), f"Expected (True, {expected_capacity}) when len(active)={len(active)} <= limit={limit}, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])