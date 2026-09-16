import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, tuples
import math

# Import the function under test
# Note: The actual function implementation should be imported from the source code
# For now, we'll define a placeholder that matches the expected behavior
def adjust_portfolio(current, target, damping=0.1):
    """
    Adjust portfolio using linear interpolation with damping factor.
    
    Args:
        current: Current portfolio allocation list
        target: Target portfolio allocation list  
        damping: Damping factor (0.0 to 1.0)
    
    Returns:
        Adjusted portfolio allocation list
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    
    if not current:
        raise ValueError("empty allocation")
    
    result = []
    for i in range(len(current)):
        new_value = current[i] + (target[i] - current[i]) * damping
        result.append(new_value)
    
    return result


class TestAdjustPortfolio:
    """Test suite for adjust_portfolio function using Hypothesis."""

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when lengths are equal."""
        assume(len(current) == len(target))
        result = adjust_portfolio(current, target, damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function is defined for non-empty inputs."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # This test verifies the function doesn't crash on valid non-empty inputs
        result = adjust_portfolio(current, target, damping)
        assert result is not None
        assert isinstance(result, list)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_damping_adjustment(self, current, target, damping):
        """Test that damping adjustment formula is correctly applied."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = adjust_portfolio(current, target, damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_drifting_totals(self, current, target, damping):
        """Test that sum may not equal original sum (drifting totals)."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = adjust_portfolio(current, target, damping)
        original_sum = sum(current)
        result_sum = sum(result)
        
        # The sum should generally not be preserved (unless damping=0 or current=target)
        # This test verifies the "drifting totals" property
        if damping != 0.0 and current != target:
            assert not math.isclose(original_sum, result_sum, rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_identity_on_same(self, current, target, damping):
        """Test that identical inputs return identical outputs."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(current == target)
        
        result = adjust_portfolio(current, target, damping)
        
        for i in range(len(current)):
            assert math.isclose(result[i], current[i], rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that linear interpolation formula is correctly applied."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = adjust_portfolio(current, target, damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False)),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            adjust_portfolio(current, target, damping)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False)),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, current, target, damping):
        """Test that empty current allocation raises ValueError."""
        assume(not current)
        
        with pytest.raises(ValueError, match="empty allocation"):
            adjust_portfolio(current, target, damping)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @example(current=[0.0], target=[1.0], damping=0.5)  # Edge case with single element
    @example(current=[0.5, 0.5], target=[1.0, 0.0], damping=0.1)  # Simple interpolation
    @example(current=[0.1, 0.2, 0.7], target=[0.3, 0.4, 0.3], damping=0.2)  # Multi-element
    def test_edge_cases(self, current, target, damping):
        """Test various edge cases and specific examples."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Test that the function works for all valid inputs
        result = adjust_portfolio(current, target, damping)
        
        # Verify basic properties
        assert len(result) == len(current)
        assert all(isinstance(x, (int, float)) for x in result)
        
        # Verify interpolation bounds
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val