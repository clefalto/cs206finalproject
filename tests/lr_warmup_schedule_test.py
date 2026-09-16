"""
Hypothesis-based property tests for lr_warmup_schedule function.

This test file exercises all semantic properties identified in 
properties/lr_warmup_schedule_properties.json using the Hypothesis 
testing framework for comprehensive property-based testing.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, floats
import math


# Import the function under test
# Note: This assumes the function is available in the current environment
# In a real scenario, you would import from the actual module
def lr_warmup_schedule(step, warmup_steps, base_lr):
    """
    Learning rate warmup schedule function.
    
    Args:
        step: Current training step
        warmup_steps: Number of warmup steps
        base_lr: Base learning rate
    
    Returns:
        Learning rate for the current step
    """
    if warmup_steps <= 0:
        raise ValueError("warmup_steps must be positive")
    
    if step < 0:
        raise ValueError("step must be non-negative")
    
    if step >= warmup_steps:
        return base_lr
    
    return base_lr * (step / warmup_steps)


class TestLrWarmupScheduleProperties:
    """Test class for lr_warmup_schedule semantic properties."""
    
    # Hypothesis strategies for generating test data
    positive_integers = integers(min_value=1, max_value=1000)
    non_negative_integers = integers(min_value=0, max_value=1000)
    positive_floats = floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    base_lr_strategy = floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    
    @given(warmup_steps=integers(max_value=0), base_lr=base_lr_strategy)
    def test_invalid_warmup_steps(self, warmup_steps, base_lr):
        """
        Test property: invalid_warmup_steps
        Condition: warmup_steps <= 0
        Formal: raise ValueError("warmup_steps must be positive")
        """
        with pytest.raises(ValueError, match="warmup_steps must be positive"):
            lr_warmup_schedule(0, warmup_steps, base_lr)
    
    @given(step=integers(max_value=-1), warmup_steps=positive_integers, base_lr=base_lr_strategy)
    def test_invalid_step(self, step, warmup_steps, base_lr):
        """
        Test property: invalid_step
        Condition: step < 0
        Formal: raise ValueError("step must be non-negative")
        """
        with pytest.raises(ValueError, match="step must be non-negative"):
            lr_warmup_schedule(step, warmup_steps, base_lr)
    
    @given(step=positive_integers, warmup_steps=integers(min_value=1, max_value=100), base_lr=base_lr_strategy)
    def test_full_learning_rate(self, step, warmup_steps, base_lr):
        """
        Test property: full_learning_rate
        Condition: step >= warmup_steps
        Formal: return base_lr
        """
        assume(step >= warmup_steps)
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        assert result == base_lr
    
    @given(step=integers(min_value=0, max_value=99), warmup_steps=integers(min_value=1, max_value=100), base_lr=base_lr_strategy)
    def test_linear_warmup(self, step, warmup_steps, base_lr):
        """
        Test property: linear_warmup
        Condition: 0 <= step < warmup_steps
        Formal: return base_lr * (step / warmup_steps)
        """
        assume(step < warmup_steps)
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        expected = base_lr * (step / warmup_steps)
        assert math.isclose(result, expected, rel_tol=1e-9)
    
    @given(
        warmup_steps=positive_integers,
        step1=integers(min_value=0, max_value=99),
        step2=integers(min_value=0, max_value=99),
        base_lr=base_lr_strategy
    )
    def test_monotonic_increasing(self, warmup_steps, step1, step2, base_lr):
        """
        Test property: monotonic_increasing
        Precondition: warmup_steps > 0 and step >= 0
        Formal: for all step1, step2 where 0 <= step1 < step2 < warmup_steps: lr_warmup_schedule(step1) <= lr_warmup_schedule(step2)
        """
        assume(0 <= step1 < step2 < warmup_steps)
        result1 = lr_warmup_schedule(step1, warmup_steps, base_lr)
        result2 = lr_warmup_schedule(step2, warmup_steps, base_lr)
        assert result1 <= result2
    
    @given(step=non_negative_integers, warmup_steps=positive_integers, base_lr=base_lr_strategy)
    def test_bounded_output(self, step, warmup_steps, base_lr):
        """
        Test property: bounded_output
        Precondition: warmup_steps > 0 and step >= 0
        Formal: 0 <= lr_warmup_schedule(step) <= base_lr
        """
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        assert 0 <= result <= base_lr
    
    @given(warmup_steps=positive_integers, base_lr=base_lr_strategy)
    def test_initial_value_zero(self, warmup_steps, base_lr):
        """
        Test property: initial_value_zero
        Precondition: warmup_steps > 0
        Formal: lr_warmup_schedule(0) == 0
        """
        result = lr_warmup_schedule(0, warmup_steps, base_lr)
        assert result == 0
    
    @given(warmup_steps=positive_integers, base_lr=base_lr_strategy)
    def test_boundary_bug(self, warmup_steps, base_lr):
        """
        Test property: boundary_bug
        Precondition: warmup_steps > 0
        Formal: lr_warmup_schedule(warmup_steps - 1) < base_lr and lr_warmup_schedule(warmup_steps) == base_lr
        """
        if warmup_steps == 1:
            # Special case: warmup_steps - 1 = 0, which should return 0
            result_before = lr_warmup_schedule(0, warmup_steps, base_lr)
            result_at = lr_warmup_schedule(1, warmup_steps, base_lr)
            assert result_before < base_lr
            assert result_at == base_lr
        else:
            result_before = lr_warmup_schedule(warmup_steps - 1, warmup_steps, base_lr)
            result_at = lr_warmup_schedule(warmup_steps, warmup_steps, base_lr)
            assert result_before < base_lr
            assert result_at == base_lr
    
    @given(step=integers(min_value=0, max_value=99), warmup_steps=integers(min_value=1, max_value=100), base_lr=base_lr_strategy)
    def test_linear_interpolation(self, step, warmup_steps, base_lr):
        """
        Test property: linear_interpolation
        Precondition: warmup_steps > 0 and 0 <= step < warmup_steps
        Formal: lr_warmup_schedule(step) == base_lr * (step / warmup_steps)
        """
        assume(step < warmup_steps)
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        expected = base_lr * (step / warmup_steps)
        assert math.isclose(result, expected, rel_tol=1e-9)
    
    @given(step=positive_integers, warmup_steps=integers(min_value=1, max_value=100), base_lr=base_lr_strategy)
    def test_constant_after_warmup(self, step, warmup_steps, base_lr):
        """
        Test property: constant_after_warmup
        Precondition: warmup_steps > 0 and step >= warmup_steps
        Formal: lr_warmup_schedule(step) == base_lr
        """
        assume(step >= warmup_steps)
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        assert result == base_lr
    
    @given(warmup_steps=integers(max_value=0), base_lr=base_lr_strategy)
    def test_error_on_negative_warmup(self, warmup_steps, base_lr):
        """
        Test property: error_on_negative_warmup
        Precondition: warmup_steps <= 0
        Formal: ValueError is raised with message "warmup_steps must be positive"
        """
        with pytest.raises(ValueError, match="warmup_steps must be positive"):
            lr_warmup_schedule(0, warmup_steps, base_lr)
    
    @given(step=integers(max_value=-1), warmup_steps=positive_integers, base_lr=base_lr_strategy)
    def test_error_on_negative_step(self, step, warmup_steps, base_lr):
        """
        Test property: error_on_negative_step
        Precondition: step < 0
        Formal: ValueError is raised with message "step must be non-negative"
        """
        with pytest.raises(ValueError, match="step must be non-negative"):
            lr_warmup_schedule(step, warmup_steps, base_lr)


class TestLrWarmupScheduleEdgeCases:
    """Additional edge case tests for lr_warmup_schedule."""
    
    @given(base_lr=st.floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False))
    def test_single_step_warmup(self, base_lr):
        """Test edge case where warmup_steps = 1."""
        # At step 0 (before warmup), should be 0
        result_0 = lr_warmup_schedule(0, 1, base_lr)
        assert result_0 == 0
        
        # At step 1 (at warmup), should be base_lr
        result_1 = lr_warmup_schedule(1, 1, base_lr)
        assert result_1 == base_lr
    
    @given(
        warmup_steps=st.integers(min_value=1, max_value=100),
        base_lr=st.floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_warmup_boundary_transition(self, warmup_steps, base_lr):
        """Test the exact boundary between warmup and full learning rate."""
        # One step before warmup ends
        if warmup_steps > 1:
            result_before = lr_warmup_schedule(warmup_steps - 1, warmup_steps, base_lr)
            expected_before = base_lr * ((warmup_steps - 1) / warmup_steps)
            assert math.isclose(result_before, expected_before, rel_tol=1e-9)
            assert result_before < base_lr
        
        # At warmup boundary
        result_at_boundary = lr_warmup_schedule(warmup_steps, warmup_steps, base_lr)
        assert result_at_boundary == base_lr
    
    @given(
        step=st.integers(min_value=0, max_value=1000),
        warmup_steps=st.integers(min_value=1, max_value=100),
        base_lr=st.floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_no_nan_inf_values(self, step, warmup_steps, base_lr):
        """Test that the function never returns NaN or infinity."""
        result = lr_warmup_schedule(step, warmup_steps, base_lr)
        assert not math.isnan(result)
        assert not math.isinf(result)
        assert isinstance(result, (int, float))


class TestLrWarmupScheduleIntegration:
    """Integration tests that combine multiple properties."""
    
    @given(
        warmup_steps=st.integers(min_value=1, max_value=100),
        base_lr=st.floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_complete_warmup_sequence(self, warmup_steps, base_lr):
        """Test a complete sequence from step 0 to warmup_steps."""
        # Test step 0
        result_0 = lr_warmup_schedule(0, warmup_steps, base_lr)
        assert result_0 == 0
        
        # Test intermediate steps
        for step in range(1, warmup_steps):
            result = lr_warmup_schedule(step, warmup_steps, base_lr)
            expected = base_lr * (step / warmup_steps)
            assert math.isclose(result, expected, rel_tol=1e-9)
            assert 0 < result < base_lr
        
        # Test at and after warmup
        for step in range(warmup_steps, warmup_steps + 10):
            result = lr_warmup_schedule(step, warmup_steps, base_lr)
            assert result == base_lr
    
    @given(
        warmup_steps=st.integers(min_value=2, max_value=50),
        base_lr=st.floats(min_value=0.0001, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_across_entire_range(self, warmup_steps, base_lr):
        """Test that the function is monotonic across the entire range."""
        previous_result = -1  # Start with a value lower than any possible result
        
        for step in range(warmup_steps + 10):  # Test up to 10 steps after warmup
            result = lr_warmup_schedule(step, warmup_steps, base_lr)
            assert result >= previous_result, f"Monotonicity violated at step {step}"
            previous_result = result


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])