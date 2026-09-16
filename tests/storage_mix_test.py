import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math

# Import the storage_mix function from the main module
# Note: This assumes the storage_mix function is available in the main module
# If it's in a different module, adjust the import accordingly
from dataset.python_programs import storage_mix


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_shape_mismatch_error(current, target, damping):
    """Test that shape mismatch raises ValueError"""
    assume(len(current) != len(target))
    with pytest.raises(ValueError, match="shape mismatch"):
        storage_mix(current, target, damping)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False)),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_empty_allocation_error(current, target, damping):
    """Test that empty allocation raises ValueError"""
    assume(not current)
    with pytest.raises(ValueError, match="empty allocation"):
        storage_mix(current, target, damping)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_shape_consistency(current, target, damping):
    """Test that output shape matches input shape when valid"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, damping)
    assert len(result) == len(current)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_linear_interpolation(current, target, damping):
    """Test that storage_mix performs linear interpolation"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, damping)
    
    for i in range(len(current)):
        expected = current[i] + (target[i] - current[i]) * damping
        assert math.isclose(result[i], expected, rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
)
def test_damping_factor_effect_zero(current, target):
    """Test that damping=0 returns current"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, 0.0)
    
    for i in range(len(current)):
        assert math.isclose(result[i], current[i], rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1)
)
def test_damping_factor_effect_one(current, target):
    """Test that damping=1 returns target"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, 1.0)
    
    for i in range(len(current)):
        assert math.isclose(result[i], target[i], rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_monotonicity_preservation(current, target, damping):
    """Test that interpolation preserves monotonicity bounds"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, damping)
    
    for i in range(len(current)):
        min_val = min(current[i], target[i])
        max_val = max(current[i], target[i])
        assert min_val <= result[i] <= max_val


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_no_renormalization_bug(current, target, damping):
    """Test that the function doesn't have a renormalization bug"""
    assume(len(current) == len(target))
    assume(sum(current) == pytest.approx(1.0))
    assume(sum(target) == pytest.approx(1.0))
    
    result = storage_mix(current, target, damping)
    # The sum should NOT be 1 (this would indicate a renormalization bug)
    # We check that it's different from 1 by a small tolerance
    assert not math.isclose(sum(result), 1.0, rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_preserves_zero_entries(current, target, damping):
    """Test that zero entries in current are handled correctly"""
    assume(len(current) == len(target))
    
    # Find indices where current has zero values
    zero_indices = [i for i, val in enumerate(current) if math.isclose(val, 0.0, rel_tol=1e-9, abs_tol=1e-9)]
    
    if zero_indices:
        result = storage_mix(current, target, damping)
        for i in zero_indices:
            expected = target[i] * damping
            assert math.isclose(result[i], expected, rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_preserves_target_entries(current, target, damping):
    """Test that when target[i] == current[i], the result equals current[i]"""
    assume(len(current) == len(target))
    
    # Find indices where target equals current
    equal_indices = [i for i in range(len(current)) if math.isclose(target[i], current[i], rel_tol=1e-9, abs_tol=1e-9)]
    
    if equal_indices:
        result = storage_mix(current, target, damping)
        for i in equal_indices:
            assert math.isclose(result[i], current[i], rel_tol=1e-9, abs_tol=1e-9)


@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_bounded_adjustment(current, target, damping):
    """Test that adjustments are bounded by the difference between current and target"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, damping)
    
    for i in range(len(current)):
        adjustment = abs(result[i] - current[i])
        max_possible_adjustment = abs(target[i] - current[i])
        assert adjustment <= max_possible_adjustment


# Additional edge case tests
@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=1),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=1),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_single_element_lists(current, target, damping):
    """Test with single element lists"""
    assume(len(current) == len(target))
    result = storage_mix(current, target, damping)
    assert len(result) == 1
    expected = current[0] + (target[0] - current[0]) * damping
    assert math.isclose(result[0], expected, rel_tol=1e-9, abs_tol=1e-9)


@given(
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_identical_lists(damping):
    """Test when current and target are identical"""
    current = [1.0, 2.0, 3.0]
    target = [1.0, 2.0, 3.0]
    result = storage_mix(current, target, damping)
    
    for i in range(len(current)):
        assert math.isclose(result[i], current[i], rel_tol=1e-9, abs_tol=1e-9)


# Test with specific examples that should trigger edge cases
@example(current=[0.0, 0.0, 0.0], target=[1.0, 1.0, 1.0], damping=0.5)
@example(current=[1.0, 2.0, 3.0], target=[1.0, 2.0, 3.0], damping=0.0)
@example(current=[1.0, 2.0, 3.0], target=[1.0, 2.0, 3.0], damping=1.0)
@example(current=[0.5, 0.5], target=[0.0, 1.0], damping=0.5)
@given(
    current=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
    target=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
    damping=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
)
def test_edge_cases(current, target, damping):
    """Test specific edge cases with examples"""
    assume(len(current) == len(target))
    
    # Test shape consistency
    result = storage_mix(current, target, damping)
    assert len(result) == len(current)
    
    # Test linear interpolation
    for i in range(len(current)):
        expected = current[i] + (target[i] - current[i]) * damping
        assert math.isclose(result[i], expected, rel_tol=1e-9, abs_tol=1e-9)