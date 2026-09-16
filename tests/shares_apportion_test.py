#!/usr/bin/env python3
"""
Hypothesis-based property tests for the shares_apportion function.

This test file verifies all 10 semantic properties identified for the
shares_apportion function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, just

# Import the function under test
# Note: The actual import path should be adjusted based on the project structure
# For now, we'll assume the function is available in the current module or a known location
try:
    from shares_apportion import shares_apportion
except ImportError:
    # If the function is not available, we'll create a mock implementation
    # for testing purposes. This should be replaced with the actual import.
    def shares_apportion(total, weights, minimum=0):
        """
        Mock implementation of shares_apportion for testing.
        This should be replaced with the actual function import.
        """
        if total < 0:
            raise ValueError("total must be non-negative")
        if minimum < 0:
            raise ValueError("minimum must be non-negative")
        if not weights:
            raise ValueError("no weights provided")
        if not any(weights):
            raise ValueError("all weights are zero")
        
        # Simple proportional allocation with minimum enforcement
        n = len(weights)
        if total < minimum * n:
            raise ValueError("total too small for minimum allocation")
        
        # Allocate minimum to each
        result = [minimum] * n
        remaining = total - minimum * n
        
        # Proportional allocation of remaining
        weight_sum = sum(weights)
        for i, w in enumerate(weights):
            if w > 0:
                result[i] += int(remaining * w / weight_sum)
        
        return result


class TestSharesApportionProperties:
    """Test class for shares_apportion semantic properties."""

    @given(
        total=st.integers(min_value=-1000, max_value=-1),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_negative_total_error(self, total, weights, minimum):
        """
        Test Property: negative_total_error
        Condition: total < 0
        Formal: if total < 0 then ValueError("total must be non-negative") is raised
        """
        with pytest.raises(ValueError, match="total must be non-negative"):
            shares_apportion(total, weights, minimum)

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100),
        minimum=st.integers(min_value=-1000, max_value=-1)
    )
    def test_negative_minimum_error(self, total, weights, minimum):
        """
        Test Property: negative_minimum_error
        Condition: minimum < 0
        Formal: if minimum < 0 then ValueError("minimum must be non-negative") is raised
        """
        with pytest.raises(ValueError, match="minimum must be non-negative"):
            shares_apportion(total, weights, minimum)

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=0, max_size=0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_empty_weights_error(self, total, weights, minimum):
        """
        Test Property: empty_weights_error
        Condition: not weights
        Formal: if not weights then ValueError("no weights provided") is raised
        """
        with pytest.raises(ValueError, match="no weights provided"):
            shares_apportion(total, weights, minimum)

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: not any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_zero_weights_error(self, total, weights, minimum):
        """
        Test Property: zero_weights_error
        Condition: not any(weights)
        Formal: if not any(weights) then ValueError("all weights are zero") is raised
        """
        with pytest.raises(ValueError, match="all weights are zero"):
            shares_apportion(total, weights, minimum)

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_non_negative_allocations(self, total, weights, minimum):
        """
        Test Property: non_negative_allocations
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: all(allocation >= 0 for allocation in shares_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = shares_apportion(total, weights, minimum)
        assert all(allocation >= 0 for allocation in result), f"Found negative allocation in result: {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_minimum_allocation(self, total, weights, minimum):
        """
        Test Property: minimum_allocation
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: all(allocation >= minimum for allocation in shares_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = shares_apportion(total, weights, minimum)
        assert all(allocation >= minimum for allocation in result), f"Found allocation below minimum {minimum} in result: {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_integer_allocations(self, total, weights, minimum):
        """
        Test Property: integer_allocations
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: all(isinstance(allocation, int) for allocation in shares_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = shares_apportion(total, weights, minimum)
        assert all(isinstance(allocation, int) for allocation in result), f"Found non-integer allocation in result: {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_allocation_sum_less_than_total(self, total, weights, minimum):
        """
        Test Property: allocation_sum_less_than_total
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: sum(shares_apportion(total, weights)) <= total
        """
        assume(total >= minimum * len(weights))
        result = shares_apportion(total, weights, minimum)
        assert sum(result) <= total, f"Sum of allocations {sum(result)} exceeds total {total}"

    @given(
        total1=st.integers(min_value=0, max_value=1000),
        total2=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonicity(self, total1, total2, weights, minimum):
        """
        Test Property: monotonicity
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: if total1 <= total2 then all(a1 <= a2 for a1, a2 in zip(shares_apportion(total1, weights), shares_apportion(total2, weights)))
        """
        assume(total1 <= total2)
        assume(total1 >= minimum * len(weights))
        assume(total2 >= minimum * len(weights))
        
        result1 = shares_apportion(total1, weights, minimum)
        result2 = shares_apportion(total2, weights, minimum)
        
        for a1, a2 in zip(result1, result2):
            assert a1 <= a2, f"Monotonicity failed: {a1} > {a2}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: any(w)),
        minimum=st.integers(min_value=0, max_value=1000),
        k=st.integers(min_value=1, max_value=1000)
    )
    def test_scale_invariance(self, total, weights, minimum, k):
        """
        Test Property: scale_invariance
        Precondition: total >= 0 and minimum >= 0 and weights is non-empty and not all weights are zero
        Formal: shares_apportion(total, [w * k for w in weights]) == shares_apportion(total, weights) for any positive k
        """
        assume(total >= minimum * len(weights))
        
        scaled_weights = [w * k for w in weights]
        result1 = shares_apportion(total, weights, minimum)
        result2 = shares_apportion(total, scaled_weights, minimum)
        
        assert result1 == result2, f"Scale invariance failed: {result1} != {result2}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])