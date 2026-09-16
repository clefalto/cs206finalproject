"""
Hypothesis-based property tests for tasks_allocator function.

This test suite exercises all semantic properties identified in
properties/tasks_allocator_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dataset.python_programs.tasks_allocator import tasks_allocator


class TestTasksAllocatorErrorConditions:
    """Test error conditions and exception raising."""
    
    @given(total=st.floats(max_value=-0.1))
    def test_negative_total_error(self, total):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            tasks_allocator(total, [1, 2, 3])
    
    @given(minimum=st.floats(max_value=-0.1))
    def test_negative_minimum_error(self, minimum):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            tasks_allocator(10, [1, 2, 3], minimum=minimum)
    
    def test_empty_weights_error(self):
        """Test that empty weights raises ValueError."""
        with pytest.raises(ValueError, match="no weights provided"):
            tasks_allocator(10, [])
    
    def test_zero_weights_error(self):
        """Test that all zero weights raises ValueError."""
        with pytest.raises(ValueError, match="all weights are zero"):
            tasks_allocator(10, [0, 0, 0])
    
    @given(weights=st.lists(st.floats(min_value=0, max_value=0), min_size=1))
    def test_all_zero_weights_error(self, weights):
        """Test that all zero weights raises ValueError for any length."""
        with pytest.raises(ValueError, match="all weights are zero"):
            tasks_allocator(10, weights)


class TestTasksAllocatorFunctionProperties:
    """Test function-level properties of tasks_allocator."""
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_non_negative_allocations(self, total, weights, minimum):
        """Test that all allocations are non-negative."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert all(a >= 0 for a in allocations), f"Found negative allocation: {allocations}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_minimum_allocation_guarantee(self, total, weights, minimum):
        """Test that all allocations meet the minimum requirement."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert all(a >= minimum for a in allocations), f"Found allocation below minimum {minimum}: {allocations}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_allocation_sum_bound(self, total, weights, minimum):
        """Test that sum of allocations does not exceed total."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert sum(allocations) <= total + 1e-9, f"Sum {sum(allocations)} exceeds total {total}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_allocation_sum_bound_with_minimum(self, total, weights, minimum):
        """Test that sum of allocations is at least minimum * len(weights)."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        expected_min_sum = minimum * len(weights)
        assert sum(allocations) >= expected_min_sum - 1e-9, f"Sum {sum(allocations)} below expected minimum {expected_min_sum}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=2),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_proportional_allocation(self, total, weights, minimum):
        """Test that allocations are approximately proportional to weights."""
        assume(any(weights))  # Ensure not all weights are zero
        assume(sum(w > 0 for w in weights) >= 2)  # Need at least 2 non-zero weights
        
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        # Find indices of non-zero weights
        non_zero_indices = [i for i, w in enumerate(weights) if w > 0]
        
        if len(non_zero_indices) >= 2:
            # Test proportionality for pairs of non-zero weights
            for i in range(len(non_zero_indices)):
                for j in range(i + 1, len(non_zero_indices)):
                    idx_i, idx_j = non_zero_indices[i], non_zero_indices[j]
                    weight_ratio = weights[idx_i] / weights[idx_j]
                    alloc_ratio = allocations[idx_i] / allocations[idx_j] if allocations[idx_j] > 0 else float('inf')
                    
                    # Allow for some tolerance due to integer truncation
                    tolerance = 0.1
                    assert abs(alloc_ratio - weight_ratio) <= tolerance, \
                        f"Proportionality violated: weight ratio {weight_ratio}, alloc ratio {alloc_ratio}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_integer_allocation(self, total, weights, minimum):
        """Test that all allocations are integers."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert all(isinstance(a, int) for a in allocations), f"Found non-integer allocation: {allocations}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_allocation_length(self, total, weights, minimum):
        """Test that allocations list has same length as weights."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert len(allocations) == len(weights), f"Length mismatch: allocations {len(allocations)}, weights {len(weights)}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=2),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_monotonic_allocation(self, total, weights, minimum):
        """Test that higher weights get higher or equal allocations."""
        assume(any(weights))  # Ensure not all weights are zero
        
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        # Check monotonicity: if weights[i] >= weights[j], then allocations[i] >= allocations[j]
        for i in range(len(weights)):
            for j in range(len(weights)):
                if weights[i] >= weights[j]:
                    assert allocations[i] >= allocations[j], \
                        f"Monotonicity violated: weight {weights[i]} >= {weights[j]} but allocation {allocations[i]} < {allocations[j]}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        k=st.floats(min_value=0.1, max_value=100)
    )
    def test_scale_invariance(self, total, weights, k):
        """Test that scaling weights by positive k doesn't change allocations."""
        assume(any(weights))  # Ensure not all weights are zero
        assume(k > 0)  # Ensure k is positive
        
        allocations1 = tasks_allocator(total, weights)
        scaled_weights = [w * k for w in weights]
        allocations2 = tasks_allocator(total, scaled_weights)
        
        assert allocations1 == allocations2, f"Scale invariance violated: {allocations1} != {allocations2}"
    
    @given(
        total1=st.floats(min_value=0, max_value=1000),
        total2=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_total_independence(self, total1, total2, weights, minimum):
        """Test that allocations are the same when totals are above minimum threshold."""
        assume(any(weights))  # Ensure not all weights are zero
        
        min_required = minimum * len(weights)
        
        # Only test when both totals are above the minimum required
        if total1 >= min_required and total2 >= min_required:
            allocations1 = tasks_allocator(total1, weights, minimum=minimum)
            allocations2 = tasks_allocator(total2, weights, minimum=minimum)
            
            assert allocations1 == allocations2, f"Total independence violated: {allocations1} != {allocations2}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum1=st.floats(min_value=0, max_value=10),
        minimum2=st.floats(min_value=0, max_value=10)
    )
    def test_minimum_independence(self, total, weights, minimum1, minimum2):
        """Test that allocations are the same when minimums are below planned values."""
        assume(any(weights))  # Ensure not all weights are zero
        
        # Calculate planned allocations to determine if minimums are below planned
        total_weight = sum(weights)
        planned = [max(0, (w / total_weight) * total) for w in weights]
        min_planned = min(planned)
        
        # Only test when both minimums are below the minimum planned allocation
        if minimum1 <= min_planned and minimum2 <= min_planned:
            allocations1 = tasks_allocator(total, weights, minimum=minimum1)
            allocations2 = tasks_allocator(total, weights, minimum=minimum2)
            
            assert allocations1 == allocations2, f"Minimum independence violated: {allocations1} != {allocations2}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_zero_weight_handling(self, total, weights, minimum):
        """Test that zero weights get minimum allocation."""
        assume(any(weights))  # Ensure not all weights are zero
        
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        for i, weight in enumerate(weights):
            if weight == 0:
                assert allocations[i] == minimum, f"Zero weight {i} should get minimum {minimum}, got {allocations[i]}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_single_weight_handling(self, total, minimum):
        """Test that single weight gets all the allocation."""
        weights = [1.0]  # Single weight
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        assert len(allocations) == 1, f"Expected single allocation, got {len(allocations)}"
        assert allocations[0] == total, f"Single weight should get total {total}, got {allocations[0]}"
    
    def test_error_conditions_comprehensive(self):
        """Test all error conditions comprehensively."""
        # Test negative total
        with pytest.raises(ValueError, match="total must be non-negative"):
            tasks_allocator(-1, [1, 2, 3])
        
        # Test negative minimum
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            tasks_allocator(10, [1, 2, 3], minimum=-1)
        
        # Test empty weights
        with pytest.raises(ValueError, match="no weights provided"):
            tasks_allocator(10, [])
        
        # Test all zero weights
        with pytest.raises(ValueError, match="all weights are zero"):
            tasks_allocator(10, [0, 0, 0])


class TestTasksAllocatorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1, max_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_single_element_weights(self, total, weights, minimum):
        """Test with single element weights list."""
        assume(any(weights))  # Ensure not all weights are zero
        allocations = tasks_allocator(total, weights, minimum=minimum)
        assert len(allocations) == 1
        assert allocations[0] == total
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=2),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_mixed_zero_nonzero_weights(self, total, weights, minimum):
        """Test with mix of zero and non-zero weights."""
        assume(any(weights))  # Ensure not all weights are zero
        assume(sum(w > 0 for w in weights) >= 1)  # Ensure at least one non-zero weight
        
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        # Check that zero weights get minimum allocation
        for i, weight in enumerate(weights):
            if weight == 0:
                assert allocations[i] == minimum, f"Zero weight {i} should get minimum {minimum}, got {allocations[i]}"
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_minimum_exceeds_total(self, total, weights, minimum):
        """Test behavior when minimum exceeds what would be allocated."""
        assume(any(weights))  # Ensure not all weights are zero
        assume(minimum * len(weights) <= total)  # Ensure minimum is feasible
        
        allocations = tasks_allocator(total, weights, minimum=minimum)
        
        # All allocations should be at least minimum
        assert all(a >= minimum for a in allocations)
        
        # Sum should be at least minimum * len(weights)
        assert sum(allocations) >= minimum * len(weights) - 1e-9


class TestTasksAllocatorDeterminism:
    """Test that the function is deterministic."""
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=100), min_size=1),
        minimum=st.floats(min_value=0, max_value=10)
    )
    def test_deterministic_output(self, total, weights, minimum):
        """Test that the function produces the same output for same inputs."""
        assume(any(weights))  # Ensure not all weights are zero
        
        # Call the function twice with same inputs
        allocations1 = tasks_allocator(total, weights, minimum=minimum)
        allocations2 = tasks_allocator(total, weights, minimum=minimum)
        
        assert allocations1 == allocations2, f"Function is not deterministic: {allocations1} != {allocations2}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])