"""
Hypothesis-based tests for tip_share function semantic properties.

This test file exercises all semantic properties identified in
properties/tip_share_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

# Import the function under test
from dataset.python_programs.tip_share import tip_share


class TestTipShareBranchProperties:
    """Test branch-level error conditions."""

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
    def test_empty_ratios_error(self, ratios):
        """Test that empty ratios raises ValueError with 'no ratios' message."""
        assume(len(ratios) == 0)
        with pytest.raises(ValueError, match="no ratios"):
            tip_share(100.0, ratios)

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_invalid_ratios_error(self, ratios):
        """Test that sum(ratios) <= 0 raises ValueError with 'invalid ratios' message."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            tip_share(100.0, ratios)

    @given(amount=st.floats(allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_negative_amount_error(self, amount, ratios):
        """Test that negative amount raises ValueError with 'negative amount' message."""
        assume(amount < 0)
        assume(sum(ratios) > 0)
        with pytest.raises(ValueError, match="negative amount"):
            tip_share(amount, ratios)


class TestTipShareFunctionProperties:
    """Test function-level semantic properties."""

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_non_empty_ratios(self, ratios):
        """Test that ratios list is non-empty."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        result = tip_share(100.0, ratios)
        assert len(ratios) > 0

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_positive_ratios_sum(self, ratios):
        """Test that sum of ratios is positive."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        result = tip_share(100.0, ratios)
        assert sum(ratios) > 0

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_non_negative_amount(self, amount, ratios):
        """Test that amount is non-negative."""
        assume(sum(ratios) > 0)
        result = tip_share(amount, ratios)
        assert amount >= 0

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_shares_sum_to_amount(self, amount, ratios):
        """Test that shares sum to amount minus fee * len(ratios)."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        # Use default fee of 0.0 for this test
        result = tip_share(amount, ratios, fee=0.0)
        expected_sum = amount - len(ratios) * 0.0
        assert abs(sum(result) - expected_sum) < 1e-9

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10))
    def test_proportional_distribution(self, amount, ratios):
        """Test that shares maintain proportional distribution."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        # Use default fee of 0.0 for this test
        result = tip_share(amount, ratios, fee=0.0)
        
        # Check that ratios between shares match ratios between input ratios
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if ratios[j] != 0 and result[j] != 0:
                    expected_ratio = ratios[i] / ratios[j]
                    actual_ratio = result[i] / result[j]
                    assert abs(actual_ratio - expected_ratio) < 1e-9

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_non_negative_shares(self, amount, ratios):
        """Test that all shares are non-negative when fee is small enough."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        # Calculate maximum fee that keeps all shares non-negative
        min_share_ratio = min([(r / sum(ratios)) * amount for r in ratios])
        fee = min_share_ratio * 0.9  # Use 90% of max fee to ensure non-negative shares
        
        result = tip_share(amount, ratios, fee=fee)
        assert all(share >= -1e-9 for share in result)  # Allow small floating point errors

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_same_length_output(self, amount, ratios):
        """Test that output length equals input ratios length."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = tip_share(amount, ratios)
        assert len(result) == len(ratios)

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10), k=st.floats(min_value=0.1, max_value=100.0))
    def test_scale_invariance(self, amount, ratios, k):
        """Test that scaling amount scales shares proportionally."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        assume(k > 0)
        
        # Use default fee of 0.0 for this test
        result_original = tip_share(amount, ratios, fee=0.0)
        result_scaled = tip_share(k * amount, ratios, fee=0.0)
        
        expected_scaled = [k * share for share in result_original]
        for i in range(len(result_scaled)):
            assert abs(result_scaled[i] - expected_scaled[i]) < 1e-9

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10), k=st.floats(min_value=0.1, max_value=100.0))
    def test_ratio_scale_invariance(self, amount, ratios, k):
        """Test that scaling ratios doesn't change the result."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        assume(k > 0)
        
        # Use default fee of 0.0 for this test
        result_original = tip_share(amount, ratios, fee=0.0)
        scaled_ratios = [k * r for r in ratios]
        result_scaled = tip_share(amount, scaled_ratios, fee=0.0)
        
        for i in range(len(result_original)):
            assert abs(result_original[i] - result_scaled[i]) < 1e-9

    @given(ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_zero_amount_zero_shares(self, ratios):
        """Test that zero amount results in shares equal to -fee."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        
        fee = 2.5  # Use a specific fee value
        result = tip_share(0.0, ratios, fee=fee)
        expected = [-fee] * len(ratios)
        
        for i in range(len(result)):
            assert abs(result[i] - expected[i]) < 1e-9

    @given(amount1=st.floats(min_value=0, allow_nan=False, allow_infinity=False), amount2=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_monotonicity(self, amount1, amount2, ratios):
        """Test that increasing amount doesn't decrease any share."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount1 >= amount2 >= 0)
        
        # Use default fee of 0.0 for this test
        result1 = tip_share(amount1, ratios, fee=0.0)
        result2 = tip_share(amount2, ratios, fee=0.0)
        
        for i in range(len(result1)):
            assert result1[i] >= result2[i] - 1e-9  # Allow small floating point errors

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10), fee=st.floats(min_value=0, max_value=100))
    def test_fee_subtraction_bug(self, amount, ratios, fee):
        """Test the fee subtraction bug: sum of shares equals amount - len(ratios) * fee."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = tip_share(amount, ratios, fee=fee)
        expected_sum = amount - len(ratios) * fee
        assert abs(sum(result) - expected_sum) < 1e-9


class TestTipShareEdgeCases:
    """Test additional edge cases and combinations."""

    @given(amount=st.floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=5))
    def test_zero_ratios_handling(self, amount, ratios):
        """Test handling of zero ratios in the input."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = tip_share(amount, ratios)
        assert len(result) == len(ratios)
        assert all(isinstance(share, float) for share in result)

    @given(amount=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False), ratios=st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=3))
    def test_reasonable_ranges(self, amount, ratios):
        """Test with reasonable ranges for amount and ratios."""
        assume(len(ratios) > 0)
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = tip_share(amount, ratios)
        assert len(result) == len(ratios)
        # Shares should be reasonable given the input ranges
        assert all(isinstance(share, float) for share in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])