"""
Tests for award_payout function using Hypothesis testing framework.
Tests all semantic properties identified in properties/award_payout_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, lists, integers


def award_payout(amount, ratios, fee=0.0):
    """
    Distribute an award amount proportionally based on ratios with fee deduction.
    
    Args:
        amount: Total amount to distribute (must be non-negative)
        ratios: List of ratios for distribution (must sum > 0)
        fee: Fixed fee to deduct from each share (default: 0.0)
    
    Returns:
        List of shares distributed proportionally after fee deduction
    
    Raises:
        ValueError: If ratios is empty, amount is negative, or total ratio <= 0
    """
    if not ratios:
        raise ValueError('ratios required')
    
    if amount < 0:
        raise ValueError('negative amount')
    
    total_ratio = sum(ratios)
    if total_ratio <= 0:
        raise ValueError('invalid ratios')
    
    # Calculate shares with fee deduction
    shares = []
    for ratio in ratios:
        share = (ratio / total_ratio) * amount - fee
        shares.append(share)
    
    return shares


class TestAwardPayout:
    """Test class for award_payout function semantic properties."""

    @given(
        amount=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_ratios_error(self, amount, fee):
        """Test that empty ratios raises ValueError('ratios required')."""
        with pytest.raises(ValueError, match="ratios required"):
            award_payout(amount, [], fee=fee)

    @given(
        ratios=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        negative_amount = st.floats(min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False)
    )
    def test_negative_amount_error(self, ratios, fee, negative_amount):
        """Test that negative amount raises ValueError('negative amount')."""
        
        with pytest.raises(ValueError, match="negative amount"):
            award_payout(negative_amount, ratios, fee=fee)

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios = st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_invalid_ratios_error(self, amount, fee, ratios):
        """Test that ratios with sum <= 0 raises ValueError('invalid ratios')."""
        # Generate ratios that sum to <= 0
        
        assume(sum(ratios) <= 0)
        
        with pytest.raises(ValueError, match="invalid ratios"):
            award_payout(amount, ratios, fee=fee)

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_fee_deduction(self, amount, ratios, fee):
        """Test that each share equals proportional amount minus fee."""
        assume(sum(ratios) > 0)
        
        result = award_payout(amount, ratios, fee=fee)
        
        for i, ratio in enumerate(ratios):
            expected_share = (ratio / sum(ratios)) * amount - fee
            assert abs(result[i] - expected_share) < 1e-10, \
                f"Share {i}: expected {expected_share}, got {result[i]}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_proportional_distribution(self, amount, ratios):
        """Test that sum of shares equals amount when fee is 0."""
        assume(sum(ratios) > 0)
        
        result = award_payout(amount, ratios, fee=0.0)
        
        total_shares = sum(result)
        assert abs(total_shares - amount) < 1e-10, \
            f"Sum of shares {total_shares} != amount {amount}"

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
        
        result = award_payout(amount, ratios, fee=fee)
        
        for i, share in enumerate(result):
            assert share >= 0, f"Share {i} is negative: {share}"

    @given(
        amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_length_preservation(self, amount, ratios, fee):
        """Test that output length equals input ratios length."""
        assume(sum(ratios) > 0)
        
        result = award_payout(amount, ratios, fee=fee)
        
        assert len(result) == len(ratios), \
            f"Output length {len(result)} != input length {len(ratios)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])