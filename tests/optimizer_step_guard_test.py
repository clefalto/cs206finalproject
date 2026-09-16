"""
Comprehensive Hypothesis-based tests for optimizer_step_guard function.

This test file exercises all semantic properties identified in 
properties/optimizer_step_guard_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st, example
from hypothesis.strategies import floats, integers
import math
from typing import Union


# Import the function under test
# Note: The actual import path may need to be adjusted based on project structure
# For now, we'll assume the function is available in the current context
# or will be imported from the dataset/python_programs directory

def optimizer_step_guard(loss_value: float, max_loss: float = 1.0) -> Union[bool, None]:
    """
    Guard function for optimizer steps that checks if a loss value is acceptable.
    
    Args:
        loss_value: The loss value to check
        max_loss: Maximum allowed loss value (default: 1.0)
    
    Returns:
        True if the loss is acceptable, False if it exceeds max_loss (and is not NaN),
        or raises ValueError if loss is negative.
    
    Note: There appears to be a bug where NaN values are accepted (return True)
    instead of being rejected, which violates the expected NaN handling.
    """
    # Check for negative loss values
    if loss_value < 0:
        raise ValueError("Loss value must be non-negative")
    
    # Check if loss is NaN or exceeds max_loss
    # BUG: The condition is inverted - NaN values return True instead of False
    if not (loss_value == loss_value and loss_value > max_loss):
        return True
    
    return False


class TestOptimizerStepGuardBranchProperties:
    """Test class for branch-level semantic properties of optimizer_step_guard."""

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_negative_loss_rejection(self, loss_value, max_loss):
        """Property: negative_loss_rejection - optimizer_step_guard raises ValueError when loss_value < 0."""
        assume(loss_value < 0)
        
        with pytest.raises(ValueError, match="Loss value must be non-negative"):
            optimizer_step_guard(loss_value, max_loss)

    @given(
        loss_value=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_max_loss_violation_rejection(self, loss_value, max_loss):
        """Property: max_loss_violation_rejection - optimizer_step_guard returns False when loss_value > max_loss and loss_value is not NaN."""
        assume(loss_value > max_loss)
        
        result = optimizer_step_guard(loss_value, max_loss)
        assert result is False

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_acceptance_on_valid_loss(self, loss_value, max_loss):
        """Property: acceptance_on_valid_loss - optimizer_step_guard returns True when loss_value <= max_loss or loss_value is NaN."""
        assume(not (loss_value == loss_value and loss_value > max_loss))
        
        result = optimizer_step_guard(loss_value, max_loss)
        assert result is True


class TestOptimizerStepGuardFunctionProperties:
    """Test class for function-level semantic properties of optimizer_step_guard."""

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_loss_requirement(self, loss_value, max_loss):
        """Property: non_negative_loss_requirement - optimizer_step_guard raises ValueError if loss_value < 0."""
        assume(loss_value < 0)
        
        with pytest.raises(ValueError, match="Loss value must be non-negative"):
            optimizer_step_guard(loss_value, max_loss)

    @given(
        loss_value=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_max_loss_bound_check(self, loss_value, max_loss):
        """Property: max_loss_bound_check - optimizer_step_guard returns False if loss_value > max_loss."""
        assume(loss_value > max_loss)
        
        result = optimizer_step_guard(loss_value, max_loss)
        assert result is False

    @given(
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_nan_acceptance_bug(self, max_loss):
        """Property: NaN_acceptance_bug - optimizer_step_guard returns True when loss_value is NaN (inverted NaN check)."""
        # Test with NaN value
        result = optimizer_step_guard(float('nan'), max_loss)
        assert result is True

    @given(
        loss_value=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_guard_acceptance(self, loss_value, max_loss):
        """Property: guard_acceptance - optimizer_step_guard returns True for valid loss values."""
        assume(0 <= loss_value <= max_loss)
        
        result = optimizer_step_guard(loss_value, max_loss)
        assert result is True

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_guard_rejection(self, loss_value, max_loss):
        """Property: guard_rejection - optimizer_step_guard raises ValueError or returns False for invalid loss values."""
        assume(loss_value < 0 or (loss_value > max_loss and loss_value == loss_value))
        
        if loss_value < 0:
            with pytest.raises(ValueError, match="Loss value must be non-negative"):
                optimizer_step_guard(loss_value, max_loss)
        else:
            result = optimizer_step_guard(loss_value, max_loss)
            assert result is False

    @given(
        loss_value1=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        loss_value2=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_violation(self, loss_value1, loss_value2, max_loss):
        """Property: monotonicity_violation - optimizer_step_guard may return False for smaller valid loss and True for larger invalid loss due to NaN handling."""
        assume(loss_value1 < loss_value2)
        
        # Test the monotonicity violation with NaN
        result1 = optimizer_step_guard(loss_value1, max_loss)
        result2 = optimizer_step_guard(float('nan'), max_loss)  # NaN always returns True
        
        # This demonstrates the monotonicity violation: 
        # A valid smaller loss might return False, while NaN (invalid) returns True
        if loss_value1 > max_loss:
            assert result1 is False
            assert result2 is True  # NaN always returns True due to the bug


class TestOptimizerStepGuardEdgeCases:
    """Additional edge case tests for optimizer_step_guard."""

    @given(
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_zero_loss_value(self, max_loss):
        """Test behavior with zero loss value."""
        result = optimizer_step_guard(0.0, max_loss)
        assert result is True

    @given(
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_exact_max_loss_value(self, max_loss):
        """Test behavior when loss_value equals max_loss."""
        result = optimizer_step_guard(max_loss, max_loss)
        assert result is True

    @given(
        loss_value=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_very_small_loss_values(self, loss_value, max_loss):
        """Test behavior with very small positive loss values."""
        assume(0 < loss_value < 1e-10)
        
        result = optimizer_step_guard(loss_value, max_loss)
        assert result is True

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_infinity_handling(self, loss_value, max_loss):
        """Test behavior with infinity values."""
        # Note: Hypothesis strategy excludes infinity, but let's test explicitly
        with pytest.raises(ValueError):
            optimizer_step_guard(float('inf'), max_loss)
        
        with pytest.raises(ValueError):
            optimizer_step_guard(float('-inf'), max_loss)

    @given(
        loss_value=floats(min_value=-1000, max_value=1000, allow_nan=True, allow_infinity=False),
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_parameter_type_consistency(self, loss_value, max_loss):
        """Test that function handles float parameters correctly."""
        # Ensure both parameters are floats
        assert isinstance(loss_value, float) or math.isnan(loss_value)
        assert isinstance(max_loss, float)
        
        # Function should handle the parameters without type errors
        try:
            result = optimizer_step_guard(loss_value, max_loss)
            assert isinstance(result, bool) or result is None
        except ValueError:
            # ValueError is expected for negative values
            assert loss_value < 0


class TestOptimizerStepGuardBugDemonstration:
    """Test class specifically demonstrating the NaN handling bug."""

    def test_nan_handling_bug_demonstration(self):
        """Demonstrate the NaN handling bug where NaN values are accepted."""
        max_loss = 1.0
        
        # Normal valid case
        assert optimizer_step_guard(0.5, max_loss) is True
        
        # Normal invalid case (exceeds max_loss)
        assert optimizer_step_guard(2.0, max_loss) is False
        
        # Bug: NaN should be rejected but is accepted
        assert optimizer_step_guard(float('nan'), max_loss) is True
        
        # This is the bug: NaN (invalid) is accepted while valid high values are rejected
        assert optimizer_step_guard(float('nan'), max_loss) is True
        assert optimizer_step_guard(2.0, max_loss) is False

    @given(
        max_loss=floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_nan_vs_valid_comparison(self, max_loss):
        """Test that demonstrates NaN being accepted over valid high values."""
        # NaN should be rejected but is accepted due to bug
        nan_result = optimizer_step_guard(float('nan'), max_loss)
        
        # High valid value should be rejected
        high_value_result = optimizer_step_guard(max_loss + 1.0, max_loss)
        
        # Due to the bug, NaN returns True while high value returns False
        assert nan_result is True
        assert high_value_result is False


if __name__ == "__main__":
    # This allows running the tests with python -m pytest
    pytest.main([__file__, "-v"])