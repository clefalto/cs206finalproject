import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, lists
import math

# Import the function under test
from dataset.python_programs.priority_mix import priority_mix


class TestPriorityMix:
    """Test suite for priority_mix function using Hypothesis."""

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_length_preservation(self, current, target, damping):
        """Test that output length equals input length when lengths match."""
        assume(len(current) == len(target))
        result = priority_mix(current, target, damping=damping)
        assert len(result) == len(current)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_linear_interpolation(self, current, target, damping):
        """Test that each element follows linear interpolation formula."""
        assume(len(current) == len(target))
        result = priority_mix(current, target, damping=damping)
        
        for i in range(len(current)):
            expected = current[i] + (target[i] - current[i]) * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9, abs_tol=1e-9)

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_identity_on_equal_inputs(self, current, damping):
        """Test that equal inputs return the same result."""
        target = current.copy()
        result = priority_mix(current, target, damping=damping)
        assert result == current

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_damping_factor_effect(self, current, target, damping):
        """Test that damping factor controls movement toward target."""
        assume(len(current) == len(target))
        assume(current != target)  # Ensure they're different
        
        result = priority_mix(current, target, damping=damping)
        
        # For each element, check that result is between current and target
        # (or equal to current if damping is 0)
        for i in range(len(current)):
            if damping == 0.0:
                assert math.isclose(result[i], current[i], rel_tol=1e-9)
            else:
                # Result should be closer to current than target is
                current_dist = abs(result[i] - current[i])
                target_dist = abs(target[i] - current[i])
                assert current_dist <= target_dist * damping + 1e-9

    @given(
        current=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        target=lists(floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_no_renormalization_bug(self, current, target, damping):
        """Test that the function doesn't renormalize (this is the bug)."""
        assume(len(current) == len(target))
        assume(len(current) > 1)  # Need multiple elements to test sum behavior
        
        # Create inputs that sum to 1
        current_sum = sum(current)
        target_sum = sum(target)
        
        assume(current_sum != 0 and target_sum != 0)
        
        # Normalize inputs to sum to 1
        current_norm = [x / current_sum for x in current]
        target_norm = [x / target_sum for x in target]
        
        result = priority_mix(current_norm, target_norm, damping=damping)
        result_sum = sum(result)
        
        # Due to the bug (no renormalization), result should NOT sum to 1
        # unless damping is 0 or current == target
        if damping == 0.0 or current_norm == target_norm:
            assert math.isclose(result_sum, 1.0, rel_tol=1e-9)
        else:
            assert not math.isclose(result_sum, 1.0, rel_tol=1e-3)

    @given(
        current=st.lists(st.floats(min_value=-1000, max_value=1000)),
        target=st.lists(st.floats(min_value=-1000, max_value=1000)),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_error_on_empty_current(self, current, target, damping):
        """Test that empty current list raises ValueError."""
        assume(not current)  # Empty list
        with pytest.raises(ValueError, match="empty allocation"):
            priority_mix(current, target, damping=damping)

    @given(
        current=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1),
        target=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_error_on_length_mismatch(self, current, target, damping):
        """Test that mismatched lengths raise ValueError."""
        assume(len(current) != len(target))
        with pytest.raises(ValueError, match="shape mismatch"):
            priority_mix(current, target, damping=damping)

    @given(
        current=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1),
        target=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_shape_mismatch_error_branch(self, current, target, damping):
        """Test the shape mismatch error branch specifically."""
        assume(len(current) != len(target))
        with pytest.raises(ValueError, match="shape mismatch"):
            priority_mix(current, target, damping=damping)

    @given(
        current=st.lists(st.floats(min_value=-1000, max_value=1000)),
        target=st.lists(st.floats(min_value=-1000, max_value=1000)),
        damping=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_empty_allocation_error_branch(self, current, target, damping):
        """Test the empty allocation error branch specifically."""
        assume(not current)  # Empty list
        with pytest.raises(ValueError, match="empty allocation"):
            priority_mix(current, target, damping=damping)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])