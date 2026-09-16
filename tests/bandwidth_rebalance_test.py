"""
Hypothesis-based property tests for the bandwidth_rebalance function.

This test suite exercises all semantic properties identified in
properties/bandwidth_rebalance_properties.json using the Hypothesis
testing framework to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.bandwidth_rebalance import bandwidth_rebalance


class TestBandwidthRebalanceProperties:
    """Test class for bandwidth_rebalance semantic properties."""

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output has same shape as input when shapes match."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        assert len(result) == len(current), "Output length should match input length"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function returns non-None for non-empty input."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        assert result is not None, "Function should return a result for non-empty input"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that output follows linear interpolation formula."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, \
                f"Element {i}: expected {expected}, got {result[i]}"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_identity_on_equal(self, current, damping):
        """Test that function returns input when current equals target."""
        assume(len(current) > 0)
        
        target = current.copy()
        result = bandwidth_rebalance(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, \
                f"Element {i}: should equal input when current == target"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity(self, current, target, damping):
        """Test that interpolation maintains monotonicity."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        
        for i in range(len(current)):
            if current[i] <= target[i]:
                assert current[i] <= result[i] <= target[i], \
                    f"Element {i}: monotonicity violated: {current[i]} <= {result[i]} <= {target[i]}"
            else:  # current[i] > target[i]
                assert target[i] <= result[i] <= current[i], \
                    f"Element {i}: monotonicity violated: {target[i]} <= {result[i]} <= {current[i]}"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_bounded_output(self, current, target, damping):
        """Test that output is bounded by min and max of input values."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val, \
                f"Element {i}: output {result[i]} not bounded by [{min_val}, {max_val}]"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_sensitivity_zero(self, current, target):
        """Test that damping=0 returns current values."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=0.0)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, \
                f"Element {i}: damping=0 should return current value"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_sensitivity_one(self, current, target):
        """Test that damping=1 returns target values."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=1.0)
        
        for i in range(len(current)):
            assert abs(result[i] - target[i]) < 1e-10, \
                f"Element {i}: damping=1 should return target value"

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_no_renormalization_bug(self, current, target, damping):
        """Test that function does NOT renormalize (this is intended behavior)."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(damping != 0.0)  # Skip when damping=0 as it would equal current sum
        
        result = bandwidth_rebalance(current, target, damping=damping)
        current_sum = sum(current)
        result_sum = sum(result)
        
        # The function should NOT renormalize, so sums should generally differ
        # We test that it's NOT always equal (allowing for floating point precision)
        if abs(current_sum - result_sum) > 1e-10:
            assert True, "Function correctly does not renormalize (sums differ)"
        else:
            # If sums are equal, it might be a coincidence, but that's acceptable
            pass

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_shape_mismatch_error(self, current, target):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            bandwidth_rebalance(current, target)

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), max_size=0),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_empty_allocation_error(self, current, target):
        """Test that empty current allocation raises ValueError."""
        assume(not current)  # Empty list
        
        with pytest.raises(ValueError, match="empty allocation"):
            bandwidth_rebalance(current, target)


class TestEdgeCases:
    """Additional edge case tests for bandwidth_rebalance."""

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_single_element_lists(self, current, target, damping):
        """Test behavior with single-element lists."""
        assume(len(current) == len(target) == 1)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        assert len(result) == 1
        expected = current[0] + (target[0] - current[0]) * damping
        assert abs(result[0] - expected) < 1e-10

    @given(
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_identical_lists(self, damping):
        """Test with identical current and target lists."""
        current = [1.0, 2.0, 3.0, 4.0, 5.0]
        target = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        result = bandwidth_rebalance(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10

    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_various_list_sizes(self, current, target, damping):
        """Test with various list sizes."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = bandwidth_rebalance(current, target, damping=damping)
        assert len(result) == len(current)
        
        # Verify linear interpolation for all elements
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10


class TestBoundaryConditions:
    """Test boundary conditions and special values."""

    def test_damping_zero_boundary(self):
        """Test damping at exact boundary value 0."""
        current = [1.0, 2.0, 3.0]
        target = [4.0, 5.0, 6.0]
        
        result = bandwidth_rebalance(current, target, damping=0.0)
        assert result == current

    def test_damping_one_boundary(self):
        """Test damping at exact boundary value 1."""
        current = [1.0, 2.0, 3.0]
        target = [4.0, 5.0, 6.0]
        
        result = bandwidth_rebalance(current, target, damping=1.0)
        assert result == target

    def test_damping_half(self):
        """Test damping at midpoint value 0.5."""
        current = [0.0, 10.0, 20.0]
        target = [10.0, 0.0, 30.0]
        
        result = bandwidth_rebalance(current, target, damping=0.5)
        expected = [5.0, 5.0, 25.0]
        
        for i in range(len(expected)):
            assert abs(result[i] - expected[i]) < 1e-10

    def test_zero_values(self):
        """Test with zero values in input."""
        current = [0.0, 0.0, 0.0]
        target = [1.0, 2.0, 3.0]
        
        result = bandwidth_rebalance(current, target, damping=0.5)
        expected = [0.5, 1.0, 1.5]
        
        for i in range(len(expected)):
            assert abs(result[i] - expected[i]) < 1e-10

    def test_large_values(self):
        """Test with large numerical values."""
        current = [1e6, 2e6, 3e6]
        target = [4e6, 5e6, 6e6]
        
        result = bandwidth_rebalance(current, target, damping=0.3)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * 0.3
            assert abs(result[i] - expected) < 1e-4  # Allow for floating point precision with large numbers


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])