import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, tuples
import math

# Import the function under test
# Note: The actual function implementation should be imported from the source code
# For now, we'll define a placeholder that matches the expected behavior
def probability_rebalance(current, target, damping=0.1):
    """
    Rebalance probabilities using linear interpolation with damping factor.
    
    Args:
        current: Current probability distribution list
        target: Target probability distribution list  
        damping: Damping factor (0.0 to 1.0)
    
    Returns:
        Adjusted probability distribution list
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


class TestProbabilityRebalance:
    """Test suite for probability_rebalance function using Hypothesis."""

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_consistency(self, current, target, damping):
        """Test that output shape matches input shape when lengths are equal."""
        assume(len(current) == len(target))
        result = probability_rebalance(current, target, damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_non_empty_input(self, current, target, damping):
        """Test that function returns non-None result for non-empty input."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        result = probability_rebalance(current, target, damping)
        assert result is not None

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that linear interpolation formula is correctly applied."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        result = probability_rebalance(current, target, damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_factor_zero(self, current, target):
        """Test that damping=0 returns current allocation unchanged."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        result = probability_rebalance(current, target, damping=0.0)
        
        for i in range(len(current)):
            assert math.isclose(result[i], current[i], rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_damping_factor_one(self, current, target):
        """Test that damping=1 returns target allocation."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        result = probability_rebalance(current, target, damping=1.0)
        
        for i in range(len(current)):
            assert math.isclose(result[i], target[i], rel_tol=1e-9)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_bounded_interpolation(self, current, target, damping):
        """Test that interpolation values are bounded by current and target."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        assume(0 <= damping <= 1)
        result = probability_rebalance(current, target, damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_sum_preservation_violation(self, current, target, damping):
        """Test that sum is not forced to 1 when both inputs sum to 1 (BUG)."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        assume(len(current) > 0)
        
        # Create probability distributions that sum to 1
        current_sum = sum(current)
        target_sum = sum(target)
        
        assume(current_sum != 0 and target_sum != 0)
        
        # Normalize to sum to 1
        current_norm = [x / current_sum for x in current]
        target_norm = [x / target_sum for x in target]
        
        result = probability_rebalance(current_norm, target_norm, damping)
        result_sum = sum(result)
        
        # The result should NOT necessarily sum to 1
        # This test verifies the "sum preservation violation" property
        # by ensuring the function doesn't artificially force the sum to 1
        assert not math.isclose(result_sum, 1.0, rel_tol=1e-9) or len(current) == 1

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, current, target, damping):
        """Test that interpolation preserves monotonicity bounds."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        assume(0 <= damping <= 1)
        result = probability_rebalance(current, target, damping)
        
        for i in range(len(current)):
            if current[i] <= target[i]:
                assert result[i] >= current[i]
            else:
                assert result[i] <= current[i]

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.9, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_target_convergence(self, current, target, damping):
        """Test that high damping values approach target distribution."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        result = probability_rebalance(current, target, damping)
        
        # With high damping, result should be close to target
        for i in range(len(current)):
            assert math.isclose(result[i], target[i], rel_tol=0.1)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """Test that shape mismatch raises ValueError."""
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            probability_rebalance(current, target, damping)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False)),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_empty_allocation_error(self, current, target, damping):
        """Test that empty current allocation raises ValueError."""
        assume(not current)
        
        with pytest.raises(ValueError, match="empty allocation"):
            probability_rebalance(current, target, damping)

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @example(current=[0.0], target=[1.0], damping=0.5)  # Edge case with single element
    @example(current=[0.5, 0.5], target=[1.0, 0.0], damping=0.1)  # Simple interpolation
    @example(current=[0.1, 0.2, 0.7], target=[0.3, 0.4, 0.3], damping=0.2)  # Multi-element
    @example(current=[0.25, 0.25, 0.25, 0.25], target=[0.5, 0.3, 0.1, 0.1], damping=0.3)  # Four elements
    def test_edge_cases(self, current, target, damping):
        """Test various edge cases and specific examples."""
        assume(len(current) == len(target))
        assume(len(current) > 0)
        assume(current)  # Non-empty current allocation
        
        # Test that the function works for all valid inputs
        result = probability_rebalance(current, target, damping)
        
        # Verify basic properties
        assert len(result) == len(current)
        assert all(isinstance(x, (int, float)) for x in result)
        
        # Verify interpolation bounds
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val

    @given(
        current=lists(floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False), min_size=1),
        target=lists(floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False), min_size=1),
        damping=floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_probability_bounds(self, current, target, damping):
        """Test that probability values remain within [0, 1] bounds when inputs are in bounds."""
        assume(len(current) == len(target))
        assume(current)  # Non-empty current allocation
        assume(0 <= damping <= 1)
        
        # Ensure inputs are valid probabilities (between 0 and 1)
        assume(all(0 <= x <= 1 for x in current))
        assume(all(0 <= x <= 1 for x in target))
        
        result = probability_rebalance(current, target, damping)
        
        # Verify all results are within probability bounds
        for i in range(len(result)):
            assert 0 <= result[i] <= 1, f"Result {result[i]} at index {i} is outside [0, 1] bounds"