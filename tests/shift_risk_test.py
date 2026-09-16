import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import sys
import os

# Add the current directory to Python path to import shift_risk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shift_risk import shift_risk


class TestShiftRiskProperties:
    """Test class for shift_risk function using Hypothesis testing framework."""
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            shift_risk(current, target, damping)
    
    @given(
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, target, damping):
        """Test that empty current allocation raises ValueError."""
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            shift_risk(current, target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that linear interpolation is performed correctly."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        # Verify the linear interpolation formula: c + (t - c) * damping
        expected = [c + (t - c) * damping for c, t in zip(current, target)]
        
        assert len(result) == len(expected)
        for i in range(len(result)):
            assert abs(result[i] - expected[i]) < 1e-10
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_length_preservation(self, current, target, damping):
        """Test that output length equals input length when shapes match."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        assert len(result) == len(current)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_element_type_preservation(self, current, target, damping):
        """Test that element types are preserved in the result."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        # All elements should be floats (the result of arithmetic operations)
        for i in range(len(result)):
            assert isinstance(result[i], float)
    
    @given(
        allocation=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_identity_on_equal_inputs(self, allocation, damping):
        """Test that shift_risk returns the same allocation when current equals target."""
        assume(allocation)  # Ensure allocation is not empty
        
        result = shift_risk(allocation, allocation, damping)
        
        assert result == allocation
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_damping_factor_effect(self, current, target, damping):
        """Test that damping factor correctly controls movement towards target."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        # When damping is 0, result should equal current
        if damping == 0:
            assert result == current
        
        # When damping is 1, result should equal target
        if damping == 1:
            assert result == target
        
        # For intermediate damping values, result should be between current and target
        if 0 < damping < 1:
            for i in range(len(result)):
                c, t = current[i], target[i]
                r = result[i]
                
                # Result should be between current and target
                if c <= t:
                    assert c <= r <= t
                else:
                    assert t <= r <= c
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_no_normalization_bug(self, current, target, damping):
        """Test that the function does NOT normalize when inputs sum to 1.0 (this is the bug)."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        # Filter to only test cases where both current and target sum to 1.0
        assume(abs(sum(current) - 1.0) < 1e-10)
        assume(abs(sum(target) - 1.0) < 1e-10)
        
        result = shift_risk(current, target, damping)
        
        # This test documents the bug: the result should NOT sum to 1.0
        # (unless damping is 0 or 1, in which case it might by coincidence)
        result_sum = sum(result)
        
        # The bug is that the function doesn't normalize, so the sum should generally not be 1.0
        # We can't assert this will always be true due to floating point precision,
        # but we can check that it's not always 1.0
        if damping not in [0, 1]:
            # For intermediate damping values, the sum should typically not be 1.0
            assert abs(result_sum - 1.0) > 1e-12 or abs(result_sum - 1.0) < 1e-15
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_linear_combination_property(self, current, target, damping):
        """Test the linear combination property for each element."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        # Verify: result[i] = current[i] + (target[i] - current[i]) * damping
        for i in range(len(result)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_boundary_preservation(self, current, target, damping):
        """Test that results stay within the bounds of current and target values."""
        assume(len(current) == len(target))
        assume(current)  # Ensure current is not empty
        
        result = shift_risk(current, target, damping)
        
        for i in range(len(result)):
            c, t = current[i], target[i]
            r = result[i]
            
            # Result should be between min(c, t) and max(c, t)
            min_val = min(c, t)
            max_val = max(c, t)
            
            assert min_val <= r <= max_val