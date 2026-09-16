"""
Hypothesis-based property tests for budget_mix function.

This test suite exercises all semantic properties identified for the
budget_mix function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists

from dataset.python_programs.budget_mix import budget_mix


class TestBudgetMixErrorConditions:
    """Test error conditions and exception handling."""

    @given(
        current=st.lists(st.floats(allow_infinity=False, allow_nan=False)),
        target=st.lists(st.floats(allow_infinity=False, allow_nan=False))
    )
    def test_shape_mismatch_error(self, current, target):
        """Test that different length inputs raise ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            budget_mix(current, target)

    @given(target=st.lists(st.floats(allow_infinity=False, allow_nan=False)))
    def test_empty_allocation_error(self, target):
        """Test that empty current allocation raises ValueError."""
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            budget_mix(current, target)


class TestBudgetMixProperties:
    """Test semantic properties of budget_mix function."""

    # Strategy for valid inputs
    valid_lists = st.lists(
        st.floats(min_value=-1000, max_value=1000, allow_infinity=False, allow_nan=False),
        min_size=1,
        max_size=20
    )
    
    damping_factor = st.floats(min_value=0, max_value=1, allow_infinity=False, allow_nan=False)

    @given(
        current=valid_lists,
        target=valid_lists,
        damping=damping_factor
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output length matches input length."""
        assume(len(current) == len(target))
        
        result = budget_mix(current, target, damping=damping)
        assert len(result) == len(current), \
            f"Length mismatch: {len(result)} != {len(current)}"

    @given(
        current=valid_lists,
        target=valid_lists,
        damping=damping_factor
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function returns non-None for non-empty input."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = budget_mix(current, target, damping=damping)
        assert result is not None, "Function should return non-None for non-empty input"

    @given(
        current=valid_lists,
        target=valid_lists,
        damping=damping_factor
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that result follows linear interpolation formula."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = budget_mix(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, \
                f"Linear interpolation failed at index {i}: {result[i]} != {expected}"

    @given(
        current=valid_lists,
        damping=damping_factor
    )
    def test_identity_on_same_inputs(self, current, damping):
        """Test that identical inputs return the original input."""
        assume(current != [])
        
        target = current.copy()
        result = budget_mix(current, target, damping=damping)
        
        assert result == current, \
            f"Identity property failed: {result} != {current}"

    @given(
        current=valid_lists,
        target=valid_lists,
        damping=damping_factor
    )
    def test_damping_factor_effect(self, current, target, damping):
        """Test that damping factor controls movement towards target."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = budget_mix(current, target, damping=damping)
        
        # For each element, check that result is between current and target
        # (or equal to current if damping is 0, or equal to target if damping is 1)
        for i in range(len(current)):
            if damping == 0:
                assert result[i] == current[i], \
                    f"Damping=0 should preserve current: {result[i]} != {current[i]}"
            elif damping == 1:
                assert result[i] == target[i], \
                    f"Damping=1 should reach target: {result[i]} != {target[i]}"
            else:
                # Result should be between current and target
                if current[i] <= target[i]:
                    assert current[i] <= result[i] <= target[i], \
                        f"Result not between current and target: {result[i]} not in [{current[i]}, {target[i]}]"
                else:
                    assert target[i] <= result[i] <= current[i], \
                        f"Result not between current and target: {result[i]} not in [{target[i]}, {current[i]}]"

    @given(
        current=valid_lists,
        target=valid_lists,
        damping=damping_factor
    )
    def test_no_renormalization_bug(self, current, target, damping):
        """Test that function does not renormalize when sum(current) == 1.0."""
        assume(len(current) == len(target))
        assume(current != [])
        
        # Create a normalized current allocation
        current_sum = sum(current)
        assume(current_sum != 0)
        
        normalized_current = [x / current_sum for x in current]
        assume(abs(sum(normalized_current) - 1.0) < 1e-10)
        
        result = budget_mix(normalized_current, target, damping=damping)
        result_sum = sum(result)
        
        # The sum should generally not be 1.0 (unless by coincidence)
        # We can't assert it's never 1.0, but we can test that it's not
        # always 1.0 by checking a variety of cases
        if damping != 0 and target != normalized_current:
            # When damping > 0 and target differs from current,
            # the sum should generally change
            assert abs(result_sum - 1.0) > 1e-10 or abs(damping) < 1e-10, \
                f"Function appears to renormalize when it shouldn't: sum={result_sum}"


class TestBudgetMixEdgeCases:
    """Test edge cases and boundary conditions."""

    damping_factor = st.floats(min_value=0, max_value=1, allow_infinity=False, allow_nan=False)

    def test_zero_damping(self):
        """Test behavior with zero damping factor."""
        current = [1.0, 2.0, 3.0]
        target = [4.0, 5.0, 6.0]
        damping = 0.0
        
        result = budget_mix(current, target, damping=damping)
        assert result == current, "Zero damping should preserve current allocation"

    def test_full_damping(self):
        """Test behavior with full damping factor."""
        current = [1.0, 2.0, 3.0]
        target = [4.0, 5.0, 6.0]
        damping = 1.0
        
        result = budget_mix(current, target, damping=damping)
        assert result == target, "Full damping should reach target allocation"

    @given(
        current=st.lists(st.floats(min_value=-100, max_value=100, allow_infinity=False, allow_nan=False), min_size=1, max_size=5),
        damping=damping_factor
    )
    def test_single_element_lists(self, current, damping):
        """Test with single element lists."""
        target = [current[0] + 1]  # Different from current
        
        result = budget_mix(current, target, damping=damping)
        
        assert len(result) == 1
        expected = current[0] + (target[0] - current[0]) * damping
        assert abs(result[0] - expected) < 1e-10

    @given(
        size=st.integers(min_value=1, max_value=10),
        damping=damping_factor
    )
    def test_equal_length_lists(self, size, damping):
        """Test with equal length lists of various sizes."""
        current = [1.0] * size
        target = [2.0] * size
        
        result = budget_mix(current, target, damping=damping)
        
        assert len(result) == size
        expected = 1.0 + (2.0 - 1.0) * damping
        assert all(abs(r - expected) < 1e-10 for r in result)

    @given(
        current=st.lists(st.floats(min_value=-10, max_value=10, allow_infinity=False, allow_nan=False), min_size=2, max_size=10),
        damping=damping_factor
    )
    def test_negative_values(self, current, damping):
        """Test with negative values in current allocation."""
        target = [-x for x in current]  # Opposite signs
        
        result = budget_mix(current, target, damping=damping)
        
        assert len(result) == len(current)
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10

    def test_very_small_damping(self):
        """Test with very small damping factor."""
        current = [1.0, 2.0, 3.0]
        target = [10.0, 20.0, 30.0]
        damping = 1e-10
        
        result = budget_mix(current, target, damping=damping)
        
        # Result should be very close to current
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-8, \
                f"Very small damping should barely change values: {result[i]} vs {current[i]}"

    def test_very_large_values(self):
        """Test with very large values."""
        current = [1e6, 2e6, 3e6]
        target = [4e6, 5e6, 6e6]
        damping = 0.5
        
        result = budget_mix(current, target, damping=damping)
        
        assert len(result) == 3
        for i in range(3):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-6, \
                f"Large values test failed at index {i}: {result[i]} vs {expected}"


class TestBudgetMixTypeSafety:
    """Test type safety and input validation."""

    damping_factor = st.floats(min_value=0, max_value=1, allow_infinity=False, allow_nan=False)

    @given(
        current=st.lists(st.floats(allow_infinity=False, allow_nan=False)),
        target=st.lists(st.floats(allow_infinity=False, allow_nan=False)),
        damping=damping_factor
    )
    def test_float_outputs(self, current, target, damping):
        """Test that all outputs are floats."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = budget_mix(current, target, damping=damping)
        
        assert all(isinstance(x, float) for x in result), \
            f"Found non-float output in {result}"

    def test_integer_inputs(self):
        """Test with integer inputs (should be converted to floats)."""
        current = [1, 2, 3]
        target = [4, 5, 6]
        damping = 0.5
        
        result = budget_mix(current, target, damping=damping)
        
        assert len(result) == 3
        assert all(isinstance(x, float) for x in result)
        expected = [2.5, 3.5, 4.5]
        for i in range(3):
            assert abs(result[i] - expected[i]) < 1e-10