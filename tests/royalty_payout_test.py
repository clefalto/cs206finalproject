"""
Tests for royalty_payout function using Hypothesis testing framework.
Tests all semantic properties identified in properties/royalty_payout_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, lists, integers


# Import the function under test
from dataset.python_programs.royalty_payout import royalty_payout


class TestRoyaltyPayout:
    """Test class for royalty_payout function semantic properties."""

    @given(
        amount=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_ratios_error(self, amount, fee):
        """Test that empty ratios raises ValueError('ratios required')."""
        with pytest.raises(ValueError, match="ratios required"):
            royalty_payout(amount, [], fee=fee)

    @given(
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_negative_amount_error(self, ratios, fee):
        """Test that negative amount raises ValueError('negative amount')."""
        negative_amount = st.floats(min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False).example()
        
        with pytest.raises(ValueError, match="negative amount"):
            royalty_payout(negative_amount, ratios, fee=fee)

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_ratios_error(self, amount, fee):
        """Test that ratios with sum <= 0 raises ValueError('invalid ratios')."""
        # Generate ratios that sum to <= 0
        ratios = st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1).example()
        assume(sum(ratios) <= 0)
        
        with pytest.raises(ValueError, match="invalid ratios"):
            royalty_payout(amount, ratios, fee=fee)

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_sum_preservation(self, amount, ratios, fee):
        """Test that sum of shares equals amount - len(ratios) * fee."""
        assume(sum(ratios) > 0)
        
        result = royalty_payout(amount, ratios, fee=fee)
        expected_sum = amount - len(ratios) * fee
        actual_sum = sum(result)
        
        assert abs(actual_sum - expected_sum) < 1e-10, \
            f"Sum of shares {actual_sum} != expected {expected_sum}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=10)
    )
    def test_proportional_distribution(self, amount, ratios):
        """Test that shares maintain ratio proportions when fee is 0."""
        assume(sum(ratios) > 0)
        assume(all(r != 0 for r in ratios))  # All ratios non-zero
        
        result = royalty_payout(amount, ratios, fee=0.0)
        
        # Check that shares[i] / shares[j] == ratios[i] / ratios[j]
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if i != j:
                    ratio_i_j = ratios[i] / ratios[j]
                    share_i_j = result[i] / result[j]
                    assert abs(share_i_j - ratio_i_j) < 1e-10, \
                        f"Ratio {i}/{j}: shares ratio {share_i_j} != ratios ratio {ratio_i_j}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test that all shares are non-negative when fee is small enough."""
        assume(sum(ratios) > 0)
        min_proportional = min((r / sum(ratios)) * amount for r in ratios)
        assume(fee <= min_proportional)
        
        result = royalty_payout(amount, ratios, fee=fee)
        
        for i, share in enumerate(result):
            assert share >= 0, f"Share {i} is negative: {share}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_fee_deduction(self, amount, ratios, fee):
        """Test that each share equals proportional amount minus fee."""
        assume(sum(ratios) > 0)
        
        result = royalty_payout(amount, ratios, fee=fee)
        
        for i, ratio in enumerate(ratios):
            expected_share = (ratio / sum(ratios)) * amount - fee
            assert abs(result[i] - expected_share) < 1e-10, \
                f"Share {i}: expected {expected_share}, got {result[i]}"

    @given(
        amount1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        amount2=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity(self, amount1, amount2, ratios, fee):
        """Test that shares increase monotonically with amount."""
        assume(sum(ratios) > 0)
        assume(amount1 >= amount2 >= 0)
        
        result1 = royalty_payout(amount1, ratios, fee=fee)
        result2 = royalty_payout(amount2, ratios, fee=fee)
        
        for i in range(len(ratios)):
            assert result1[i] >= result2[i], \
                f"Share {i}: result1 {result1[i]} < result2 {result2[i]} for amounts {amount1} >= {amount2}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        k=st.floats(min_value=0.1, max_value=10, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, amount, ratios, k, fee):
        """Test that scaling ratios doesn't change the result."""
        assume(sum(ratios) > 0)
        assume(k > 0)
        
        result1 = royalty_payout(amount, ratios, fee=fee)
        scaled_ratios = [k * r for r in ratios]
        result2 = royalty_payout(amount, scaled_ratios, fee=fee)
        
        for i in range(len(ratios)):
            assert abs(result1[i] - result2[i]) < 1e-10, \
                f"Share {i}: result1 {result1[i]} != result2 {result2[i]} for scaled ratios"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])