#!/usr/bin/env python3
"""
Hypothesis-based property tests for shift_weight function.

This test file exercises all semantic properties identified in
properties/shift_weight_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, tuples
import sys
import os

# Add the current directory to Python path to import shift_weight
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function under test
# Note: The actual shift_weight function should be imported from its module
# For now, we'll define a placeholder that raises NotImplementedError
# This allows the test structure to be validated without the actual implementation
def shift_weight(current, target, damping=0.1):
    """
    Placeholder implementation of shift_weight function.
    
    This should be replaced with the actual implementation.
    """
    raise NotImplementedError("shift_weight function not implemented")


class TestShiftWeightProperties:
    """Test class for shift_weight semantic properties."""
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            shift_weight(current, target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=0),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, current, target, damping):
        """Test that empty allocation raises ValueError."""
        assume(not current)
        
        with pytest.raises(ValueError, match="empty allocation"):
            shift_weight(current, target, damping)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when shapes are consistent."""
        assume(len(current) == len(target))
        
        result = shift_weight(current, target, damping)
        assert len(result) == len(current)
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_damping_interpolation(self, current, target, damping):
        """Test that damping interpolation formula is correct."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = shift_weight(current, target, damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, \
                f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_identity_on_same(self, current, damping):
        """Test that shift_weight(current, current) == current."""
        assume(current != [])
        
        result = shift_weight(current, current, damping)
        assert result == current
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test linear interpolation property."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = shift_weight(current, target, damping)
        
        # Check that result[i] = current[i] + damping * (target[i] - current[i])
        for i in range(len(current)):
            expected = current[i] + damping * (target[i] - current[i])
            assert abs(result[i] - expected) < 1e-10, \
                f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_bounded_interpolation(self, current, target, damping):
        """Test that interpolation is bounded between current and target values."""
        assume(len(current) == len(target))
        assume(current != [])
        assume(0 <= damping <= 1)
        
        result = shift_weight(current, target, damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val, \
                f"Index {i}: result {result[i]} not bounded by [{min_val}, {max_val}]"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping1=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        damping2=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_interpolation(self, current, target, damping1, damping2):
        """Test that interpolation is monotonic in damping when current[i] <= target[i]."""
        assume(len(current) == len(target))
        assume(current != [])
        assume(0 <= damping1 <= damping2 <= 1)
        
        # Only test indices where current[i] <= target[i]
        test_indices = [i for i in range(len(current)) if current[i] <= target[i]]
        assume(len(test_indices) > 0)
        
        result1 = shift_weight(current, target, damping1)
        result2 = shift_weight(current, target, damping2)
        
        for i in test_indices:
            assert result1[i] <= result2[i], \
                f"Index {i}: monotonicity violated: {result1[i]} > {result2[i]}"
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_zero_damping_identity(self, current, target):
        """Test that zero damping returns current values."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = shift_weight(current, target, damping=0.0)
        assert result == current
    
    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_full_damping_target(self, current, target):
        """Test that full damping (damping=1) returns target values."""
        assume(len(current) == len(target))
        assume(current != [])
        
        result = shift_weight(current, target, damping=1.0)
        assert result == target


if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main([__file__, "-v"])