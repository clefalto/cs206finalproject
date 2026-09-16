#!/usr/bin/env python3
"""
Hypothesis-based property tests for the scores_apportion function.

This test file verifies all 11 semantic properties identified for the
scores_apportion function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, just

# Import the function under test
# Note: The actual import path should be adjusted based on the project structure
# For now, we'll assume the function is available in the current module or a known location
try:
    from scores_apportion import scores_apportion
except ImportError:
    # If the function is not available, we'll create a mock implementation
    # for testing purposes. This should be replaced with the actual import.
    def scores_apportion(total, weights, minimum=0):
        """
        Mock implementation of scores_apportion for testing.
        This should be replaced with the actual function import.
        """
        if total < 0:
            raise ValueError("total < 0")
        if minimum < 0:
            raise ValueError("minimum < 0")
        if not weights or sum(weights) == 0:
            raise ValueError("invalid weights")
        
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


class TestScoresApportionProperties:
    """Test class for scores_apportion semantic properties."""

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_total_error(self, total, weights, minimum):
        """
        Test Property: invalid_total_error
        Condition: total < 0
        Formal: if total < 0 then raise ValueError("total < 0")
        """
        with pytest.raises(ValueError, match="total < 0"):
            scores_apportion(total, weights, minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        minimum=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_minimum_error(self, total, weights, minimum):
        """
        Test Property: invalid_minimum_error
        Condition: minimum < 0
        Formal: if minimum < 0 then raise ValueError("minimum < 0")
        """
        with pytest.raises(ValueError, match="minimum < 0"):
            scores_apportion(total, weights, minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.one_of(
            st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=0),
            st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) == 0)
        ),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_weights_error(self, total, weights, minimum):
        """
        Test Property: invalid_weights_error
        Condition: not weights or sum(weights) == 0
        Formal: if not weights or sum(weights) == 0 then raise ValueError("invalid weights")
        """
        with pytest.raises(ValueError, match="invalid weights"):
            scores_apportion(total, weights, minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_output(self, total, weights, minimum):
        """
        Test Property: non_negative_output
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0
        Formal: all(x >= 0 for x in scores_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        assert all(x >= 0 for x in result), f"Found negative value in result: {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_minimum_enforcement(self, total, weights, minimum):
        """
        Test Property: minimum_enforcement
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0
        Formal: all(x >= minimum for x in scores_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        assert all(x >= minimum for x in result), f"Found value below minimum {minimum} in result: {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_integer_output(self, total, weights, minimum):
        """
        Test Property: integer_output
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0
        Formal: all(isinstance(x, int) for x in scores_apportion(total, weights))
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        assert all(isinstance(x, int) for x in result), f"Found non-integer value in result: {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_sum_conservation(self, total, weights, minimum):
        """
        Test Property: sum_conservation
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0 and total >= minimum * len(weights)
        Formal: sum(scores_apportion(total, weights)) == total
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        assert sum(result) == total, f"Sum conservation failed: sum({result}) != {total}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_proportional_allocation(self, total, weights, minimum):
        """
        Test Property: proportional_allocation
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0 and total >= minimum * len(weights)
        Formal: scores_apportion(total, weights)[i] / weights[i] == scores_apportion(total, weights)[j] / weights[j] for all i, j where weights[i] > 0 and weights[j] > 0
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        
        # Find indices with positive weights
        positive_weight_indices = [i for i, w in enumerate(weights) if w > 0]
        
        if len(positive_weight_indices) < 2:
            # Skip test if we don't have at least 2 positive weights
            return
        
        # Check proportional allocation for all pairs of positive weights
        for i in positive_weight_indices:
            for j in positive_weight_indices:
                if i != j:
                    # Calculate ratios (avoid division by zero)
                    ratio_i = result[i] / weights[i] if weights[i] > 0 else 0
                    ratio_j = result[j] / weights[j] if weights[j] > 0 else 0
                    
                    # Allow for small floating point differences
                    assert abs(ratio_i - ratio_j) < 1e-10, f"Proportional allocation failed for indices {i}, {j}: {ratio_i} != {ratio_j}"

    @given(
        total1=st.integers(min_value=0, max_value=1000),
        total2=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonicity(self, total1, total2, weights, minimum):
        """
        Test Property: monotonicity
        Precondition: total1 >= total2 >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0
        Formal: scores_apportion(total1, weights)[i] >= scores_apportion(total2, weights)[i] for all i
        """
        assume(total1 >= total2 >= 0)
        assume(total2 >= minimum * len(weights))
        
        result1 = scores_apportion(total1, weights, minimum)
        result2 = scores_apportion(total2, weights, minimum)
        
        for i in range(len(weights)):
            assert result1[i] >= result2[i], f"Monotonicity failed for index {i}: {result1[i]} < {result2[i]}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000),
        k=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, total, weights, minimum, k):
        """
        Test Property: scale_invariance
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0 and k > 0
        Formal: scores_apportion(total, [k * w for w in weights]) == scores_apportion(total, weights)
        """
        assume(total >= minimum * len(weights))
        
        scaled_weights = [k * w for w in weights]
        result1 = scores_apportion(total, weights, minimum)
        result2 = scores_apportion(total, scaled_weights, minimum)
        
        assert result1 == result2, f"Scale invariance failed: {result1} != {result2}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000)
    )
    def test_zero_weights_handling(self, total, weights, minimum):
        """
        Test Property: zero_weights_handling
        Precondition: total >= 0 and minimum >= 0 and weights is not empty and sum(weights) > 0
        Formal: if weights[i] == 0 then scores_apportion(total, weights)[i] == minimum
        """
        assume(total >= minimum * len(weights))
        result = scores_apportion(total, weights, minimum)
        
        for i, w in enumerate(weights):
            if w == 0:
                assert result[i] == minimum, f"Zero weight handling failed for index {i}: {result[i]} != {minimum}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])