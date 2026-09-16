import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math

# Import the shift_demand function from the main module
# Note: This assumes the shift_demand function is available in the main module
# If it's in a different module, adjust the import accordingly
from dataset.python_programs import shift_demand


class TestShiftDemandProperties:
    """Test class for shift_demand function using Hypothesis testing framework."""
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            shift_demand(current, target, damping)
    
    @given(
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, target, damping):
        """Test that empty current allocation raises ValueError."""
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            shift_demand(current, target, damping)
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_damping_adjustment(self, current, target, damping):
        """Test that damping adjustment formula is applied correctly."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, damping)
        
        # Verify the formula: adjusted[i] = current[i] + (target[i] - current[i]) * damping
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when shapes are consistent."""
        assume(len(current) == len(target))
        
        result = shift_demand(current, target, damping)
        assert len(result) == len(current), f"Output length {len(result)} != input length {len(current)}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function returns non-None for non-empty input."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, damping)
        assert result is not None, "Function should return a non-None result for non-empty input"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_damping_interpolation(self, current, target, damping):
        """Test that damping interpolation formula is applied correctly for all elements."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, damping)
        
        # Verify interpolation formula for all elements
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_identity_when_damping_zero(self, current, target):
        """Test that when damping is 0, result equals current."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, 0.0)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Index {i}: expected {current[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_target_when_damping_one(self, current, target):
        """Test that when damping is 1, result equals target."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, 1.0)
        
        for i in range(len(target)):
            assert abs(result[i] - target[i]) < 1e-10, f"Index {i}: expected {target[i]}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that linear interpolation formula is applied correctly."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, damping)
        
        # Verify linear interpolation: result = current + damping * (target - current)
        for i in range(len(current)):
            expected = current[i] + damping * (target[i] - current[i])
            assert abs(result[i] - expected) < 1e-10, f"Index {i}: expected {expected}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_preserves_non_negativity(self, current, target, damping):
        """Test that non-negative inputs produce non-negative outputs."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(all(c >= 0 for c in current))
        assume(all(t >= 0 for t in target))
        
        result = shift_demand(current, target, damping)
        
        for i in range(len(result)):
            assert result[i] >= 0, f"Index {i}: expected non-negative value, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_bounded_adjustment(self, current, target, damping):
        """Test that adjusted values are bounded between current and target values."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = shift_demand(current, target, damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val, f"Index {i}: expected value between {min_val} and {max_val}, got {result[i]}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_sum_preservation_bug(self, current, target, damping):
        """Test that sum is NOT preserved (demonstrating the bug)."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(sum(current) == sum(target))
        
        result = shift_demand(current, target, damping)
        
        # This test demonstrates the bug: sum should be preserved but isn't
        original_sum = sum(current)
        result_sum = sum(result)
        
        # The bug: result_sum != original_sum (this should pass, demonstrating the bug)
        assert abs(result_sum - original_sum) > 1e-10, f"Sum should not be preserved (bug): original={original_sum}, result={result_sum}"
    
    @given(
        current=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2),
        target=lists(floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, current, target, damping):
        """Test that monotonicity is preserved in the adjustment."""
        assume(len(current) == len(target))
        assume(len(current) > 1)
        
        result = shift_demand(current, target, damping)
        
        # Check all pairs for monotonicity preservation
        for i in range(len(current)):
            for j in range(len(current)):
                if i != j:
                    # If current[i] <= current[j] and target[i] <= target[j], then result[i] <= result[j]
                    if current[i] <= current[j] and target[i] <= target[j]:
                        assert result[i] <= result[j], f"Monotonicity violated: current[{i}]={current[i]} <= current[{j}]={current[j]} and target[{i}]={target[i]} <= target[{j}]={target[j]}, but result[{i}]={result[i]} > result[{j}]={result[j]}"