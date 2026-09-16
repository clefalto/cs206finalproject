#!/usr/bin/env python3
"""
Hypothesis-based property tests for the votes_apportion function.

This test file verifies all 24 semantic properties identified for the
votes_apportion function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, booleans, one_of, just

# Import the function under test
# Note: The actual import path should be adjusted based on the project structure
# For now, we'll assume the function is available in the current module or a known location
# try:
from dataset.python_programs.votes_apportion import votes_apportion
# except ImportError:
#     # If the function is not available, we'll create a mock implementation
#     # for testing purposes. This should be replaced with the actual import.
#     def votes_apportion(total, weights, minimum=0, floor_to_int=True):
#         """
#         Mock implementation of votes_apportion for testing.
#         This should be replaced with the actual function import.
#         """
#         if len(weights) == 0:
#             raise ValueError("weights required")
#         if total < 0:
#             raise ValueError("negative total")
#         if minimum < 0:
#             raise ValueError("negative minimum")
#         if sum(weights) == 0:
#             raise ValueError("zero total weight")
        
#         # Calculate shares
#         shares = []
#         weight_sum = sum(weights)
        
#         for w in weights:
#             portion = (w / weight_sum) * total
#             if portion > minimum:
#                 shares.append(portion)
#             else:
#                 shares.append(minimum)
        
#         # Apply floor_to_int if requested
#         if floor_to_int:
#             shares = [int(v) for v in shares]
        
#         return shares


class TestVotesApportionProperties:
    """Test class for votes_apportion semantic properties."""

    # Branch-level properties (error conditions)
    
    @given(
        total=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_empty_weights_error(self, total, weights, minimum, floor_to_int):
        """
        Test Property: empty_weights_error
        Condition: len(weights) == 0
        Formal: len(weights) == 0 => raises ValueError("weights required")
        """
        with pytest.raises(ValueError, match="weights required"):
            votes_apportion(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_negative_total_error(self, total, weights, minimum, floor_to_int):
        """
        Test Property: negative_total_error
        Condition: total < 0
        Formal: total < 0 => raises ValueError("negative total")
        """
        with pytest.raises(ValueError, match="negative total"):
            votes_apportion(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        minimum=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_negative_minimum_error(self, total, weights, minimum, floor_to_int):
        """
        Test Property: negative_minimum_error
        Condition: minimum < 0
        Formal: minimum < 0 => raises ValueError("negative minimum")
        """
        with pytest.raises(ValueError, match="negative minimum"):
            votes_apportion(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) == 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_zero_weight_sum_error(self, total, weights, minimum, floor_to_int):
        """
        Test Property: zero_weight_sum_error
        Condition: sum(weights) == 0
        Formal: sum(weights) == 0 => raises ValueError("zero total weight")
        """
        with pytest.raises(ValueError, match="zero total weight"):
            votes_apportion(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_portion_above_minimum(self, total, weights, minimum, floor_to_int):
        """
        Test Property: portion_above_minimum
        Condition: portion > minimum
        Formal: portion > minimum => shares[i] == portion
        """
        assume(len(weights) > 0)
        assume(sum(weights) > 0)
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        weight_sum = sum(weights)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion > minimum:
                if floor_to_int:
                    expected = int(portion)
                else:
                    expected = portion
                assert result[i] == expected, f"Portion above minimum failed for index {i}: {result[i]} != {expected}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_portion_below_minimum(self, total, weights, minimum, floor_to_int):
        """
        Test Property: portion_below_minimum
        Condition: portion <= minimum
        Formal: portion <= minimum => shares[i] == minimum
        """
        assume(len(weights) > 0)
        assume(sum(weights) > 0)
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        weight_sum = sum(weights)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion <= minimum:
                if floor_to_int:
                    expected = int(minimum)
                else:
                    expected = minimum
                assert result[i] == expected, f"Portion below minimum failed for index {i}: {result[i]} != {expected}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_integer_flooring(self, total, weights, minimum, floor_to_int):
        """
        Test Property: integer_flooring
        Condition: floor_to_int
        Formal: floor_to_int => return [int(v) for v in shares]
        """
        assume(len(weights) > 0)
        assume(sum(weights) > 0)
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, int) for s in result), f"Integer flooring failed: found non-integer in result {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.just(False)
    )
    def test_float_preservation(self, total, weights, minimum, floor_to_int):
        """
        Test Property: float_preservation
        Condition: not floor_to_int
        Formal: not floor_to_int => return shares
        """
        assume(len(weights) > 0)
        assume(sum(weights) > 0)
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, (int, float)) for s in result), f"Float preservation failed: found non-numeric in result {result}"

    # Function-level properties (invariants and postconditions)
    
    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_non_empty_weights_precondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: non_empty_weights_precondition
        Precondition: len(weights) > 0
        Formal: len(weights) > 0
        """
        assume(sum(weights) > 0)
        # This is a precondition test - the function should work when precondition is met
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert len(weights) > 0, "Precondition violated: weights should be non-empty"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_non_negative_total_precondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: non_negative_total_precondition
        Precondition: total >= 0
        Formal: total >= 0
        """
        assume(sum(weights) > 0)
        # This is a precondition test - the function should work when precondition is met
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert total >= 0, "Precondition violated: total should be non-negative"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_non_negative_minimum_precondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: non_negative_minimum_precondition
        Precondition: minimum >= 0
        Formal: minimum >= 0
        """
        assume(sum(weights) > 0)
        # This is a precondition test - the function should work when precondition is met
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert minimum >= 0, "Precondition violated: minimum should be non-negative"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_non_zero_weight_sum_precondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: non_zero_weight_sum_precondition
        Precondition: sum(weights) > 0
        Formal: sum(weights) > 0
        """
        # This is a precondition test - the function should work when precondition is met
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert sum(weights) > 0, "Precondition violated: sum of weights should be positive"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_shares_length_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: shares_length_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: len(shares) == len(weights)
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert len(result) == len(weights), f"Length invariant failed: len({result}) != len({weights})"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_shares_non_negative_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: shares_non_negative_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: all(s >= 0 for s in shares)
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(s >= 0 for s in result), f"Non-negative invariant failed: found negative value in {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_shares_minimum_bound_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: shares_minimum_bound_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: all(s >= minimum for s in shares)
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(s >= minimum for s in result), f"Minimum bound invariant failed: found value below minimum {minimum} in {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_shares_sum_bound_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: shares_sum_bound_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: sum(shares) >= total
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert sum(result) >= total, f"Sum bound invariant failed: sum({result}) < {total}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_proportional_allocation_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: proportional_allocation_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0 and all(w/sum(weights)*total >= minimum for w in weights)
        Formal: shares[i] == (weights[i] / sum(weights)) * total for all i
        """
        assume(all(w/sum(weights)*total >= minimum for w in weights))
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        weight_sum = sum(weights)
        
        for i, w in enumerate(weights):
            expected = (w / weight_sum) * total
            if floor_to_int:
                expected = int(expected)
            
            assert result[i] == expected, f"Proportional allocation failed for index {i}: {result[i]} != {expected}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_minimum_enforcement_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: minimum_enforcement_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: shares[i] >= minimum for all i
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(s >= minimum for s in result), f"Minimum enforcement failed: found value below minimum {minimum} in {result}"

    @given(
        total=st.integers(min_value=0, max_value=1000),
        weights=st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.integers(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_integer_output_postcondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: integer_output_postcondition
        Precondition: floor_to_int and len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: all(isinstance(s, int) for s in shares)
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, int) for s in result), f"Integer output postcondition failed: found non-integer in {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.just(False)
    )
    def test_float_output_postcondition(self, total, weights, minimum, floor_to_int):
        """
        Test Property: float_output_postcondition
        Precondition: not floor_to_int and len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: all(isinstance(s, (int, float)) for s in shares)
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, (int, float)) for s in result), f"Float output postcondition failed: found non-numeric in {result}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_monotonicity_invariant(self, total, weights, minimum, floor_to_int):
        """
        Test Property: monotonicity_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0
        Formal: weights[i] >= weights[j] => shares[i] >= shares[j]
        """
        result = votes_apportion(total, weights, minimum, floor_to_int)
        
        for i in range(len(weights)):
            for j in range(len(weights)):
                if weights[i] >= weights[j]:
                    assert result[i] >= result[j], f"Monotonicity failed: weights[{i}]={weights[i]} >= weights[{j}]={weights[j]} but result[{i}]={result[i]} < result[{j}]={result[j]}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans(),
        k=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance_invariant(self, total, weights, minimum, floor_to_int, k):
        """
        Test Property: scale_invariance_invariant
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0 and k > 0
        Formal: votes_apportion(total, [k*w for w in weights], minimum, floor_to_int) == votes_apportion(total, weights, minimum, floor_to_int)
        """
        scaled_weights = [k * w for w in weights]
        result1 = votes_apportion(total, weights, minimum, floor_to_int)
        result2 = votes_apportion(total, scaled_weights, minimum, floor_to_int)
        
        assert result1 == result2, f"Scale invariance failed: {result1} != {result2}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_total_preservation_metamorphic(self, total, weights, minimum, floor_to_int):
        """
        Test Property: total_preservation_metamorphic
        Precondition: len(weights) > 0 and total >= 0 and minimum >= 0 and sum(weights) > 0 and all(w/sum(weights)*total >= minimum for w in weights)
        Formal: sum(votes_apportion(total, weights, minimum, floor_to_int)) == total
        """
        assume(all(w/sum(weights)*total >= minimum for w in weights))
        
        result = votes_apportion(total, weights, minimum, floor_to_int)
        assert sum(result) == total, f"Total preservation failed: sum({result}) != {total}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        minimum2=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_minimum_increase_monotonicity(self, total, weights, minimum1, minimum2, floor_to_int):
        """
        Test Property: minimum_increase_monotonicity
        Precondition: len(weights) > 0 and total >= 0 and minimum1 >= 0 and minimum2 >= 0 and minimum2 > minimum1 and sum(weights) > 0
        Formal: all(s2 >= s1 for s1, s2 in zip(votes_apportion(total, weights, minimum1, floor_to_int), votes_apportion(total, weights, minimum2, floor_to_int)))
        """
        assume(minimum2 > minimum1)
        
        result1 = votes_apportion(total, weights, minimum1, floor_to_int)
        result2 = votes_apportion(total, weights, minimum2, floor_to_int)
        
        for s1, s2 in zip(result1, result2):
            assert s2 >= s1, f"Minimum increase monotonicity failed: {s2} < {s1}"

    @given(
        total1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        total2=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100).filter(lambda w: sum(w) > 0),
        minimum=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        floor_to_int=st.booleans()
    )
    def test_total_increase_monotonicity(self, total1, total2, weights, minimum, floor_to_int):
        """
        Test Property: total_increase_monotonicity
        Precondition: len(weights) > 0 and total1 >= 0 and total2 >= 0 and total2 > total1 and minimum >= 0 and sum(weights) > 0
        Formal: all(s2 >= s1 for s1, s2 in zip(votes_apportion(total1, weights, minimum, floor_to_int), votes_apportion(total2, weights, minimum, floor_to_int)))
        """
        assume(total2 > total1)
        
        result1 = votes_apportion(total1, weights, minimum, floor_to_int)
        result2 = votes_apportion(total2, weights, minimum, floor_to_int)
        
        for s1, s2 in zip(result1, result2):
            assert s2 >= s1, f"Total increase monotonicity failed: {s2} < {s1}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])