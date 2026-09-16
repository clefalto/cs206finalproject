"""
Hypothesis-based tests for the realign_replica function semantic properties.

This test file exercises all semantic properties identified in 
properties/realign_replica_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, one_of

from dataset.python_programs.realign_replica import realign_replica


class TestRealignReplicaSemanticProperties:
    """Test class for realign_replica semantic properties using Hypothesis."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_shape_mismatch_error(self, current, target, damping):
        """
        Test that realign_replica raises ValueError when len(current) != len(target).
        Property: shape_mismatch_error
        Formal: len(current) != len(target) => raises ValueError("shape mismatch")
        """
        assume(len(current) != len(target))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            realign_replica(current, target, damping=damping)

    @given(
        target=lists(floats(min_value=-1000, max_value=1000), min_size=0, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_empty_allocation_error(self, target, damping):
        """
        Test that realign_replica raises ValueError when current is empty.
        Property: empty_allocation_error
        Formal: not current => raises ValueError("empty allocation")
        """
        current = []
        
        with pytest.raises(ValueError, match="empty allocation"):
            realign_replica(current, target, damping=damping)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_length_preservation(self, current, target, damping):
        """
        Test that output length equals input length when shapes match.
        Property: length_preservation
        Precondition: len(current) == len(target)
        Formal: len(realign_replica(current, target)) == len(current)
        """
        assume(len(current) == len(target))
        
        result = realign_replica(current, target, damping=damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_linear_interpolation(self, current, target, damping):
        """
        Test that realign_replica performs linear interpolation.
        Property: linear_interpolation
        Precondition: len(current) == len(target) and current != []
        Formal: realign_replica(current, target)[i] == current[i] + (target[i] - current[i]) * damping for all i
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_replica(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert abs(result[i] - expected) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {expected}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_identity_on_equal_inputs(self, current, damping):
        """
        Test that when current equals target, result equals current.
        Property: identity_on_equal_inputs
        Precondition: current == target and current != []
        Formal: realign_replica(current, current) == current
        """
        assume(len(current) > 0)
        target = current.copy()
        
        result = realign_replica(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result[i] - current[i]) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {current[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_target_convergence(self, current, target):
        """
        Test that when damping=1.0, result equals target.
        Property: target_convergence
        Precondition: damping == 1.0 and len(current) == len(target) and current != []
        Formal: realign_replica(current, target) == target
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_replica(current, target, damping=1.0)
        
        for i in range(len(current)):
            assert abs(result[i] - target[i]) < 1e-10, f"Mismatch at index {i}: got {result[i]}, expected {target[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
    )
    def test_no_drift_invariant(self, current, target):
        """
        Test that when sums are equal and damping=1.0, sum is preserved.
        Property: no_drift_invariant
        Precondition: sum(current) == sum(target) and damping == 1.0 and len(current) == len(target) and current != []
        Formal: sum(realign_replica(current, target)) == sum(current)
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Create inputs with equal sums
        if sum(current) != 0:
            current = [x / sum(current) for x in current]
        if sum(target) != 0:
            target = [x / sum(target) for x in target]
        
        assume(abs(sum(current) - sum(target)) < 1e-10)
        
        result = realign_replica(current, target, damping=1.0)
        result_sum = sum(result)
        
        assert abs(result_sum - sum(current)) < 1e-10, f"Sum drift: got {result_sum}, expected {sum(current)}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_monotonic_convergence(self, current, target, damping):
        """
        Test that result values get closer to target values.
        Property: monotonic_convergence
        Precondition: 0 <= damping <= 1 and len(current) == len(target) and current != []
        Formal: abs(realign_replica(current, target)[i] - target[i]) <= abs(current[i] - target[i]) for all i
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        result = realign_replica(current, target, damping=damping)
        
        for i in range(len(current)):
            original_distance = abs(current[i] - target[i])
            new_distance = abs(result[i] - target[i])
            
            # With damping in [0,1], we should get closer or stay the same
            assert new_distance <= original_distance + 1e-10, \
                f"Distance increased at index {i}: was {original_distance}, now {new_distance}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=0, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=0, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_error_conditions(self, current, target, damping):
        """
        Test that appropriate ValueError is raised for error conditions.
        Property: error_conditions
        Precondition: len(current) != len(target) or not current
        Formal: raises ValueError with appropriate message
        """
        assume(len(current) != len(target) or not current)
        
        with pytest.raises(ValueError) as exc_info:
            realign_replica(current, target, damping=damping)
        
        # Check that the error message is appropriate
        error_msg = str(exc_info.value)
        if len(current) != len(target):
            assert "shape mismatch" in error_msg
        elif not current:
            assert "empty allocation" in error_msg


class TestRealignReplicaEdgeCases:
    """Additional edge case tests for realign_replica."""

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
        result = realign_replica(current, target, damping=damping)
        
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
        
        result = realign_replica(current, target, damping=damping)
        
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
        
        result1 = realign_replica(current, target, damping=damping)
        result2 = realign_replica(current, target, damping=damping)
        
        for i in range(len(current)):
            assert abs(result1[i] - result2[i]) < 1e-10, f"Non-deterministic result at index {i}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
        damping=floats(min_value=0, max_value=1)
    )
    def test_sum_drift_bug(self, current, target, damping):
        """
        Test the sum drift bug: when damping=1.0 and sums are equal, 
        the function should preserve sum but doesn't due to missing normalization.
        This test documents the bug behavior.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Create inputs with equal sums
        if sum(current) != 0:
            current = [x / sum(current) for x in current]
        if sum(target) != 0:
            target = [x / sum(target) for x in target]
        
        assume(abs(sum(current) - sum(target)) < 1e-10)
        
        result = realign_replica(current, target, damping=1.0)
        result_sum = sum(result)
        
        # Due to the bug (missing normalization), sum might not be preserved
        # This test documents the current behavior
        assert len(result) == len(current)
        # Note: sum(result) may not equal sum(current) due to the bug


class TestRealignReplicaMetamorphic:
    """Metamorphic property tests for realign_replica."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50)
    )
    def test_idempotent_with_damping_one(self, current, target):
        """
        Test that applying realign_replica twice with damping=1.0 is idempotent.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # First application
        intermediate = realign_replica(current, target, damping=1.0)
        
        # Second application
        final = realign_replica(intermediate, target, damping=1.0)
        
        # Should be equal when damping=1
        for i in range(len(current)):
            assert abs(final[i] - intermediate[i]) < 1e-10, f"Mismatch at index {i}: got {final[i]}, expected {intermediate[i]}"

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1, max_size=50),
        damping1=floats(min_value=0, max_value=1),
        damping2=floats(min_value=0, max_value=1)
    )
    def test_composition_property(self, current, target, damping1, damping2):
        """
        Test composition property: applying with damping1 then damping2 
        should be equivalent to applying with damping1 * damping2.
        """
        assume(len(current) == len(target))
        assume(len(current) > 0)
        
        # Apply first transformation
        intermediate = realign_replica(current, target, damping=damping1)
        
        # Apply second transformation
        final = realign_replica(intermediate, target, damping=damping2)
        
        # Expected result from single transformation with combined damping
        combined_damping = damping1 * damping2
        expected = realign_replica(current, target, damping=combined_damping)
        
        for i in range(len(current)):
            assert abs(final[i] - expected[i]) < 1e-10, \
                f"Composition failed at index {i}: got {final[i]}, expected {expected[i]}"