import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import floats, lists, one_of, just
import math

from dataset.python_programs.realign_power import realign_power


class TestRealignPowerProperties:
    """Test suite for realign_power function using Hypothesis testing framework."""
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when lengths are equal."""
        assume(len(current) == len(target))
        result = realign_power(current, target, damping)
        assert len(result) == len(current), f"Output length {len(result)} doesn't match input length {len(current)}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_linear_interpolation(self, current, target, damping):
        """Test that realign_power implements linear interpolation formula."""
        assume(len(current) == len(target))
        result = realign_power(current, target, damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9, abs_tol=1e-9), \
                f"Linear interpolation failed at index {i}: got {result[i]}, expected {expected}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_damping_factor_application(self, current, target, damping):
        """Test that damping factor is correctly applied to differences."""
        assume(len(current) == len(target))
        result = realign_power(current, target, damping)
        
        for i in range(len(current)):
            change = result[i] - current[i]
            expected_change = (target[i] - current[i]) * damping
            assert math.isclose(change, expected_change, rel_tol=1e-9, abs_tol=1e-9), \
                f"Damping factor application failed at index {i}: got {change}, expected {expected_change}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    @settings(max_examples=50, deadline=None)
    def test_target_convergence(self, current, target):
        """Test that with damping=1.0, result equals target."""
        assume(len(current) == len(target))
        result = realign_power(current, target, 1.0)
        
        for i in range(len(current)):
            assert math.isclose(result[i], target[i], rel_tol=1e-9, abs_tol=1e-9), \
                f"Target convergence failed at index {i}: got {result[i]}, expected {target[i]}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    @settings(max_examples=50, deadline=None)
    def test_no_change_when_damping_zero(self, current, target):
        """Test that with damping=0.0, result equals current."""
        assume(len(current) == len(target))
        result = realign_power(current, target, 0.0)
        
        for i in range(len(current)):
            assert math.isclose(result[i], current[i], rel_tol=1e-9, abs_tol=1e-9), \
                f"No change when damping=0 failed at index {i}: got {result[i]}, expected {current[i]}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_monotonic_movement(self, current, target, damping):
        """Test that result values are between current and target values."""
        assume(len(current) == len(target))
        result = realign_power(current, target, damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val, \
                f"Monotonic movement violated at index {i}: result {result[i]} not between {min_val} and {max_val}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_error_on_empty_input(self, current, target, damping):
        """Test that empty current list raises ValueError."""
        with pytest.raises(ValueError, match="empty allocation"):
            realign_power([], target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_error_on_shape_mismatch(self, current, target, damping):
        """Test that mismatched lengths raise ValueError."""
        assume(len(current) != len(target))
        with pytest.raises(ValueError, match="shape mismatch"):
            realign_power(current, target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_shape_mismatch_error_branch(self, current, target, damping):
        """Test the shape mismatch error branch specifically."""
        assume(len(current) != len(target))
        with pytest.raises(ValueError, match="shape mismatch"):
            realign_power(current, target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_empty_allocation_error_branch(self, current, target, damping):
        """Test the empty allocation error branch specifically."""
        with pytest.raises(ValueError, match="empty allocation"):
            realign_power([], target, damping)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])