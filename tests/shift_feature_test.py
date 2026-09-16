"""
Hypothesis tests for shift_feature function semantic properties.
Tests all properties identified in shift_feature_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, tuples
import math


def shift_feature(current, target, damping=0.5):
    """
    Shift feature values from current towards target using damping factor.
    
    Args:
        current: List of current feature values
        target: List of target feature values  
        damping: Damping factor between 0 and 1
    
    Returns:
        Adjusted feature values
    
    Raises:
        ValueError: If shape mismatch or empty allocation
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    
    if not current:
        raise ValueError("empty allocation")
    
    adjusted = [c + (t - c) * damping for c, t in zip(current, target)]
    return adjusted


class TestShiftFeatureProperties:
    """Test class for shift_feature semantic properties."""
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test shape mismatch error branch."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            shift_feature(current, target, damping)
    
    @given(
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_empty_allocation_error(self, target, damping):
        """Test empty allocation error branch."""
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            shift_feature(current, target, damping)
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_damping_adjustment(self, current, target, damping):
        """Test damping adjustment calculation."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty
        
        result = shift_feature(current, target, damping)
        
        # Verify the formula: adjusted[i] = current[i] + (target[i] - current[i]) * damping
        expected = [c + (t - c) * damping for c, t in zip(current, target)]
        
        for i, (actual, exp) in enumerate(zip(result, expected)):
            assert abs(actual - exp) < 1e-10, f"Index {i}: expected {exp}, got {actual}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test shape consistency property."""
        assume(len(current) == len(target))
        
        result = shift_feature(current, target, damping)
        assert len(result) == len(current)
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test non-empty input property."""
        assume(current)
        
        result = shift_feature(current, target, damping)
        assert result is not None
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_damping_interpolation(self, current, target, damping):
        """Test damping interpolation property."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping)
        
        # Verify interpolation formula for all elements
        for i, (c, t) in enumerate(zip(current, target)):
            expected = c + (t - c) * damping
            assert abs(result[i] - expected) < 1e-10
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_identity_when_damping_zero(self, current, target):
        """Test identity when damping is zero."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping=0.0)
        
        for i, (actual, expected) in enumerate(zip(result, current)):
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_target_when_damping_one(self, current, target):
        """Test target when damping is one."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping=1.0)
        
        for i, (actual, expected) in enumerate(zip(result, target)):
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test linear interpolation property."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping)
        
        # Verify linear interpolation: result = current + damping * (target - current)
        for i, (c, t, r) in enumerate(zip(current, target, result)):
            expected = c + damping * (t - c)
            assert abs(r - expected) < 1e-10, f"Index {i}: expected {expected}, got {r}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=0, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_preserves_non_negativity(self, current, target, damping):
        """Test preserves non-negativity property."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping)
        
        # All values should remain non-negative
        for i, value in enumerate(result):
            assert value >= -1e-10, f"Index {i}: expected non-negative, got {value}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_bounded_adjustment(self, current, target, damping):
        """Test bounded adjustment property."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping)
        
        # Each adjusted value should be between current and target
        for i, (c, t, r) in enumerate(zip(current, target, result)):
            min_val = min(c, t)
            max_val = max(c, t)
            assert min_val - 1e-10 <= r <= max_val + 1e-10, \
                f"Index {i}: expected between {min_val} and {max_val}, got {r}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_sum_preservation_bug(self, current, target, damping):
        """Test sum preservation bug (property that should fail)."""
        assume(len(current) == len(target))
        assume(current)
        assume(sum(current) == sum(target))
        assume(damping != 0)  # Only test when damping is not zero
        
        result = shift_feature(current, target, damping)
        
        # This should fail - the function doesn't preserve sum
        original_sum = sum(current)
        result_sum = sum(result)
        
        # The bug: sum is not preserved (unless damping is 0)
        if damping != 0:
            assert abs(original_sum - result_sum) > 1e-10, \
                f"Sum should not be preserved: original={original_sum}, result={result_sum}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=2, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=2, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_monotonicity_preservation(self, current, target, damping):
        """Test monotonicity preservation property."""
        assume(len(current) == len(target))
        assume(current)
        
        result = shift_feature(current, target, damping)
        
        # Check if monotonicity is preserved
        for i in range(len(current)):
            for j in range(len(current)):
                if i != j:
                    if current[i] <= current[j] and target[i] <= target[j]:
                        assert result[i] <= result[j] + 1e-10, \
                            f"Monotonicity violated: current[{i}]={current[i]} <= current[{j}]={current[j]}, " \
                            f"target[{i}]={target[i]} <= target[{j}]={target[j]}, " \
                            f"but result[{i}]={result[i]} > result[{j}]={result[j]}"
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_commutativity_bug(self, current, target, damping):
        """Test commutativity bug (property that should fail)."""
        assume(len(current) == len(target))
        assume(current)
        assume(damping != 0.5)  # Only test when damping is not 0.5
        
        result1 = shift_feature(current, target, damping)
        result2 = shift_feature(target, current, damping)
        
        # This should fail - the function is not commutative
        for i, (r1, r2) in enumerate(zip(result1, result2)):
            if abs(r1 - r2) > 1e-10:
                # Found a difference, which confirms the bug
                return
        
        # If we get here, the results were the same (unexpected for damping != 0.5)
        pytest.fail(f"Unexpected commutativity: damping={damping}, results were identical")
    
    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        intermediate=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        damping=floats(min_value=0, max_value=1)
    )
    def test_associativity_violation(self, current, intermediate, target, damping):
        """Test associativity violation (property that should fail)."""
        assume(len(current) == len(intermediate) == len(target))
        assume(current)
        assume(damping != 0)  # Only test when damping is not zero
        
        # First step: current -> intermediate
        step1 = shift_feature(current, intermediate, damping)
        
        # Second step: step1 -> target  
        result1 = shift_feature(step1, target, damping)
        
        # Direct: current -> target
        result2 = shift_feature(current, target, damping)
        
        # This should fail - associativity is violated
        differences = [abs(r1 - r2) for r1, r2 in zip(result1, result2)]
        
        # Check if there are any significant differences
        if any(diff > 1e-10 for diff in differences):
            # Found differences, which confirms the bug
            return
        
        # If we get here, the results were the same (unexpected for damping != 0)
        pytest.fail(f"Unexpected associativity: damping={damping}, results were identical")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])