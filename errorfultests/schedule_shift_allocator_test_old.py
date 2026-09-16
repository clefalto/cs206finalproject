#!/usr/bin/env python3
"""
Hypothesis-based property tests for schedule_shift_allocator function.

This test file exercises all 16 semantic properties identified in
properties/schedule_shift_allocator_properties.json using the Hypothesis
testing framework to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
# Note: The actual implementation should be imported from the source code
# For now, we'll define a placeholder that raises NotImplementedError
def schedule_shift_allocator(total, weights, minimum=0):
    """
    Placeholder implementation - replace with actual function.
    
    Args:
        total: Total amount to allocate
        weights: List of weights for proportional allocation
        minimum: Minimum allocation for each weight
        
    Returns:
        List of allocations
    """
    raise NotImplementedError("Replace with actual schedule_shift_allocator implementation")


class TestScheduleShiftAllocatorProperties:
    """Test class for schedule_shift_allocator semantic properties."""
    
    # Hypothesis strategies for generating test data
    valid_totals = st.integers(min_value=0, max_value=10000)
    valid_minimums = st.integers(min_value=0, max_value=1000)
    valid_weights = st.lists(
        st.integers(min_value=0, max_value=1000), 
        min_size=1, 
        max_size=50
    ).filter(lambda w: sum(w) > 0)
    
    @given(total=st.integers(max_value=-1))
    def test_rejects_negative_total(self, total):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            schedule_shift_allocator(total, [1, 2, 3])
    
    @given(minimum=st.integers(max_value=-1))
    def test_rejects_negative_minimum(self, minimum):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            schedule_shift_allocator(100, [1, 2, 3], minimum=minimum)
    
    @given(weights=st.lists(st.integers(min_value=0), max_size=50))
    def test_rejects_invalid_weights(self, weights):
        """Test that invalid weights (empty or sum to zero) raise ValueError."""
        assume(not weights or sum(weights) == 0)
        with pytest.raises(ValueError, match="invalid weights"):
            schedule_shift_allocator(100, weights)
    
    @given(weights=valid_weights, minimum=valid_minimums)
    def test_zero_total_allocation(self, weights, minimum):
        """Test that zero total results in all allocations being minimum values."""
        result = schedule_shift_allocator(0, weights, minimum=minimum)
        expected = [minimum] * len(weights)
        assert result == expected
    
    @given(total=valid_totals, minimum=valid_minimums)
    def test_single_weight_allocation(self, total, minimum):
        """Test allocation with single weight equals min(minimum, total)."""
        weights = [1]  # Single weight
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        expected = [min(minimum, total)]
        assert result == expected
    
    @given(weights=st.lists(st.integers(min_value=0), min_size=1, max_size=50))
    def test_zero_weights_allocation(self, weights):
        """Test that all-zero weights raise ValueError."""
        assume(all(w == 0 for w in weights))
        with pytest.raises(ValueError, match="invalid weights"):
            schedule_shift_allocator(100, weights)
    
    @given(total=valid_totals, weights=valid_weights, minimum=valid_minimums)
    def test_non_negative_allocations(self, total, weights, minimum):
        """Test that all allocations are non-negative."""
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        assert all(allocation >= 0 for allocation in result)
    
    @given(total=valid_totals, weights=valid_weights, minimum=valid_minimums)
    def test_minimum_guarantee(self, total, weights, minimum):
        """Test that all allocations meet minimum requirement."""
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        assert all(allocation >= minimum for allocation in result)
    
    @given(weights=valid_weights, total=valid_totals, minimum=valid_minimums)
    def test_allocation_length_preservation(self, weights, total, minimum):
        """Test that result length equals weights length."""
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        assert len(result) == len(weights)
    
    @given(total=valid_totals, weights=valid_weights, minimum=valid_minimums)
    def test_integer_allocations(self, total, weights, minimum):
        """Test that all allocations are integers."""
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        assert all(isinstance(allocation, int) for allocation in result)
    
    @given(
        total1=st.integers(min_value=0, max_value=5000),
        total2=st.integers(min_value=0, max_value=5000),
        weights=valid_weights,
        minimum=valid_minimums
    )
    def test_monotonic_total(self, total1, total2, weights, minimum):
        """Test that increasing total doesn't decrease any allocation."""
        assume(total1 <= total2)
        
        result1 = schedule_shift_allocator(total1, weights, minimum=minimum)
        result2 = schedule_shift_allocator(total2, weights, minimum=minimum)
        
        assert all(result1[i] <= result2[i] for i in range(len(weights)))
    
    @given(
        total=valid_totals,
        weights=valid_weights,
        minimum=valid_minimums,
        k=st.floats(min_value=0.1, max_value=100.0)
    )
    def test_scale_invariance_weights(self, total, weights, minimum, k):
        """Test that scaling weights doesn't change allocation."""
        scaled_weights = [int(k * w) for w in weights]
        assume(sum(scaled_weights) > 0)  # Ensure scaled weights are valid
        
        result1 = schedule_shift_allocator(total, weights, minimum=minimum)
        result2 = schedule_shift_allocator(total, scaled_weights, minimum=minimum)
        
        assert result1 == result2
    
    @given(
        total=st.integers(min_value=1, max_value=1000),
        weights=valid_weights,
        minimum=valid_minimums,
        k=st.integers(min_value=1, max_value=10)
    )
    def test_scale_invariance_total(self, total, weights, minimum, k):
        """Test that scaling total scales allocations proportionally."""
        result1 = schedule_shift_allocator(total, weights, minimum=minimum)
        result2 = schedule_shift_allocator(k * total, weights, minimum=minimum)
        
        expected = [k * x for x in result1]
        assert result2 == expected
    
    @given(total=valid_totals, weights=valid_weights, minimum=valid_minimums)
    def test_remainder_loss_bug(self, total, weights, minimum):
        """Test that sum of allocations doesn't exceed total (due to truncation)."""
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        assert sum(result) <= total
    
    @given(
        total=st.integers(min_value=1000, max_value=10000),  # Large total for proportionality
        weights=st.lists(
            st.integers(min_value=1, max_value=100), 
            min_size=2, 
            max_size=10
        ),
        minimum=st.integers(min_value=0, max_value=10)
    )
    def test_proportional_allocation(self, total, weights, minimum):
        """Test that allocations are approximately proportional to weights."""
        assume(sum(weights) > 0)
        
        result = schedule_shift_allocator(total, weights, minimum=minimum)
        
        # Check that proportions are approximately maintained
        # Allow for some tolerance due to integer truncation
        for i in range(len(weights)):
            for j in range(len(weights)):
                if i != j and weights[i] > 0 and weights[j] > 0:
                    ratio_result = result[i] / result[j] if result[j] > 0 else float('inf')
                    ratio_weights = weights[i] / weights[j]
                    
                    # Allow 10% tolerance for proportionality due to integer arithmetic
                    tolerance = 0.1
                    assert abs(ratio_result - ratio_weights) / ratio_weights <= tolerance
    
    def test_error_conditions(self):
        """Test that all error conditions raise ValueError."""
        # Test negative total
        with pytest.raises(ValueError):
            schedule_shift_allocator(-1, [1, 2, 3])
        
        # Test negative minimum
        with pytest.raises(ValueError):
            schedule_shift_allocator(100, [1, 2, 3], minimum=-1)
        
        # Test empty weights
        with pytest.raises(ValueError):
            schedule_shift_allocator(100, [])
        
        # Test zero weights
        with pytest.raises(ValueError):
            schedule_shift_allocator(100, [0, 0, 0])


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])