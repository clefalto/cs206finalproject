"""
Tests for the adjust_supply function using Hypothesis testing framework.
Tests cover all semantic properties identified in properties/adjust_supply_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.adjust_supply import adjust_supply


class TestAdjustSupply:
    """Test class for adjust_supply function covering all semantic properties."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """
        Test branch property: shape_mismatch_error
        When len(current) != len(target), adjust_supply should raise ValueError("shape mismatch")
        """
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            adjust_supply(current, target, damping=damping)

    @given(
        target=lists(floats(min_value=-1000, max_value=1000), min_size=0, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_empty_allocation_error(self, target, damping):
        """
        Test branch property: empty_allocation_error
        When current is empty, adjust_supply should raise ValueError("empty allocation")
        """
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            adjust_supply(current, target, damping=damping)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_shape_consistency(self, current, target, damping):
        """
        Test function property: shape_consistency
        Precondition: len(current) == len(target)
        Formal: len(adjust_supply(current, target)) == len(current)
        """
        assume(len(current) == len(target))
        
        result = adjust_supply(current, target, damping=damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_non_empty_input(self, current, target, damping):
        """
        Test function property: non_empty_input
        Precondition: current != []
        Formal: adjust_supply(current, target) is not None
        """
        assume(current != [])
        
        result = adjust_supply(current, target, damping=damping)
        assert result is not None

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_linear_interpolation(self, current, target, damping):
        """
        Test function property: linear_interpolation
        Precondition: len(current) == len(target) and current != []
        Formal: adjust_supply(current, target)[i] == current[i] + (target[i] - current[i]) * damping for all i
        """
        assume(len(current) == len(target) and current != [])
        
        result = adjust_supply(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {expected}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.001, max_value=1.0)
    )
    def test_metamorphic_monotonicity(self, current, target, damping):
        """
        Test function property: metamorphic_monotonicity
        Precondition: len(current) == len(target) and current != [] and damping > 0
        Formal: if target[i] > current[i] then adjust_supply(current, target)[i] > current[i] for all i
        """
        assume(len(current) == len(target) and current != [] and damping > 0)
        
        result = adjust_supply(current, target, damping=damping)
        
        for i in range(len(current)):
            if target[i] > current[i]:
                assert result[i] > current[i], f"Monotonicity violated at index {i}: target={target[i]}, current={current[i]}, result={result[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.001, max_value=0.999)
    )
    def test_metamorphic_convergence(self, current, target, damping):
        """
        Test function property: metamorphic_convergence
        Precondition: len(current) == len(target) and current != [] and 0 < damping < 1
        Formal: abs(adjust_supply(current, target)[i] - target[i]) < abs(current[i] - target[i]) for all i
        """
        assume(len(current) == len(target) and current != [] and 0 < damping < 1)
        
        result = adjust_supply(current, target, damping=damping)
        
        for i in range(len(current)):
            distance_before = abs(current[i] - target[i])
            distance_after = abs(result[i] - target[i])
            
            # Only test convergence when there's actually a difference to converge
            if distance_before > 1e-10:
                assert distance_after < distance_before, f"Convergence violated at index {i}: before={distance_before}, after={distance_after}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_invariant_length_preservation(self, current, target, damping):
        """
        Test function property: invariant_length_preservation
        Precondition: len(current) == len(target) and current != []
        Formal: len(adjust_supply(current, target)) == len(current)
        """
        assume(len(current) == len(target) and current != [])
        
        result = adjust_supply(current, target, damping=damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_precondition_shape_match(self, current, target, damping):
        """
        Test function property: precondition_shape_match
        Precondition: len(current) == len(target)
        Formal: adjust_supply(current, target) is defined
        """
        assume(len(current) == len(target))
        
        # If the precondition is met, the function should not raise an exception
        # (other than potential numerical issues which are not part of the semantic properties)
        try:
            result = adjust_supply(current, target, damping=damping)
            assert result is not None
        except ValueError as e:
            # Only allow ValueError for empty allocation, not for shape mismatch
            if "shape mismatch" in str(e):
                pytest.fail(f"Shape mismatch error when precondition should be satisfied: {e}")
            elif "empty allocation" in str(e):
                # This is expected if current is empty, but our precondition doesn't guarantee non-empty
                pass

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_precondition_non_empty(self, current, target, damping):
        """
        Test function property: precondition_non_empty
        Precondition: current != []
        Formal: adjust_supply(current, target) is defined
        """
        assume(current != [])
        
        # If the precondition is met, the function should not raise an exception
        # (other than potential numerical issues which are not part of the semantic properties)
        try:
            result = adjust_supply(current, target, damping=damping)
            assert result is not None
        except ValueError as e:
            # Only allow ValueError for shape mismatch, not for empty allocation
            if "empty allocation" in str(e):
                pytest.fail(f"Empty allocation error when precondition should be satisfied: {e}")
            elif "shape mismatch" in str(e):
                # This is expected if shapes don't match, but our precondition doesn't guarantee matching shapes
                pass

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0.0, max_value=1.0)
    )
    def test_postcondition_adjustment(self, current, target, damping):
        """
        Test function property: postcondition_adjustment
        Precondition: len(current) == len(target) and current != []
        Formal: adjust_supply(current, target) contains adjusted values based on damping factor
        """
        assume(len(current) == len(target) and current != [])
        
        result = adjust_supply(current, target, damping=damping)
        
        # Verify that the result contains adjusted values
        # For each element, check that it's been adjusted according to the damping factor
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Adjustment incorrect at index {i}: got {result[i]}, expected {expected}"
            
        # Also verify that the result is different from input when damping > 0 and target != current
        if damping > 0 and any(target[i] != current[i] for i in range(len(current))):
            assert result != current, "Result should be different from input when adjustment is applied"

    # Additional edge case tests to complement the property-based tests

    def test_exact_damping_values(self):
        """Test specific damping values for predictable behavior."""
        current = [1.0, 2.0, 3.0]
        target = [4.0, 5.0, 6.0]
        
        # Test damping = 0 (no change)
        result_zero = adjust_supply(current, target, damping=0.0)
        assert result_zero == current
        
        # Test damping = 1 (full adjustment)
        result_full = adjust_supply(current, target, damping=1.0)
        assert result_full == target

    def test_negative_values(self):
        """Test that the function handles negative values correctly."""
        current = [-1.0, -2.0, 3.0]
        target = [2.0, -5.0, -1.0]
        
        result = adjust_supply(current, target, damping=0.5)
        expected = [-1.0 + (2.0 - (-1.0)) * 0.5, -2.0 + (-5.0 - (-2.0)) * 0.5, 3.0 + (-1.0 - 3.0) * 0.5]
        expected = [0.5, -3.5, 1.0]
        
        for i in range(len(result)):
            assert abs(result[i] - expected[i]) < 1e-10

    def test_single_element_lists(self):
        """Test with single element lists."""
        current = [5.0]
        target = [10.0]
        
        result = adjust_supply(current, target, damping=0.3)
        expected = [5.0 + (10.0 - 5.0) * 0.3]  # [6.5]
        
        assert abs(result[0] - expected[0]) < 1e-10