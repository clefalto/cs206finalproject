import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math

# Import the function under test
from dataset.python_programs import revenue_share


class TestRevenueShare:
    """Test suite for revenue_share function using Hypothesis framework."""

    @given(ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=0, max_size=100))
    def test_empty_ratios_error(self, ratios):
        """Test that empty ratios list raises ValueError with 'ratios required' message."""
        assume(not ratios)  # Only test when ratios is empty
        with pytest.raises(ValueError, match="ratios required"):
            revenue_share(100.0, ratios)

    @given(amount=st.floats(max_value=-0.01), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_negative_amount_error(self, amount, ratios):
        """Test that negative amount raises ValueError with 'negative amount' message."""
        assume(amount < 0)
        with pytest.raises(ValueError, match="negative amount"):
            revenue_share(amount, ratios)

    @given(ratios=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1, max_size=100))
    def test_invalid_ratios_error(self, ratios):
        """Test that total ratio <= 0 raises ValueError with 'invalid ratios' message."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            revenue_share(100.0, ratios)

    @given(ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_non_empty_ratios_required(self, ratios):
        """Test that ratios list must be non-empty."""
        assume(len(ratios) > 0)
        # This should not raise an error for non-empty ratios
        result = revenue_share(100.0, ratios)
        assert isinstance(result, list)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_non_negative_amount(self, amount, ratios):
        """Test that amount must be non-negative."""
        assume(amount >= 0)
        assume(sum(ratios) > 0)
        # This should not raise an error for non-negative amounts
        result = revenue_share(amount, ratios)
        assert isinstance(result, list)

    @given(ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_positive_total_ratio(self, ratios):
        """Test that total ratio must be positive."""
        assume(sum(ratios) > 0)
        # This should not raise an error for positive total ratios
        result = revenue_share(100.0, ratios)
        assert isinstance(result, list)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_shares_sum_to_amount_minus_fees(self, amount, ratios):
        """Test that shares sum to amount minus fees."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = revenue_share(amount, ratios)
        fee = 1.0  # Assuming fee is 1.0 based on the property description
        
        # Check that sum of (shares - fee) equals amount - (len(ratios) * fee)
        shares_minus_fees = sum([s - fee for s in result])
        expected_total = amount - (len(ratios) * fee)
        
        # Use math.isclose for floating point comparison
        assert math.isclose(shares_minus_fees, expected_total, rel_tol=1e-9, abs_tol=1e-9)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_proportional_distribution(self, amount, ratios):
        """Test that shares are distributed proportionally to ratios."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = revenue_share(amount, ratios)
        total_ratio = sum(ratios)
        
        for i in range(len(ratios)):
            expected_share = (ratios[i] / total_ratio) * amount
            # Use math.isclose for floating point comparison
            assert math.isclose(result[i], expected_share, rel_tol=1e-9, abs_tol=1e-9)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_same_length_output(self, amount, ratios):
        """Test that output list has same length as input ratios."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = revenue_share(amount, ratios)
        assert len(result) == len(ratios)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_fee_deduction_bug(self, amount, ratios):
        """Test that fee is deducted from each share."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = revenue_share(amount, ratios)
        total_ratio = sum(ratios)
        fee = 1.0  # Assuming fee is 1.0 based on the property description
        
        for i in range(len(ratios)):
            expected_share_before_fee = (ratios[i] / total_ratio) * amount
            expected_final_share = expected_share_before_fee - fee
            # Use math.isclose for floating point comparison
            assert math.isclose(result[i], expected_final_share, rel_tol=1e-9, abs_tol=1e-9)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=2, max_size=100))
    def test_monotonic_ratios(self, amount, ratios):
        """Test that higher ratios get higher shares."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        
        result = revenue_share(amount, ratios)
        
        # Check all pairs to ensure monotonicity
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if ratios[i] > ratios[j]:
                    assert result[i] > result[j], f"Expected result[{i}] > result[{j}] when ratios[{i}] > ratios[{j}]"

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=50), k=st.floats(min_value=0.1, max_value=100))
    def test_scale_invariance(self, amount, ratios, k):
        """Test that scaling ratios by k doesn't change the result."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        assume(k > 0)
        
        result1 = revenue_share(amount, ratios)
        scaled_ratios = [r * k for r in ratios]
        result2 = revenue_share(amount, scaled_ratios)
        
        # Results should be identical
        for i in range(len(result1)):
            assert math.isclose(result1[i], result2[i], rel_tol=1e-9, abs_tol=1e-9)

    @given(amount=st.floats(min_value=0, max_value=1000000), ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=50), k=st.floats(min_value=0, max_value=100))
    def test_linear_amount_scaling(self, amount, ratios, k):
        """Test that scaling amount by k scales result by k."""
        assume(sum(ratios) > 0)
        assume(amount >= 0)
        assume(k >= 0)
        
        result1 = revenue_share(amount, ratios)
        result2 = revenue_share(amount * k, ratios)
        
        # Each element should be scaled by k
        for i in range(len(result1)):
            expected = result1[i] * k if k > 0 else 0
            assert math.isclose(result2[i], expected, rel_tol=1e-9, abs_tol=1e-9)

    @given(ratios=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=100))
    def test_zero_amount_zero_shares(self, ratios):
        """Test that zero amount results in -fee for each share."""
        assume(sum(ratios) > 0)
        
        result = revenue_share(0.0, ratios)
        fee = 1.0  # Assuming fee is 1.0 based on the property description
        
        expected_result = [-fee] * len(ratios)
        for i in range(len(result)):
            assert math.isclose(result[i], expected_result[i], rel_tol=1e-9, abs_tol=1e-9)

    @given(amount=st.floats(min_value=-1000000, max_value=1000000), ratios=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=0, max_size=100))
    def test_error_consistency(self, amount, ratios):
        """Test that all error conditions raise ValueError with descriptive messages."""
        # Check if any precondition should fail
        should_fail = (not ratios) or (amount < 0) or (sum(ratios) <= 0 if ratios else False)
        
        if should_fail:
            with pytest.raises(ValueError) as exc_info:
                revenue_share(amount, ratios)
            
            # Check that error message is descriptive
            error_msg = str(exc_info.value)
            assert len(error_msg) > 0
            assert "required" in error_msg or "negative" in error_msg or "invalid" in error_msg
        else:
            # Should not raise an error
            result = revenue_share(amount, ratios)
            assert isinstance(result, list)
            assert len(result) == len(ratios)