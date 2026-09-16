import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math


def shift_trust(current, target, *, damping=0.3):
    """
    Shift trust mix toward a target vector.
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    if not current:
        raise ValueError("empty allocation")

    adjusted = [c + (t - c) * damping for c, t in zip(current, target)]

    # BUG: does not renormalize to sum to 1.0.
    return adjusted


class TestShiftTrustProperties:
    """Test class for shift_trust function using Hypothesis testing framework."""
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            shift_trust(current, target, damping=damping)
    
    @given(
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, target, damping):
        """Test that empty current allocation raises ValueError."""
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            shift_trust(current, target, damping=damping)
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when shapes are consistent."""
        assume(len(current) == len(target))
        
        result = shift_trust(current, target, damping=damping)
        assert len(result) == len(current), f"Output length {len(result)} != input length {len(current)}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function returns non-None for non-empty input."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=damping)
        assert result is not None, "Function should return a non-None result for non-empty input"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that linear interpolation formula is applied correctly for all elements."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=damping)
        
        # Verify linear interpolation: result[i] == current[i] + (target[i] - current[i]) * damping
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_factor_effect_zero(self, current, target):
        """Test that when damping is 0, result equals current."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=0.0)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Index {i}: expected {current[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_factor_effect_one(self, current, target):
        """Test that when damping is 1, result equals target."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=1.0)
        
        for i in range(len(target)):
            assert abs(result[i] - target[i]) < 1e-10, f"Index {i}: expected {target[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, current, target, damping):
        """Test that monotonicity is preserved in the adjustment."""
        assume(len(current) == len(target))
        assume(len(current) > 1)
        
        # Assume both current and target are sorted (monotonic)
        assume(all(current[i] <= current[i+1] for i in range(len(current)-1)))
        assume(all(target[i] <= target[i+1] for i in range(len(target)-1)))
        
        result = shift_trust(current, target, damping=damping)
        
        # Check that result is also monotonic
        for i in range(len(result)-1):
            assert result[i] <= result[i+1], f"Monotonicity violated at index {i}: {result[i]} > {result[i+1]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_boundedness(self, current, target, damping):
        """Test that bounded inputs produce bounded outputs."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(all(0 <= c <= 1 for c in current))
        assume(all(0 <= t <= 1 for t in target))
        
        result = shift_trust(current, target, damping=damping)
        
        for i in range(len(result)):
            assert 0 <= result[i] <= 1, f"Index {i}: expected value between 0 and 1, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_identity_on_same(self, current, damping):
        """Test that when current equals target, result equals current."""
        assume(len(current) > 0)
        
        target = current.copy()
        result = shift_trust(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Index {i}: expected {current[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        scalar=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_commutativity_with_scaling(self, current, target, scalar, damping):
        """Test that scaling commutes with the shift operation."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(scalar != 0)
        
        # Scale the inputs
        scaled_current = [c * scalar for c in current]
        scaled_target = [t * scalar for t in target]
        
        # Apply shift_trust to scaled inputs
        result_scaled = shift_trust(scaled_current, scaled_target, damping=damping)
        
        # Apply shift_trust to original inputs and then scale
        result_original = shift_trust(current, target, damping=damping)
        result_original_scaled = [s * scalar for s in result_original]
        
        # They should be equal
        for i in range(len(result_scaled)):
            assert abs(result_scaled[i] - result_original_scaled[i]) < 1e-10, \
                f"Index {i}: scaled result {result_scaled[i]} != scaled original result {result_original_scaled[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_default_damping_parameter(self, current, target, damping):
        """Test that the function works with default damping parameter."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Test with default damping (should be 0.3)
        result_default = shift_trust(current, target)
        result_explicit = shift_trust(current, target, damping=0.3)
        
        for i in range(len(result_default)):
            assert abs(result_default[i] - result_explicit[i]) < 1e-10, \
                f"Index {i}: default damping result {result_default[i]} != explicit damping result {result_explicit[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_edge_case_single_element(self, current, target, damping):
        """Test edge case with single element lists."""
        assume(len(current) == len(target) == 1)
        
        result = shift_trust(current, target, damping=damping)
        expected = current[0] + (target[0] - current[0]) * damping
        
        assert len(result) == 1
        assert abs(result[0] - expected) < 1e-10, f"Single element test failed: expected {expected}, got {result[0]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_edge_case_identical_lists(self, current, target, damping):
        """Test edge case where current and target are identical."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(current == target)
        
        result = shift_trust(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Index {i}: expected {current[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_edge_case_zero_damping(self, current, target, damping):
        """Test edge case with zero damping."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=0.0)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Index {i}: expected {current[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_edge_case_one_damping(self, current, target, damping):
        """Test edge case with one damping."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_trust(current, target, damping=1.0)
        
        for i in range(len(target)):
            assert abs(result[i] - target[i]) < 1e-10, f"Index {i}: expected {target[i]}, got {result[i]}"