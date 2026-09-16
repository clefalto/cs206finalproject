"""
Hypothesis-based tests for quota_for_memory function semantic properties.

This test file exercises all 18 semantic properties identified in 
quota_for_memory_properties.json using the Hypothesis testing framework
to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of
import math

# Import the function under test
# Note: The actual implementation should be imported here
# from your_module import quota_for_memory

# Mock implementation for testing purposes
def quota_for_memory(total, weights, minimum=0):
    """
    Mock implementation of quota_for_memory for testing.
    This should be replaced with the actual implementation.
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    if minimum < 0:
        raise ValueError("minimum must be non-negative")
    if not weights:
        raise ValueError("no weights provided")
    if not any(weights):
        raise ValueError("all weights are zero")
    
    total_weight = sum(weights)
    allocations = []
    for weight in weights:
        planned = (weight / total_weight) * total
        allocation = max(minimum, int(planned))
        allocations.append(allocation)
    
    return allocations


class TestQuotaForMemoryProperties:
    """Test class for quota_for_memory semantic properties."""

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_negative_total_error(self, total, weights):
        """Test negative_total_error property: quota_for_memory(negative_total, weights) raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            quota_for_memory(total, weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False)
    )
    def test_negative_minimum_error(self, total, weights, minimum):
        """Test negative_minimum_error property: quota_for_memory(total, weights, minimum=negative_minimum) raises ValueError."""
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            quota_for_memory(total, weights, minimum=minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_weights_error(self, total):
        """Test empty_weights_error property: quota_for_memory(total, []) raises ValueError."""
        with pytest.raises(ValueError, match="no weights provided"):
            quota_for_memory(total, [])

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        zero_count=st.integers(min_value=1, max_value=10)
    )
    def test_zero_weights_error(self, total, zero_count):
        """Test zero_weights_error property: quota_for_memory(total, [0, 0, 0]) raises ValueError."""
        weights = [0.0] * zero_count
        with pytest.raises(ValueError, match="all weights are zero"):
            quota_for_memory(total, weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_allocations(self, total, weights, minimum):
        """Test non_negative_allocations property: all allocations are non-negative."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        assert all(allocation >= 0 for allocation in allocations), f"Found negative allocation in {allocations}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_allocations_length(self, total, weights, minimum):
        """Test allocations_length property: output length equals input weights length."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        assert len(allocations) == len(weights), f"Length mismatch: {len(allocations)} != {len(weights)}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_allocation_guarantee(self, total, weights, minimum):
        """Test minimum_allocation_guarantee property: all allocations meet minimum requirement."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        assert all(allocation >= minimum for allocation in allocations), f"Minimum guarantee violated in {allocations}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_sum_allocation_bound(self, total, weights, minimum):
        """Test sum_allocation_bound property: sum of allocations <= total."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        total_weight = sum(weights)
        expected_minimum_total = minimum * len(weights)
        
        # The sum should be <= total, but at least the minimum total
        assert sum(allocations) <= total, f"Sum {sum(allocations)} exceeds total {total}"
        assert sum(allocations) >= expected_minimum_total, f"Sum {sum(allocations)} below minimum expected {expected_minimum_total}"

    @given(
        total=st.floats(min_value=100, max_value=10000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_distribution(self, total, weights, minimum):
        """Test proportional_distribution property: allocations maintain weight proportions for large totals."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        total_weight = sum(weights)
        
        # For large totals, the distribution should be approximately proportional
        # Allow some tolerance due to integer truncation
        for i in range(len(weights)):
            for j in range(len(weights)):
                if i != j and weights[i] > 0 and weights[j] > 0:
                    expected_ratio = weights[i] / weights[j]
                    actual_ratio = allocations[i] / allocations[j] if allocations[j] > 0 else float('inf')
                    
                    # Allow 20% tolerance for truncation effects
                    tolerance = 0.2
                    assert abs(actual_ratio - expected_ratio) / expected_ratio <= tolerance, \
                        f"Proportion mismatch: {actual_ratio} vs {expected_ratio} for weights {weights[i]} vs {weights[j]}"

    @given(
        total1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        total2=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_total(self, total1, total2, weights, minimum):
        """Test monotonic_total property: increasing total increases allocations."""
        assume(total1 >= total2)
        
        allocations1 = quota_for_memory(total1, weights, minimum=minimum)
        allocations2 = quota_for_memory(total2, weights, minimum=minimum)
        
        for a1, a2 in zip(allocations1, allocations2):
            assert a1 >= a2, f"Monotonicity violated: {a1} < {a2}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum1=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        minimum2=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_minimum(self, total, weights, minimum1, minimum2):
        """Test monotonic_minimum property: increasing minimum increases allocations."""
        assume(minimum1 >= minimum2)
        
        allocations1 = quota_for_memory(total, weights, minimum=minimum1)
        allocations2 = quota_for_memory(total, weights, minimum=minimum2)
        
        for a1, a2 in zip(allocations1, allocations2):
            assert a1 >= a2, f"Monotonicity violated: {a1} < {a2}"

    @given(
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_zero_total_minimum(self, minimum, weights):
        """Test zero_total_minimum property: quota_for_memory(0, weights, minimum=minimum) == [minimum] * len(weights)."""
        allocations = quota_for_memory(0, weights, minimum=minimum)
        expected = [int(minimum)] * len(weights)
        assert allocations == expected, f"Expected {expected}, got {allocations}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_single_weight_total(self, total, minimum):
        """Test single_weight_total property: quota_for_memory(total, [1], minimum=minimum) == [max(minimum, total)]."""
        weights = [1.0]
        allocations = quota_for_memory(total, weights, minimum=minimum)
        expected = [max(int(minimum), int(total))]
        assert allocations == expected, f"Expected {expected}, got {allocations}"

    def test_error_conditions(self):
        """Test error_conditions property: quota_for_memory raises ValueError for invalid inputs."""
        # Test negative total
        with pytest.raises(ValueError, match="total must be non-negative"):
            quota_for_memory(-1, [1, 2, 3])
        
        # Test negative minimum
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            quota_for_memory(10, [1, 2, 3], minimum=-1)
        
        # Test empty weights
        with pytest.raises(ValueError, match="no weights provided"):
            quota_for_memory(10, [])
        
        # Test all zero weights
        with pytest.raises(ValueError, match="all weights are zero"):
            quota_for_memory(10, [0, 0, 0])

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_allocation_sum_less_than_total(self, total, weights, minimum):
        """Test allocation_sum_less_than_total property: sum of allocations <= total."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        assert sum(allocations) <= total, f"Sum {sum(allocations)} exceeds total {total}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_integer_allocation(self, total, weights, minimum):
        """Test integer_allocation property: all allocations are integers."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        assert all(isinstance(allocation, int) for allocation in allocations), \
            f"Non-integer allocations found: {allocations}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_floor_property(self, total, weights, minimum):
        """Test minimum_floor property: allocation[i] = max(minimum, (weights[i] / total_weight) * total)."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        total_weight = sum(weights)
        
        for i, weight in enumerate(weights):
            planned = (weight / total_weight) * total
            expected = max(minimum, int(planned))
            assert allocations[i] == expected, \
                f"Minimum floor violation at index {i}: got {allocations[i]}, expected {expected}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_truncation_bug_property(self, total, weights, minimum):
        """Test truncation_bug property: allocation[i] = int(planned[i]) loses fractional remainder."""
        allocations = quota_for_memory(total, weights, minimum=minimum)
        total_weight = sum(weights)
        
        for i, weight in enumerate(weights):
            planned = (weight / total_weight) * total
            truncated = int(planned)
            expected = max(minimum, truncated)
            
            # Verify that truncation occurred (unless minimum is higher)
            if planned >= minimum:
                assert allocations[i] == truncated, \
                    f"Expected truncation of {planned} to {truncated}, got {allocations[i]}"
            else:
                assert allocations[i] == int(minimum), \
                    f"Expected minimum {minimum}, got {allocations[i]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])