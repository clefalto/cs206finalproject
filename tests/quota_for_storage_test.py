import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math

# Import the function under test
from dataset.python_programs.quota_for_storage import quota_for_storage


class TestQuotaForStorage:
    """Test suite for quota_for_storage function using Hypothesis."""

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_negative_total_error(self, total, weights):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            quota_for_storage(total, weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        minimum=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_negative_minimum_error(self, total, minimum, weights):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            quota_for_storage(total, weights, minimum=minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=0)
    )
    def test_empty_weights_error(self, total, weights):
        """Test that empty weights raises ValueError."""
        with pytest.raises(ValueError, match="no weights provided"):
            quota_for_storage(total, weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.just(0.0), min_size=1, max_size=10)
    )
    def test_zero_weights_error(self, total, weights):
        """Test that all zero weights raises ValueError."""
        with pytest.raises(ValueError, match="all weights are zero"):
            quota_for_storage(total, weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_allocations(self, total, weights, minimum):
        """Test that all allocations are non-negative."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        assert all(allocation >= 0 for allocation in allocations)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_allocation_length(self, total, weights, minimum):
        """Test that allocation length matches weights length."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        assert len(allocations) == len(weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_allocation_bound(self, total, weights, minimum):
        """Test that all allocations are at least minimum."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        assert all(allocation >= int(minimum) for allocation in allocations)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_allocation_sum_bound(self, total, weights, minimum):
        """Test that sum of allocations does not exceed total."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        assert sum(allocations) <= total

    @given(
        total1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        total2=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_total(self, total1, total2, weights, minimum):
        """Test that allocations are monotonic with respect to total."""
        assume(any(weights))
        assume(total1 >= total2)
        allocations1 = quota_for_storage(total1, weights, minimum=minimum)
        allocations2 = quota_for_storage(total2, weights, minimum=minimum)
        assert all(a1 >= a2 for a1, a2 in zip(allocations1, allocations2))

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum1=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        minimum2=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_minimum(self, total, weights, minimum1, minimum2):
        """Test that allocations are monotonic with respect to minimum."""
        assume(any(weights))
        assume(minimum1 >= minimum2)
        allocations1 = quota_for_storage(total, weights, minimum=minimum1)
        allocations2 = quota_for_storage(total, weights, minimum=minimum2)
        assert all(a1 >= a2 for a1, a2 in zip(allocations1, allocations2))

    @given(
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_zero_total_minimum(self, weights, minimum):
        """Test that zero total with minimum returns minimum allocations."""
        assume(any(weights))
        allocations = quota_for_storage(0, weights, minimum=minimum)
        expected = [int(minimum)] * len(weights)
        assert allocations == expected

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_truncation_loss(self, total, weights, minimum):
        """Test that truncation can cause loss of total units."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        # When fractional parts exist, sum should be less than total
        # This is a known limitation of the implementation
        if any(isinstance(planned, float) and not planned.is_integer() 
               for planned in [max(minimum, (w / sum(weights)) * total) for w in weights]):
            assert sum(allocations) < total

    @given(
        total=st.floats(min_value=100, max_value=10000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=5),
        minimum=st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_when_sufficient(self, total, weights, minimum):
        """Test that allocations approximate proportional distribution when total is large."""
        assume(any(weights))
        assume(total >= sum(minimum for _ in weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        
        # Calculate expected proportional allocation
        total_weight = sum(weights)
        expected = [max(minimum, (w / total_weight) * total) for w in weights]
        
        # Check that allocations are close to expected (within 1 unit due to truncation)
        for i, (alloc, exp) in enumerate(zip(allocations, expected)):
            assert abs(alloc - int(exp)) <= 1, f"Allocation {i} too far from expected"

    @given(
        total=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_error_conditions(self, total, weights, minimum):
        """Test that all error conditions raise ValueError."""
        if total < 0 or minimum < 0 or not weights or not any(weights):
            with pytest.raises(ValueError):
                quota_for_storage(total, weights, minimum=minimum)
        else:
            # If no error condition, should not raise
            try:
                quota_for_storage(total, weights, minimum=minimum)
            except ValueError:
                pytest.fail("Unexpected ValueError raised for valid inputs")

    @example(total=10.5, weights=[1.0, 2.0, 3.0], minimum=1.0)
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_allocation_branch(self, total, weights, minimum):
        """Test the proportional allocation branch (planned[i] >= minimum)."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        total_weight = sum(weights)
        planned = [max(minimum, (w / total_weight) * total) for w in weights]
        
        for i, (alloc, plan) in enumerate(zip(allocations, planned)):
            if plan >= minimum:
                assert alloc == int(plan), f"Index {i}: expected int({plan}), got {alloc}"

    @example(total=5.0, weights=[1.0, 1.0, 1.0], minimum=2.0)
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_floor_branch(self, total, weights, minimum):
        """Test the minimum floor branch (planned[i] < minimum)."""
        assume(any(weights))
        allocations = quota_for_storage(total, weights, minimum=minimum)
        total_weight = sum(weights)
        planned = [max(minimum, (w / total_weight) * total) for w in weights]
        
        for i, (alloc, plan) in enumerate(zip(allocations, planned)):
            if plan < minimum:
                assert alloc == int(minimum), f"Index {i}: expected {int(minimum)}, got {alloc}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])