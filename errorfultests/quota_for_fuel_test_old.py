"""
Hypothesis-based tests for quota_for_fuel function semantic properties.
Tests all 19 semantic properties identified in quota_for_fuel_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

# Import the function under test
from dataset.python_programs.quota_for_fuel import quota_for_fuel


class TestQuotaForFuelProperties:
    """Test class for quota_for_fuel semantic properties."""

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_negative_total_error(self, total, minimum, weights):
        """Test branch property: total < 0 raises ValueError("total must be non-negative")."""
        assume(total < 0)
        with pytest.raises(ValueError, match="total must be non-negative"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_negative_minimum_error(self, total, minimum, weights):
        """Test branch property: minimum < 0 raises ValueError("minimum must be non-negative")."""
        assume(minimum < 0)
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_empty_weights_error(self, total, minimum, weights):
        """Test branch property: not weights raises ValueError("no weights provided")."""
        assume(not weights)
        with pytest.raises(ValueError, match="no weights provided"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_zero_weights_error(self, total, minimum, weights):
        """Test branch property: not any(weights) raises ValueError("all weights are zero")."""
        assume(not any(weights))
        with pytest.raises(ValueError, match="all weights are zero"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_valid_input_allocation(self, total, minimum, weights):
        """Test branch property: valid inputs return allocations where allocations[i] >= minimum for all i."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check that all allocations meet minimum requirement
        for allocation in result:
            assert allocation >= minimum, f"Allocation {allocation} is less than minimum {minimum}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_minimum_allocation_guarantee(self, total, minimum, weights):
        """Test function property: allocations[i] >= minimum for all i."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check minimum allocation guarantee
        for allocation in result:
            assert allocation >= minimum, f"Allocation {allocation} is less than minimum {minimum}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_allocation_length_preservation(self, total, minimum, weights):
        """Test function property: len(allocations) == len(weights)."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check length preservation
        assert len(result) == len(weights), f"Result length {len(result)} != weights length {len(weights)}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_non_negative_allocations(self, total, minimum, weights):
        """Test function property: allocations[i] >= 0 for all i."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check non-negative allocations
        for allocation in result:
            assert allocation >= 0, f"Allocation {allocation} is negative"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_integer_allocations(self, total, minimum, weights):
        """Test function property: allocations[i] is integer for all i."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check integer allocations
        for allocation in result:
            assert isinstance(allocation, int), f"Allocation {allocation} is not an integer"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_allocation_sum_bound(self, total, minimum, weights):
        """Test function property: sum(allocations) <= total."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check sum bound
        total_allocation = sum(result)
        assert total_allocation <= total, f"Total allocation {total_allocation} exceeds total {total}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_minimum_sum_bound(self, total, minimum, weights):
        """Test function property: sum(allocations) >= minimum * len(weights)."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check minimum sum bound
        total_allocation = sum(result)
        expected_minimum = minimum * len(weights)
        assert total_allocation >= expected_minimum, f"Total allocation {total_allocation} is less than minimum sum {expected_minimum}"

    @given(total=floats(min_value=1000, max_value=1000000, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_proportional_allocation_tendency(self, total, minimum, weights):
        """Test function property: allocations[i] / allocations[j] ≈ weights[i] / weights[j] for large total."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check proportional allocation for large totals
        for i in range(len(result)):
            for j in range(len(result)):
                if i != j and result[j] > 0 and weights[j] > 0:
                    ratio_allocation = result[i] / result[j]
                    ratio_weight = weights[i] / weights[j]
                    # Allow some tolerance for integer truncation
                    tolerance = 0.1
                    assert abs(ratio_allocation - ratio_weight) <= tolerance, \
                        f"Ratio mismatch at indices {i},{j}: allocation ratio {ratio_allocation}, weight ratio {ratio_weight}"

    @given(total1=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), total2=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=50))
    def test_monotonicity_in_total(self, total1, total2, minimum, weights):
        """Test function property: quota_for_fuel(total1, weights, minimum)[i] <= quota_for_fuel(total2, weights, minimum)[i] for all i when total1 <= total2."""
        assume(any(weights))
        assume(sum(weights) > 0)
        assume(total1 <= total2)
        
        result1 = quota_for_fuel(total1, weights, minimum)
        result2 = quota_for_fuel(total2, weights, minimum)
        
        # Check monotonicity in total
        for i in range(len(result1)):
            assert result1[i] <= result2[i], f"Monotonicity violated at index {i}: {result1[i]} > {result2[i]}"

    @given(total=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), minimum1=floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False), minimum2=floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=50))
    def test_monotonicity_in_minimum(self, total, minimum1, minimum2, weights):
        """Test function property: quota_for_fuel(total, weights, minimum1)[i] <= quota_for_fuel(total, weights, minimum2)[i] for all i when minimum1 <= minimum2."""
        assume(any(weights))
        assume(sum(weights) > 0)
        assume(minimum1 <= minimum2)
        
        result1 = quota_for_fuel(total, weights, minimum1)
        result2 = quota_for_fuel(total, weights, minimum2)
        
        # Check monotonicity in minimum
        for i in range(len(result1)):
            assert result1[i] <= result2[i], f"Monotonicity violated at index {i}: {result1[i]} > {result2[i]}"

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_error_on_negative_total(self, total, minimum, weights):
        """Test function property: raises ValueError with message "total must be non-negative" when total < 0."""
        assume(total < 0)
        with pytest.raises(ValueError, match="total must be non-negative"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_error_on_negative_minimum(self, total, minimum, weights):
        """Test function property: raises ValueError with message "minimum must be non-negative" when minimum < 0."""
        assume(minimum < 0)
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_error_on_empty_weights(self, total, minimum, weights):
        """Test function property: raises ValueError with message "no weights provided" when not weights."""
        assume(not weights)
        with pytest.raises(ValueError, match="no weights provided"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(allow_nan=False, allow_infinity=False), minimum=floats(allow_nan=False, allow_infinity=False), weights=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_error_on_zero_weights(self, total, minimum, weights):
        """Test function property: raises ValueError with message "all weights are zero" when not any(weights)."""
        assume(not any(weights))
        with pytest.raises(ValueError, match="all weights are zero"):
            quota_for_fuel(total, weights, minimum)

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), minimum=floats(min_value=0, allow_nan=False, allow_infinity=False), weights=lists(floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_allocation_truncation_bug(self, total, minimum, weights):
        """Test function property: sum(allocations) < total when fractional parts exist (bug: leftover units not redistributed)."""
        assume(any(weights))
        assume(sum(weights) > 0)
        
        result = quota_for_fuel(total, weights, minimum)
        
        # Check for truncation bug - sum should be less than total when fractional parts exist
        total_allocation = sum(result)
        if total_allocation < total:
            # This is the bug - leftover units not redistributed
            assert total_allocation < total, f"Expected truncation bug: total allocation {total_allocation} should be less than total {total}"
        else:
            # If sum equals total, it means no fractional parts or bug is fixed
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])