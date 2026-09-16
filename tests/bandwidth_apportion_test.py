"""
Hypothesis-based tests for bandwidth_apportion function semantic properties.

This test file exercises all 11 semantic properties identified for the
bandwidth_apportion function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, integers, lists, one_of
import math


def bandwidth_apportion(total, weights, minimum=0):
    """
    Allocate bandwidth proportionally based on weights.
    
    Args:
        total: Total bandwidth to allocate
        weights: List of weights for proportional allocation
        minimum: Minimum allocation for each weight
        
    Returns:
        List of allocations, one per weight
        
    Raises:
        ValueError: If total < 0, minimum < 0, weights is empty, or sum(weights) == 0
    """
    if total < 0:
        raise ValueError("Total bandwidth cannot be negative")
    
    if minimum < 0:
        raise ValueError("Minimum allocation cannot be negative")
    
    if not weights or sum(weights) == 0:
        raise ValueError("Weights must be non-empty and sum to non-zero")
    
    # Calculate proportional allocation
    weight_sum = sum(weights)
    allocations = []
    
    for weight in weights:
        # Calculate proportional share
        share = (weight / weight_sum) * total
        # Ensure minimum allocation
        allocation = max(minimum, share)
        allocations.append(allocation)
    
    # Adjust allocations to ensure total is exactly met
    actual_total = sum(allocations)
    if actual_total != total:
        # Distribute the difference proportionally
        diff = total - actual_total
        for i in range(len(allocations)):
            allocations[i] += diff * (weights[i] / weight_sum)
    
    # Convert to integers (assuming integer bandwidth units)
    return [int(round(x)) for x in allocations]


class TestBandwidthApportionProperties:
    """Test class for bandwidth_apportion semantic properties."""
    
    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_negative_total_rejection(self, total, weights, minimum):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="Total bandwidth cannot be negative"):
            bandwidth_apportion(total, weights, minimum)
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False)
    )
    def test_negative_minimum_rejection(self, total, weights, minimum):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="Minimum allocation cannot be negative"):
            bandwidth_apportion(total, weights, minimum)
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.one_of(
            st.lists(st.floats(min_value=0, max_value=0), min_size=1, max_size=10),  # All zeros
            st.just([])  # Empty list
        ),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_weights_rejection(self, total, weights, minimum):
        """Test that invalid weights (empty or sum to zero) raise ValueError."""
        with pytest.raises(ValueError, match="Weights must be non-empty and sum to non-zero"):
            bandwidth_apportion(total, weights, minimum)
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_output(self, total, weights, minimum):
        """Test that all output values are non-negative."""
        result = bandwidth_apportion(total, weights, minimum)
        assert all(x >= 0 for x in result), f"Found negative allocation: {result}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_allocation_guarantee(self, total, weights, minimum):
        """Test that all allocations meet the minimum requirement."""
        result = bandwidth_apportion(total, weights, minimum)
        assert all(x >= minimum for x in result), f"Found allocation below minimum: {result}, minimum: {minimum}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_integer_output(self, total, weights, minimum):
        """Test that all output values are integers."""
        result = bandwidth_apportion(total, weights, minimum)
        assert all(isinstance(x, int) for x in result), f"Found non-integer allocation: {result}"
    
    @given(
        total=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_allocation(self, total, weights, minimum):
        """Test that allocations approximate proportional distribution."""
        result = bandwidth_apportion(total, weights, minimum)
        
        # Calculate expected proportional allocation
        weight_sum = sum(weights)
        expected = [max(minimum, (w / weight_sum) * total) for w in weights]
        
        # Check that results are close to expected (within rounding error)
        for i, (actual, expected_val) in enumerate(zip(result, expected)):
            # Allow for rounding differences
            assert abs(actual - expected_val) <= 1, f"Allocation {i} too far from expected: {actual} vs {expected_val}"
    
    @given(
        total1=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        total2=st.floats(min_value=501, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_in_total(self, total1, total2, weights, minimum):
        """Test that increasing total increases allocations element-wise."""
        assume(total1 <= total2)
        
        result1 = bandwidth_apportion(total1, weights, minimum)
        result2 = bandwidth_apportion(total2, weights, minimum)
        
        # Each element in result2 should be >= corresponding element in result1
        for r1, r2 in zip(result1, result2):
            assert r2 >= r1, f"Monotonicity violated: {r2} < {r1}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum1=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        minimum2=st.floats(min_value=501, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_in_minimum(self, total, weights, minimum1, minimum2):
        """Test that increasing minimum increases allocations element-wise."""
        assume(minimum1 <= minimum2)
        
        result1 = bandwidth_apportion(total, weights, minimum1)
        result2 = bandwidth_apportion(total, weights, minimum2)
        
        # Each element in result2 should be >= corresponding element in result1
        for r1, r2 in zip(result1, result2):
            assert r2 >= r1, f"Monotonicity violated: {r2} < {r1}"
    
    @given(
        total=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        k=st.floats(min_value=0.1, max_value=10, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, total, weights, minimum, k):
        """Test that scaling inputs by k produces same relative results."""
        result1 = bandwidth_apportion(total, weights, minimum)
        result2 = bandwidth_apportion(k * total, [k * w for w in weights], k * minimum)
        
        # Results should be identical (since we convert to integers)
        assert result1 == result2, f"Scale invariance violated: {result1} != {result2}"
    
    @given(
        total=st.one_of(
            st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
            st.just(0)
        ),
        weights=st.one_of(
            st.lists(st.floats(min_value=0, max_value=0), min_size=1, max_size=10),
            st.just([])
        ),
        minimum=st.one_of(
            st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
            st.just(0)
        )
    )
    def test_error_conditions(self, total, weights, minimum):
        """Test that all error conditions raise ValueError."""
        # At least one of the conditions should trigger an error
        should_error = (total < 0) or (minimum < 0) or (not weights) or (sum(weights) == 0 if weights else True)
        
        if should_error:
            with pytest.raises(ValueError):
                bandwidth_apportion(total, weights, minimum)
        else:
            # If no error condition, should succeed
            result = bandwidth_apportion(total, weights, minimum)
            assert isinstance(result, list)
    
    # Additional edge case tests
    @example(total=0.0, weights=[1.0, 2.0], minimum=0.0)
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=5),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_edge_cases(self, total, weights, minimum):
        """Test additional edge cases."""
        # Test with zero total
        if total == 0:
            result = bandwidth_apportion(total, weights, minimum)
            # All allocations should be at least minimum
            assert all(x >= minimum for x in result)
        else:
            result = bandwidth_apportion(total, weights, minimum)
            # Basic sanity checks
            assert len(result) == len(weights)
            assert all(isinstance(x, int) for x in result)
            assert all(x >= 0 for x in result)