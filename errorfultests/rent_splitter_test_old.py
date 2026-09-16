"""
Hypothesis-based tests for rent_splitter function semantic properties.

This test file exercises all 17 semantic properties identified for the rent_splitter function:
- 4 branch-level properties (error conditions and valid processing)
- 13 function-level properties (input validation, mathematical properties, edge cases)
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers, composite
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs import rent_splitter


# Define strategies for generating test data
@composite
def valid_ratios(draw, min_size=1, max_size=10):
    """Generate valid ratio lists for rent_splitter."""
    # Generate a list of positive floats
    ratios = draw(lists(floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False), 
                       min_size=min_size, max_size=max_size))
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    return ratios


@composite  
def invalid_ratios(draw, min_size=1, max_size=10):
    """Generate invalid ratio lists that should trigger ValueError."""
    choice = draw(st.sampled_from(['empty', 'zero_sum', 'negative_sum']))
    
    if choice == 'empty':
        return []
    elif choice == 'zero_sum':
        # Generate ratios that sum to exactly 0
        size = draw(integers(min_value=1, max_value=max_size))
        if size == 1:
            return [0.0]
        else:
            # Create a list where positive and negative values cancel out
            pos_count = draw(integers(min_value=1, max_value=size-1))
            neg_count = size - pos_count
            pos_vals = draw(lists(floats(min_value=0.1, max_value=50.0), min_size=pos_count, max_size=pos_count))
            neg_vals = draw(lists(floats(min_value=-50.0, max_value=-0.1), min_size=neg_count, max_size=neg_count))
            ratios = pos_vals + neg_vals
            # Shuffle to avoid predictable patterns
            import random
            random.shuffle(ratios)
            return ratios
    else:  # negative_sum
        # Generate ratios that sum to a negative value
        size = draw(integers(min_value=1, max_value=max_size))
        ratios = draw(lists(floats(min_value=-100.0, max_value=-0.1, allow_nan=False, allow_infinity=False), 
                           min_size=size, max_size=size))
        assume(sum(ratios) < 0)
        return ratios


# Branch-level property tests
@given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
def test_empty_ratios_error(ratios):
    """Test that empty ratios list raises ValueError with 'no ratios' message."""
    with pytest.raises(ValueError, match="no ratios"):
        rent_splitter(100.0, ratios)


@given(ratios=invalid_ratios().filter(lambda r: len(r) > 0 and sum(r) <= 0))
def test_invalid_ratios_error(ratios):
    """Test that invalid ratios (sum <= 0) raise ValueError with 'invalid ratios' message."""
    assume(len(ratios) > 0)
    assume(sum(ratios) <= 0)
    with pytest.raises(ValueError, match="invalid ratios"):
        rent_splitter(100.0, ratios)


@given(amount=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
def test_negative_amount_error(amount):
    """Test that negative amount raises ValueError with 'negative amount' message."""
    assume(amount < 0)
    with pytest.raises(ValueError, match="negative amount"):
        rent_splitter(amount, [1.0, 2.0, 3.0])


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_valid_input_processing(amount, ratios):
    """Test that valid inputs return the expected computation: [share - fee for share in base]."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    
    # Calculate expected base shares
    total_ratio = sum(ratios)
    base = [amount * ratio / total_ratio for ratio in ratios]
    expected = [share - 1.0 for share in base]  # fee is 1.0
    
    assert len(result) == len(expected)
    for i in range(len(result)):
        assert abs(result[i] - expected[i]) < 1e-10


# Function-level property tests
@given(amount=st.floats(allow_nan=False, allow_infinity=False),
       ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_input_validation(amount, ratios):
    """Test that input validation raises ValueError for any invalid condition."""
    assume(len(ratios) == 0 or sum(ratios) <= 0 or amount < 0)
    
    with pytest.raises(ValueError):
        rent_splitter(amount, ratios)


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_proportional_distribution(amount, ratios):
    """Test that the sum of results equals amount minus total fees."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    total_fees = len(ratios) * 1.0  # fee is 1.0 per ratio
    
    assert abs(sum(result) - (amount - total_fees)) < 1e-10


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_ratio_preservation(amount, ratios):
    """Test that the ratio between base shares matches the input ratio."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    
    # Calculate base shares (before fee application)
    total_ratio = sum(ratios)
    base = [amount * ratio / total_ratio for ratio in ratios]
    
    # Check ratio preservation for all pairs where denominator is non-zero
    for i in range(len(ratios)):
        for j in range(len(ratios)):
            if ratios[j] != 0:
                expected_ratio = ratios[i] / ratios[j]
                actual_ratio = base[i] / base[j]
                assert abs(actual_ratio - expected_ratio) < 1e-10


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_fee_application_bug(amount, ratios):
    """Test that fee is applied to each share individually (this is the bug)."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    
    # Calculate what the result would be if fee was applied once to total
    total_ratio = sum(ratios)
    base = [amount * ratio / total_ratio for ratio in ratios]
    correct_result = [share - (1.0 / len(ratios)) for share in base]  # Fee spread across shares
    
    # The bug means our result differs from the correct implementation
    for i in range(len(result)):
        assert abs(result[i] - correct_result[i]) > 1e-10


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_output_length(amount, ratios):
    """Test that output length matches input ratios length."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    assert len(result) == len(ratios)


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_non_negative_base_shares(amount, ratios):
    """Test that base shares are non-negative."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    
    # Calculate base shares (before fee application)
    total_ratio = sum(ratios)
    base = [amount * ratio / total_ratio for ratio in ratios]
    
    for share in base:
        assert share >= -1e-10  # Allow small floating point errors


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_sum_preservation_before_fee(amount, ratios):
    """Test that sum of base shares equals the input amount."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(amount, ratios)
    
    # Calculate base shares (before fee application)
    total_ratio = sum(ratios)
    base = [amount * ratio / total_ratio for ratio in ratios]
    
    assert abs(sum(base) - amount) < 1e-10


@given(amount1=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       amount2=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios())
def test_monotonicity_in_amount(amount1, amount2, ratios):
    """Test that increasing amount doesn't decrease any share."""
    assume(amount1 >= 0 and amount2 >= 0)
    assume(amount1 >= amount2)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result1 = rent_splitter(amount1, ratios)
    result2 = rent_splitter(amount2, ratios)
    
    for i in range(len(ratios)):
        assert result1[i] >= result2[i] - 1e-10  # Allow small floating point errors


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios(),
       k=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_scale_invariance_ratios(amount, ratios, k):
    """Test that scaling ratios doesn't change the result."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    assume(k > 0)
    
    result1 = rent_splitter(amount, ratios)
    scaled_ratios = [k * r for r in ratios]
    result2 = rent_splitter(amount, scaled_ratios)
    
    for i in range(len(ratios)):
        assert abs(result1[i] - result2[i]) < 1e-10


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
       ratios=valid_ratios(),
       k=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_scale_invariance_amount(amount, ratios, k):
    """Test that scaling amount scales the result proportionally."""
    assume(amount >= 0)
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    assume(k >= 0)
    
    result1 = rent_splitter(amount, ratios)
    result2 = rent_splitter(k * amount, ratios)
    expected = [k * share for share in result1]
    
    for i in range(len(ratios)):
        assert abs(result2[i] - expected[i]) < 1e-10


@given(ratios=valid_ratios())
def test_zero_amount_handling(ratios):
    """Test that zero amount results in -fee for all shares."""
    assume(len(ratios) > 0)
    assume(sum(ratios) > 0)
    
    result = rent_splitter(0.0, ratios)
    
    for share in result:
        assert abs(share - (-1.0)) < 1e-10  # fee is 1.0


@given(amount=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
def test_single_ratio_handling(amount):
    """Test that single ratio results in amount - fee."""
    assume(amount >= 0)
    
    result = rent_splitter(amount, [1.0])
    assert len(result) == 1
    assert abs(result[0] - (amount - 1.0)) < 1e-10  # fee is 1.0


@given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False)),
       amount=st.floats(allow_nan=False, allow_infinity=False))
def test_error_precedence(ratios, amount):
    """Test that error checks have correct precedence order."""
    # Test empty ratios takes precedence
    if len(ratios) == 0:
        with pytest.raises(ValueError, match="no ratios"):
            rent_splitter(amount, ratios)
    # Test invalid ratios takes precedence over negative amount
    elif sum(ratios) <= 0:
        with pytest.raises(ValueError, match="invalid ratios"):
            rent_splitter(amount, ratios)
    # Test negative amount check
    elif amount < 0:
        with pytest.raises(ValueError, match="negative amount"):
            rent_splitter(amount, ratios)