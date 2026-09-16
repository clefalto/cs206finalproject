"""
Hypothesis-based tests for the realign_cache function semantic properties.

This test file exercises all semantic properties identified in 
properties/realign_cache_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, one_of

from dataset.python_programs.realign_cache import realign_cache


class TestRealignCacheSemanticProperties:
    """Test class for realign_cache semantic properties using Hypothesis."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """
        Test that realign_cache raises ValueError when len(current) != len(target).
        Property: shape_mismatch_error
        """
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            realign_cache(current, target, damping=damping)

    @given(
        target=lists(floats(min_value=-1000, max_value=1000), min_size=0, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_empty_allocation_error(self, target, damping):
        """
        Test that realign_cache raises ValueError when current is empty.
        Property: empty_allocation_error
        """
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            realign_cache(current, target, damping=damping)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_shape_consistency(self, current, target, damping):
        """
        Test that output length equals input length when shapes match.
        Property: shape_consistency
        Precondition: len(current) == len(target)
        """
        assume(len(current) == len(target))
        
        result = realign_cache(current, target, damping=damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_linear_interpolation(self, current, target, damping):
        """
        Test that realign_cache performs linear interpolation.
        Property: linear_interpolation
        Precondition: len(current) == len(target) and current != []
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_cache(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {expected}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_damping_factor_effect_zero(self, current, target):
        """
        Test that when damping=0, result equals current.
        Property: damping_factor_effect
        Precondition: len(current) == len(target) and current != []
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_cache(current, target, damping=0.0)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {current[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_damping_factor_effect_one(self, current, target):
        """
        Test that when damping=1, result equals target.
        Property: damping_factor_effect
        Precondition: len(current) == len(target) and current != []
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_cache(current, target, damping=1.0)
        
        for i in range(len(current)):
            assert abs(result[i] - target[i]) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {target[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_monotonicity_preservation(self, current, target, damping):
        """
        Test that result values are between current and target values.
        Property: monotonicity_preservation
        Precondition: len(current) == len(target) and current != [] and 0 <= damping <= 1
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_cache(current, target, damping=damping)
        
        for i in range(len(current)):
            min_val = min(current[i], target[i])
            max_val = max(current[i], target[i])
            assert min_val <= result[i] <= max_val, f"Value {result[i]} at index {i} not between {min_val} and {max_val}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_no_renormalization_bug(self, current, target, damping):
        """
        Test that the function does not renormalize (sum != 1 when inputs sum to 1).
        Property: no_renormalization_bug
        Precondition: len(current) == len(target) and current != []
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Create inputs that sum to 1
        if sum(current) != 0:
            current = [x / sum(current) for x in current]
        if sum(target) != 0:
            target = [x / sum(target) for x in target]
        
        assume(abs(sum(current) - 1.0) < 1e-10)
        assume(abs(sum(target) - 1.0) < 1e-10)
        
        result = realign_cache(current, target, damping=damping)
        result_sum = sum(result)
        
        # The bug is that it doesn't renormalize, so sum should NOT equal 1
        assert abs(result_sum - 1.0) > 1e-10, f"Result sum {result_sum} should not equal 1.0 (renormalization bug)"

    @given(damping=floats(min_value=0, max_value=1))
    def test_identity_on_empty(self, damping):
        """
        Test that empty lists raise ValueError.
        Property: identity_on_empty
        Precondition: current == []
        """
        current = []
        target = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            realign_cache(current, target, damping=damping)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50)
    )
    def test_metamorphic_relation(self, current, target):
        """
        Test metamorphic relation: applying realign_cache twice with damping=1 should be idempotent.
        Property: metamorphic_relation
        Precondition: len(current) == len(target) and current != []
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # First application
        intermediate = realign_cache(current, target, damping=1.0)
        
        # Second application
        final = realign_cache(intermediate, target, damping=1.0)
        
        # Should be equal when damping=1
        for i in range(len(current)):
            assert abs(final[i] - intermediate[i]) < 1e-10, f"Mismatch at index {i}: got {final[i]}, expected {intermediate[i]}"


class TestRealignCacheEdgeCases:
    """Additional edge case tests for realign_cache."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=-10, max_value=10)
    )
    def test_damping_out_of_bounds(self, current, target, damping):
        """
        Test behavior with damping values outside [0,1] range.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # This should still work but may produce values outside the [min, max] range
        result = realign_cache(current, target, damping=damping)
        
        assert len(result) == len(current)
        # Values might be outside the monotonicity range when damping is outside [0,1]

    @given(
        current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_no_nan_infinity(self, current, target, damping):
        """
        Test that function handles finite values correctly and doesn't produce NaN or infinity.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_cache(current, target, damping=damping)
        
        for val in result:
            assert not (val != val), f"Result contains NaN: {result}"
            assert abs(val) != float('inf'), f"Result contains infinity: {result}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_deterministic_behavior(self, current, target, damping):
        """
        Test that function produces deterministic results for same inputs.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result1 = realign_cache(current, target, damping=damping)
        result2 = realign_cache(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result1[i] - result2[i]) < 1e-10, f"Non-deterministic result at index {i}"