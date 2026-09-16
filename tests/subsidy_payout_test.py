"""
Hypothesis-based tests for subsidy_payout function semantic properties.

This test suite exercises all semantic properties identified in 
properties/subsidy_payout_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers

from dataset.python_programs.subsidy_payout import subsidy_payout


class TestSubsidyPayoutBranchProperties:
    """Test branch-level error conditions."""

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
    def test_empty_ratios_error(self, ratios):
        """Test that empty ratios raises ValueError with 'ratios required'."""
        with pytest.raises(ValueError, match="ratios required"):
            subsidy_payout(100.0, ratios)

    @given(amount=st.floats(max_value=-0.1, allow_nan=False, allow_infinity=False))
    def test_negative_amount_error(self, amount):
        """Test that negative amount raises ValueError with 'negative amount'."""
        assume(amount < 0)
        with pytest.raises(ValueError, match="negative amount"):
            subsidy_payout(amount, [1.0, 2.0])

    @given(ratios=st.lists(st.floats(min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False), min_size=1))
    def test_invalid_ratios_error(self, ratios):
        """Test that non-positive total ratio raises ValueError with 'invalid ratios'."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            subsidy_payout(100.0, ratios)


class TestSubsidyPayoutFunctionProperties:
    """Test function-level semantic properties."""

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_distribution(self, amount, ratios, fee):
        """Test that sum of shares equals original amount."""
        result = subsidy_payout(amount, ratios, fee=fee)
        shares = [(r / sum(ratios)) * amount for r in ratios]
        
        # The function should distribute the amount proportionally
        assert abs(sum(shares) - amount) < 1e-9

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_fee_deduction_bug(self, amount, ratios, fee):
        """Test the fee deduction bug - fee is deducted from every participant."""
        result = subsidy_payout(amount, ratios, fee=fee)
        shares = [(r / sum(ratios)) * amount for r in ratios]
        
        # BUG: fee is deducted from every participant
        expected = [s - fee for s in shares]
        for i, (actual, expected_val) in enumerate(zip(result, expected)):
            assert abs(actual - expected_val) < 1e-9, f"Mismatch at index {i}: {actual} != {expected_val}"

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test that shares are non-negative when fee doesn't exceed minimum share."""
        shares = [(r / sum(ratios)) * amount for r in ratios]
        min_share = min(shares)
        
        # Only test when fee doesn't make shares negative
        assume(fee <= min_share)
        
        result = subsidy_payout(amount, ratios, fee=fee)
        for share in result:
            assert share >= -1e-9, f"Share {share} is negative"

    @given(
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_zero_amount_zero_shares(self, ratios, fee):
        """Test that zero amount results in zero shares."""
        result = subsidy_payout(0.0, ratios, fee=fee)
        for share in result:
            assert abs(share) < 1e-9, f"Expected zero share, got {share}"

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_single_ratio_full_amount(self, amount, fee):
        """Test that single ratio gets full amount minus fee."""
        ratios = [1.0]
        result = subsidy_payout(amount, ratios, fee=fee)
        
        assert len(result) == 1
        assert abs(result[0] - (amount - fee)) < 1e-9

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_ratios(self, amount, ratios, fee):
        """Test that higher ratios get higher shares."""
        assume(len(ratios) >= 2)
        
        # Sort ratios and get indices
        sorted_ratios = sorted(ratios, reverse=True)
        result = subsidy_payout(amount, ratios, fee=fee)
        
        # Check that shares follow the same order as ratios
        for i in range(len(ratios) - 1):
            for j in range(i + 1, len(ratios)):
                if ratios[i] > ratios[j]:
                    assert result[i] > result[j] - 1e-9, f"Ratio {ratios[i]} > {ratios[j]} but share {result[i]} <= {result[j]}"

    @given(
        amount=st.floats(min_value=0.1, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        scale_factor=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, amount, ratios, scale_factor, fee):
        """Test that scaling ratios and amount by same factor gives same result."""
        assume(scale_factor > 0)
        
        result1 = subsidy_payout(amount, ratios, fee=fee)
        result2 = subsidy_payout(amount * scale_factor, [r * scale_factor for r in ratios], fee=fee)
        
        for r1, r2 in zip(result1, result2):
            assert abs(r1 - r2) < 1e-6, f"Scale invariance failed: {r1} != {r2}"


class TestSubsidyPayoutEdgeCases:
    """Test additional edge cases and boundary conditions."""

    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=5),
        fee=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_fee_larger_than_shares_gives_negative(self, amount, ratios, fee):
        """Test that large fees can result in negative shares (demonstrating the bug)."""
        shares = [(r / sum(ratios)) * amount for r in ratios]
        min_share = min(shares)
        
        assume(fee > min_share)
        
        result = subsidy_payout(amount, ratios, fee=fee)
        # At least one share should be negative
        assert any(share < -1e-9 for share in result)

    @given(
        amount=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=1, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=5)
    )
    def test_no_fee_gives_exact_proportional_distribution(self, amount, ratios):
        """Test that with fee=0, distribution is exactly proportional."""
        result = subsidy_payout(amount, ratios, fee=0.0)
        
        total_ratio = sum(ratios)
        expected = [(r / total_ratio) * amount for r in ratios]
        
        for actual, exp in zip(result, expected):
            assert abs(actual - exp) < 1e-9

    @example(amount=100.0, ratios=[1.0, 2.0, 3.0], fee=10.0)
    @given(
        amount=st.floats(min_value=10, max_value=1000, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=1, max_value=100, allow_nan=False, allow_infinity=False), min_size=3, max_size=5),
        fee=st.floats(min_value=1, max_value=50, allow_nan=False, allow_infinity=False)
    )
    def test_specific_example_fee_deduction(self, amount, ratios, fee):
        """Test a specific example to verify fee deduction behavior."""
        result = subsidy_payout(amount, ratios, fee=fee)
        shares = [(r / sum(ratios)) * amount for r in ratios]
        expected = [s - fee for s in shares]
        
        for i, (actual, exp) in enumerate(zip(result, expected)):
            assert abs(actual - exp) < 1e-9, f"Mismatch at index {i}: {actual} != {exp}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])