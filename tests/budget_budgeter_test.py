"""
Hypothesis-based property tests for budget_budgeter function.

This test suite exercises all semantic properties identified for the
budget_budgeter function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats

from dataset.python_programs.budget_budgeter import budget_budgeter


class TestBudgetBudgeterErrorConditions:
    """Test error conditions and exception handling."""

    @given(total=st.floats(max_value=-0.1))
    def test_negative_total_error(self, total):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            budget_budgeter(total, [1, 2, 3])

    @given(minimum=st.floats(max_value=-0.1))
    def test_negative_minimum_error(self, minimum):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            budget_budgeter(100, [1, 2, 3], minimum=minimum)

    def test_empty_weights_error(self):
        """Test that empty weights raises ValueError."""
        with pytest.raises(ValueError, match="no weights provided"):
            budget_budgeter(100, [])

    @given(total=st.floats(min_value=0, allow_infinity=False, allow_nan=False))
    def test_zero_weights_error(self, total):
        """Test that all-zero weights raises ValueError."""
        with pytest.raises(ValueError, match="all weights are zero"):
            budget_budgeter(total, [0, 0, 0])


class TestBudgetBudgeterProperties:
    """Test semantic properties of budget_budgeter function."""

    # Strategy for valid inputs
    valid_weights = st.lists(
        st.floats(min_value=0, max_value=1000, allow_infinity=False, allow_nan=False),
        min_size=1,
        max_size=10
    ).filter(lambda w: any(w))

    valid_total = st.floats(min_value=0, max_value=10000, allow_infinity=False, allow_nan=False)
    valid_minimum = st.floats(min_value=0, max_value=1000, allow_infinity=False, allow_nan=False)

    @given(total=valid_total, weights=valid_weights, minimum=valid_minimum)
    def test_non_negative_allocations(self, total, weights, minimum):
        """Test that all allocations are non-negative."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        assert all(a >= 0 for a in allocations), f"Found negative allocation in {allocations}"

    @given(total=valid_total, weights=valid_weights, minimum=valid_minimum)
    def test_minimum_allocation_guarantee(self, total, weights, minimum):
        """Test that all allocations meet the minimum requirement."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        assert all(a >= minimum for a in allocations), \
            f"Found allocation below minimum {minimum} in {allocations}"

    @given(total=valid_total, weights=valid_weights, minimum=valid_minimum)
    def test_allocation_length_preservation(self, total, weights, minimum):
        """Test that output length matches input weights length."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        assert len(allocations) == len(weights), \
            f"Length mismatch: {len(allocations)} != {len(weights)}"

    @given(total=valid_total, weights=valid_weights, minimum=valid_minimum)
    def test_budget_not_exceeded(self, total, weights, minimum):
        """Test that total allocations do not exceed the budget."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        total_allocated = sum(allocations)
        assert total_allocated <= total, \
            f"Budget exceeded: {total_allocated} > {total}"

    @given(
        total1=st.floats(min_value=0, max_value=10000, allow_infinity=False, allow_nan=False),
        total2=st.floats(min_value=0, max_value=10000, allow_infinity=False, allow_nan=False),
        weights=valid_weights,
        minimum=valid_minimum
    )
    def test_monotonicity_in_total(self, total1, total2, weights, minimum):
        """Test that increasing total increases allocations."""
        assume(total1 >= total2)
        
        allocations1 = budget_budgeter(total1, weights, minimum=minimum)
        allocations2 = budget_budgeter(total2, weights, minimum=minimum)
        
        assert all(a1 >= a2 for a1, a2 in zip(allocations1, allocations2)), \
            f"Monotonicity violated: {allocations1} not >= {allocations2}"

    @given(
        minimum1=st.floats(min_value=0, max_value=1000, allow_infinity=False, allow_nan=False),
        minimum2=st.floats(min_value=0, max_value=1000, allow_infinity=False, allow_nan=False),
        total=valid_total,
        weights=valid_weights
    )
    def test_monotonicity_in_minimum(self, minimum1, minimum2, total, weights):
        """Test that increasing minimum increases allocations."""
        assume(minimum1 >= minimum2)
        
        allocations1 = budget_budgeter(total, weights, minimum=minimum1)
        allocations2 = budget_budgeter(total, weights, minimum=minimum2)
        
        assert all(a1 >= a2 for a1, a2 in zip(allocations1, allocations2)), \
            f"Monotonicity violated: {allocations1} not >= {allocations2}"

    @given(
        total=valid_total,
        weights=valid_weights,
        minimum=valid_minimum,
        k=st.floats(min_value=0.1, max_value=100, allow_infinity=False, allow_nan=False)
    )
    def test_scale_invariance_weights(self, total, weights, minimum, k):
        """Test that scaling weights doesn't change allocations."""
        scaled_weights = [k * w for w in weights]
        
        allocations1 = budget_budgeter(total, weights, minimum=minimum)
        allocations2 = budget_budgeter(total, scaled_weights, minimum=minimum)
        
        assert allocations1 == allocations2, \
            f"Scale invariance violated: {allocations1} != {allocations2}"

    @given(
        total=valid_total,
        weights=valid_weights,
        minimum=valid_minimum,
        k=st.floats(min_value=0.1, max_value=100, allow_infinity=False, allow_nan=False)
    )
    def test_scale_invariance_total(self, total, weights, minimum, k):
        """Test that scaling total and minimum scales allocations."""
        scaled_total = k * total
        scaled_minimum = k * minimum
        
        allocations1 = budget_budgeter(total, weights, minimum=minimum)
        allocations2 = budget_budgeter(scaled_total, weights, minimum=scaled_minimum)
        
        expected_allocations = [k * a for a in allocations1]
        
        assert allocations2 == expected_allocations, \
            f"Scale invariance violated: {allocations2} != {expected_allocations}"

    @given(
        total=valid_total,
        minimum=valid_minimum,
        size=st.integers(min_value=1, max_value=10),
        weight_value=st.floats(min_value=0.1, max_value=1000, allow_infinity=False, allow_nan=False)
    )
    def test_identity_on_equal_weights(self, total, minimum, size, weight_value):
        """Test that equal weights result in equal allocations."""
        weights = [weight_value] * size
        
        allocations = budget_budgeter(total, weights, minimum=minimum)
        expected = [max(minimum, total // len(weights))] * len(weights)
        
        assert allocations == expected, \
            f"Identity property violated: {allocations} != {expected}"

    @given(
        minimum=valid_minimum,
        weights=valid_weights
    )
    def test_zero_total_gives_minimum(self, minimum, weights):
        """Test that zero total results in minimum allocations."""
        allocations = budget_budgeter(0, weights, minimum=minimum)
        expected = [minimum] * len(weights)
        
        assert allocations == expected, \
            f"Zero total property violated: {allocations} != {expected}"

    @given(total=valid_total, weights=valid_weights, minimum=valid_minimum)
    def test_integer_allocations(self, total, weights, minimum):
        """Test that all allocations are integers."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        assert all(isinstance(a, int) for a in allocations), \
            f"Found non-integer allocation in {allocations}"


class TestBudgetBudgeterEdgeCases:
    """Test edge cases and boundary conditions."""

    @given(
        total=st.floats(min_value=0, max_value=100, allow_infinity=False, allow_nan=False),
        weights=st.lists(
            st.floats(min_value=0.001, max_value=100, allow_infinity=False, allow_nan=False),
            min_size=1,
            max_size=5
        ),
        minimum=st.floats(min_value=0, max_value=10, allow_infinity=False, allow_nan=False)
    )
    def test_small_values(self, total, weights, minimum):
        """Test behavior with small values."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        
        # All properties should still hold
        assert all(a >= 0 for a in allocations)
        assert all(a >= minimum for a in allocations)
        assert len(allocations) == len(weights)
        assert sum(allocations) <= total
        assert all(isinstance(a, int) for a in allocations)

    @given(
        total=st.floats(min_value=1000, max_value=100000, allow_infinity=False, allow_nan=False),
        weights=st.lists(
            st.floats(min_value=1, max_value=10000, allow_infinity=False, allow_nan=False),
            min_size=5,
            max_size=20
        ),
        minimum=st.floats(min_value=0, max_value=100, allow_infinity=False, allow_nan=False)
    )
    def test_large_values(self, total, weights, minimum):
        """Test behavior with large values."""
        allocations = budget_budgeter(total, weights, minimum=minimum)
        
        # All properties should still hold
        assert all(a >= 0 for a in allocations)
        assert all(a >= minimum for a in allocations)
        assert len(allocations) == len(weights)
        assert sum(allocations) <= total
        assert all(isinstance(a, int) for a in allocations)

    def test_single_weight(self):
        """Test with single weight."""
        total = 100
        weights = [1]
        minimum = 10
        
        allocations = budget_budgeter(total, weights, minimum=minimum)
        
        assert len(allocations) == 1
        assert allocations[0] >= minimum
        assert allocations[0] <= total
        assert isinstance(allocations[0], int)

    def test_two_weights(self):
        """Test with two weights."""
        total = 100
        weights = [1, 2]
        minimum = 5
        
        allocations = budget_budgeter(total, weights, minimum=minimum)
        
        assert len(allocations) == 2
        assert all(a >= minimum for a in allocations)
        assert sum(allocations) <= total
        assert all(isinstance(a, int) for a in allocations)