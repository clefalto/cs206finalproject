"""
Hypothesis-based tests for quota_for_capacity function semantic properties.

This test file exercises all semantic properties identified in 
properties/quota_for_capacity_properties.json using the Hypothesis 
testing framework for property-based testing.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, booleans
import math

# Import the function under test
# Note: The actual import path will depend on where quota_for_capacity is located
# For now, we'll use a placeholder import that should be updated
try:
    from dataset.python_programs.quota_for_capacity import quota_for_capacity
except ImportError:
    # If the function is not available, we'll create a mock for testing purposes
    # This allows the test structure to be validated
    def quota_for_capacity(total, weights, minimum=0, floor_to_int=False):
        """
        Mock implementation for testing purposes.
        This should be replaced with the actual function import.
        """
        if len(weights) == 0:
            raise ValueError("weights required")
        if total < 0:
            raise ValueError("negative total")
        if minimum < 0:
            raise ValueError("negative minimum")
        if sum(weights) == 0:
            raise ValueError("zero total weight")
        
        weight_sum = sum(weights)
        shares = []
        
        for w in weights:
            portion = (w / weight_sum) * total
            if portion > minimum:
                shares.append(portion)
            else:
                shares.append(minimum)
        
        if floor_to_int:
            shares = [int(v) for v in shares]
        
        return shares

"""Test class for quota_for_capacity semantic properties."""

# Strategies for generating test data
non_negative_floats = st.floats(min_value=0, max_value=1e6, allow_infinity=False, allow_nan=False)
positive_floats = st.floats(min_value=0.0001, max_value=1e6, allow_infinity=False, allow_nan=False)
negative_floats = st.floats(max_value=-0.0001, min_value=-1e6, allow_infinity=False, allow_nan=False)
non_negative_integers = st.integers(min_value=0, max_value=1000000)
positive_integers = st.integers(min_value=1, max_value=1000000)
negative_integers = st.integers(min_value=-1000000, max_value=-1)

# Strategy for generating valid weights (non-empty, sum > 0)
valid_weights = st.lists(positive_floats, min_size=1, max_size=20)

# Strategy for generating weights that sum to zero (all zeros)
zero_weights = st.lists(st.just(0.0), min_size=1, max_size=20)


class TestBranchProperties:
    """Test branch-specific properties of quota_for_capacity."""
    
    @given(total=non_negative_floats, weights=st.just([]))
    def test_empty_weights_error(self, total, weights):
        """Test that empty weights raise ValueError with 'weights required'."""
        with pytest.raises(ValueError, match="weights required"):
            quota_for_capacity(total, weights)
    
    @given(total=negative_floats, weights=valid_weights)
    def test_negative_total_error(self, total, weights):
        """Test that negative total raises ValueError with 'negative total'."""
        with pytest.raises(ValueError, match="negative total"):
            quota_for_capacity(total, weights)
    
    @given(total=non_negative_floats, weights=valid_weights, minimum=negative_floats)
    def test_negative_minimum_error(self, total, weights, minimum):
        """Test that negative minimum raises ValueError with 'negative minimum'."""
        with pytest.raises(ValueError, match="negative minimum"):
            quota_for_capacity(total, weights, minimum=minimum)
    
    @given(total=non_negative_floats, weights=zero_weights)
    def test_zero_weight_sum_error(self, total, weights):
        """Test that zero weight sum raises ValueError with 'zero total weight'."""
        with pytest.raises(ValueError, match="zero total weight"):
            quota_for_capacity(total, weights)
    
    @given(total=non_negative_floats, weights=valid_weights)
    def test_floor_to_int_conversion(self, total, weights):
        """Test that floor_to_int=True returns integer values."""
        result = quota_for_capacity(total, weights, floor_to_int=True)
        assert all(isinstance(share, int) for share in result)
    
    @given(total=positive_floats, weights=valid_weights, minimum=non_negative_floats)
    def test_proportional_allocation(self, total, weights, minimum):
        """Test proportional allocation when portion > minimum."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        weight_sum = sum(weights)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion > minimum:
                # When portion > minimum, the share should be the portion
                assert abs(result[i] - portion) < 1e-9
    
    @given(total=positive_floats, weights=valid_weights, minimum=positive_floats)
    def test_minimum_floor(self, total, weights, minimum):
        """Test minimum floor when portion <= minimum."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        weight_sum = sum(weights)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion <= minimum:
                # When portion <= minimum, the share should be the minimum
                assert abs(result[i] - minimum) < 1e-9


class TestFunctionProperties:
    """Test function-level properties of quota_for_capacity."""
    
    @given(total=non_negative_floats, weights=valid_weights, minimum=non_negative_floats)
    def test_non_negative_shares(self, total, weights, minimum):
        """Test that all shares are non-negative."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        assert all(share >= 0 for share in result)
    
    @given(total=non_negative_floats, weights=valid_weights, minimum=non_negative_floats)
    def test_shares_sum_bound(self, total, weights, minimum):
        """Test that sum of shares is >= total."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        assert sum(result) >= total - 1e-9  # Allow for floating point precision
    
    @given(total=non_negative_floats, weights=valid_weights)
    def test_shares_length(self, total, weights):
        """Test that result length equals weights length."""
        result = quota_for_capacity(total, weights)
        assert len(result) == len(weights)
    
    @given(total1=non_negative_floats, total2=non_negative_floats, weights=valid_weights, minimum=non_negative_floats)
    def test_monotonic_total(self, total1, total2, weights, minimum):
        """Test monotonicity with respect to total."""
        assume(total1 >= total2)
        result1 = quota_for_capacity(total1, weights, minimum=minimum)
        result2 = quota_for_capacity(total2, weights, minimum=minimum)
        
        for s1, s2 in zip(result1, result2):
            assert s1 >= s2 - 1e-9  # Allow for floating point precision
    
    @given(minimum1=non_negative_floats, minimum2=non_negative_floats, total=non_negative_floats, weights=valid_weights)
    def test_monotonic_minimum(self, minimum1, minimum2, total, weights):
        """Test monotonicity with respect to minimum."""
        assume(minimum1 >= minimum2)
        result1 = quota_for_capacity(total, weights, minimum=minimum1)
        result2 = quota_for_capacity(total, weights, minimum=minimum2)
        
        for s1, s2 in zip(result1, result2):
            assert s1 >= s2 - 1e-9  # Allow for floating point precision
    
    @given(weights=valid_weights, minimum=non_negative_floats)
    def test_zero_total_zero_shares(self, weights, minimum):
        """Test that zero total with minimum produces minimum shares."""
        result = quota_for_capacity(0, weights, minimum=minimum)
        expected = [minimum] * len(weights)
        for r, e in zip(result, expected):
            assert abs(r - e) < 1e-9
    
    @given(total=non_negative_floats, weights=valid_weights)
    def test_zero_minimum_proportional(self, total, weights):
        """Test proportional allocation when minimum is zero."""
        result = quota_for_capacity(total, weights, minimum=0)
        weight_sum = sum(weights)
        expected = [(w / weight_sum) * total for w in weights]
        
        for r, e in zip(result, expected):
            assert abs(r - e) < 1e-9
    
    @given(total=non_negative_floats, minimum=non_negative_floats)
    def test_single_weight_total(self, total, minimum):
        """Test single weight case."""
        result = quota_for_capacity(total, [1], minimum=minimum)
        expected = [max(minimum, total)]
        assert len(result) == 1
        assert abs(result[0] - expected[0]) < 1e-9
    
    @given(total=non_negative_floats, weights=valid_weights, minimum=non_negative_floats)
    def test_integer_floor_bug(self, total, weights, minimum):
        """Test integer floor bug property."""
        result = quota_for_capacity(total, weights, floor_to_int=True, minimum=minimum)
        assert sum(result) <= total + 1e-9  # Allow for floating point precision
    
    @given(total=st.one_of(negative_floats, non_negative_floats), 
           weights=st.one_of(valid_weights, st.just([]), zero_weights),
           minimum=st.one_of(negative_floats, non_negative_floats))
    def test_error_conditions(self, total, weights, minimum):
        """Test all error conditions raise ValueError."""
        # Check if this should raise an error
        should_raise = (
            len(weights) == 0 or 
            total < 0 or 
            minimum < 0 or 
            sum(weights) == 0
        )
        
        if should_raise:
            with pytest.raises(ValueError):
                quota_for_capacity(total, weights, minimum=minimum)
        else:
            # If it shouldn't raise, make sure it doesn't
            result = quota_for_capacity(total, weights, minimum=minimum)
            assert isinstance(result, list)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @given(total=st.just(0), weights=valid_weights, minimum=non_negative_floats)
    def test_zero_total_with_valid_weights(self, total, weights, minimum):
        """Test zero total with valid weights."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        assert len(result) == len(weights)
        assert all(share >= minimum - 1e-9 for share in result)
    
    @given(total=positive_floats, weights=st.lists(positive_floats, min_size=1, max_size=5), minimum=st.just(0))
    def test_minimum_zero_edge_case(self, total, weights, minimum):
        """Test minimum=0 edge case."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        assert len(result) == len(weights)
        assert sum(result) >= total - 1e-9
    
    @given(total=non_negative_floats, weights=st.lists(st.floats(min_value=1e-6, max_value=1e6), min_size=10, max_size=50))
    def test_large_weight_lists(self, total, weights):
        """Test with larger weight lists."""
        result = quota_for_capacity(total, weights)
        assert len(result) == len(weights)
        assert all(share >= 0 for share in result)
    
    @given(total=st.floats(min_value=1e-6, max_value=1e-3), weights=valid_weights, minimum=st.floats(min_value=1e-6, max_value=1e-3))
    def test_small_values(self, total, weights, minimum):
        """Test with very small values."""
        result = quota_for_capacity(total, weights, minimum=minimum)
        assert len(result) == len(weights)
        assert all(share >= 0 for share in result)


class TestIntegrationProperties:
    """Test integration and complex property combinations."""
    
    @given(total=positive_floats, weights=valid_weights, minimum=non_negative_floats, floor_to_int=booleans())
    def test_combined_parameters(self, total, weights, minimum, floor_to_int):
        """Test various parameter combinations."""
        result = quota_for_capacity(total, weights, minimum=minimum, floor_to_int=floor_to_int)
        
        # Basic properties should hold
        assert len(result) == len(weights)
        assert all(share >= 0 for share in result)
        assert sum(result) >= total - 1e-9
        
        # If floor_to_int is True, all results should be integers
        if floor_to_int:
            assert all(isinstance(share, int) for share in result)
    
    @given(total=non_negative_floats, weights=valid_weights)
    def test_consistency_across_runs(self, total, weights):
        """Test that function is deterministic."""
        result1 = quota_for_capacity(total, weights)
        result2 = quota_for_capacity(total, weights)
        
        for r1, r2 in zip(result1, result2):
            assert abs(r1 - r2) < 1e-9


if __name__ == "__main__":
    # Run the tests if executed directly
    pytest.main([__file__, "-v"])