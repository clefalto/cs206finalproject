"""
Tests for payment_split_rebate function using Hypothesis testing framework.
Tests all semantic properties identified in properties/payment_split_rebate_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, lists
import math


# Import the function under test
from dataset.python_programs.payment_split_rebate import payment_split_rebate


class TestPaymentSplitRebate:
    """Test class for payment_split_rebate function semantic properties."""

    @given(
        total=st.floats(min_value=-1000, max_value=-0.01, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_negative_total_error(self, total, ratios, rebate):
        """Test that negative total raises ValueError('negative total')."""
        assume(total < 0)
        
        with pytest.raises(ValueError, match="negative total"):
            payment_split_rebate(total, ratios, rebate=rebate)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=0, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_ratios_error(self, total, ratios, rebate):
        """Test that invalid ratios (empty or sum <= 0) raises ValueError('invalid ratios')."""
        assume(not ratios or sum(ratios) <= 0)
        
        with pytest.raises(ValueError, match="invalid ratios"):
            payment_split_rebate(total, ratios, rebate=rebate)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_total_property(self, total, ratios, rebate):
        """Test that total is non-negative when precondition is met."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        
        # The function should not raise an error for non-negative total
        result = payment_split_rebate(total, ratios, rebate=rebate)
        assert total >= 0, f"Total {total} should be non-negative"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_valid_ratios_property(self, total, ratios, rebate):
        """Test that ratios are valid when precondition is met."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        
        # The function should not raise an error for valid ratios
        result = payment_split_rebate(total, ratios, rebate=rebate)
        assert len(ratios) > 0, f"Ratios length {len(ratios)} should be > 0"
        assert sum(ratios) > 0, f"Sum of ratios {sum(ratios)} should be > 0"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_sum_to_total_minus_rebate(self, total, ratios, rebate):
        """Test that sum of shares equals total - len(ratios) * rebate."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        
        result = payment_split_rebate(total, ratios, rebate=rebate)
        expected_sum = total - len(ratios) * rebate
        actual_sum = sum(result)
        
        assert abs(actual_sum - expected_sum) < 1e-10, f"Sum of shares {actual_sum} != total - len(ratios)*rebate {expected_sum}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_proportional_to_ratios(self, total, ratios, rebate):
        """Test that shares[i] / ratios[i] == shares[j] / ratios[j] for all i, j."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        assume(all(r > 0 for r in ratios))  # All ratios positive
        
        result = payment_split_rebate(total, ratios, rebate=rebate)
        
        # Check that shares[i] / ratios[i] == shares[j] / ratios[j] for all i, j
        base_ratio = result[0] / ratios[0]
        for i in range(1, len(ratios)):
            current_ratio = result[i] / ratios[i]
            assert abs(current_ratio - base_ratio) < 1e-10, f"Ratio {i}: shares[i]/ratios[i] {current_ratio} != base ratio {base_ratio}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_non_negative(self, total, ratios, rebate):
        """Test that all shares are non-negative when rebate <= min(shares)."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        
        result = payment_split_rebate(total, ratios, rebate=rebate)
        
        # Calculate what the shares would be without rebate
        total_ratio = sum(ratios)
        original_shares = [(r / total_ratio) * total for r in ratios]
        min_original_share = min(original_shares)
        
        # Only test when rebate <= min(original_shares)
        assume(rebate <= min_original_share)
        
        for share in result:
            assert share >= 0, f"Share {share} is negative when rebate {rebate} <= min(original_shares) {min_original_share}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_decrease_with_rebate(self, total, ratios, rebate):
        """Test that shares[i] == original_shares[i] - rebate for all i."""
        assume(total >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        
        result = payment_split_rebate(total, ratios, rebate=rebate)
        
        # Calculate original shares without rebate
        total_ratio = sum(ratios)
        original_shares = [(r / total_ratio) * total for r in ratios]
        
        for i in range(len(result)):
            expected_share = original_shares[i] - rebate
            assert abs(result[i] - expected_share) < 1e-10, f"Share {i}: expected {expected_share}, got {result[i]}"

    @given(
        total1=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        total2=st.floats(min_value=501, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_increase_with_total(self, total1, total2, ratios, rebate):
        """Test that shares[i] increases as total increases for all i."""
        assume(total1 >= 0 and total2 >= 0)
        assume(len(ratios) > 0 and sum(ratios) > 0)
        assume(total1 < total2)
        
        result1 = payment_split_rebate(total1, ratios, rebate=rebate)
        result2 = payment_split_rebate(total2, ratios, rebate=rebate)
        
        for i in range(len(ratios)):
            assert result2[i] > result1[i], f"Share {i}: result2[{i}] {result2[i]} should be > result1[{i}] {result1[i]}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios1=st.lists(st.floats(min_value=0.1, max_value=50, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        ratios2=st.lists(st.floats(min_value=51, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        rebate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_increase_with_ratio(self, total, ratios1, ratios2, rebate):
        """Test that shares[i] increases as ratios[i] increases for all i."""
        assume(total >= 0)
        assume(len(ratios1) > 0 and sum(ratios1) > 0)
        assume(len(ratios2) > 0 and sum(ratios2) > 0)
        assume(len(ratios1) == len(ratios2))
        
        # Ensure ratios2[i] > ratios1[i] for all i
        assume(all(r2 > r1 for r1, r2 in zip(ratios1, ratios2)))
        
        result1 = payment_split_rebate(total, ratios1, rebate=rebate)
        result2 = payment_split_rebate(total, ratios2, rebate=rebate)
        
        for i in range(len(ratios1)):
            assert result2[i] > result1[i], f"Share {i}: result2[{i}] {result2[i]} should be > result1[{i}] {result1[i]}"