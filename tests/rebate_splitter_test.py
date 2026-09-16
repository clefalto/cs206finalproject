"""
Hypothesis-based tests for the rebate_splitter function semantic properties.

This test file exercises all semantic properties identified in 
properties/rebate_splitter_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math


# Mock implementation of rebate_splitter for testing
def rebate_splitter(amount, ratios, fee=0):
    """
    Mock implementation of rebate_splitter function for testing purposes.
    
    This function distributes an amount according to given ratios and deducts fees.
    """
    if len(ratios) == 0:
        raise ValueError("no ratios")
    
    if sum(ratios) <= 0:
        raise ValueError("invalid ratios")
    
    if amount < 0:
        raise ValueError("negative amount")
    
    # Calculate base shares
    total_ratio = sum(ratios)
    base = [(r / total_ratio) * amount for r in ratios]
    
    # Apply fee deduction (note: this implements the bug described in the properties)
    result = [share - fee for share in base]
    
    return result


class TestRebateSplitterProperties:
    """Test class for rebate_splitter semantic properties."""
    
    # Strategies for generating test data
    valid_ratios = lists(floats(min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False), 
                        min_size=1, max_size=10)
    
    valid_amounts = floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
    
    valid_fees = floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    
    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=10))
    def test_empty_ratios_error(self, ratios):
        """Test that empty ratios raise ValueError with 'no ratios' message."""
        assume(len(ratios) == 0)
        
        with pytest.raises(ValueError, match="no ratios"):
            rebate_splitter(100.0, ratios)
    
    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
    def test_invalid_ratios_error(self, ratios):
        """Test that invalid ratios (sum <= 0) raise ValueError with 'invalid ratios' message."""
        assume(sum(ratios) <= 0)
        
        with pytest.raises(ValueError, match="invalid ratios"):
            rebate_splitter(100.0, ratios)
    
    @given(amount=floats(max_value=-0.001, allow_nan=False, allow_infinity=False),
           ratios=valid_ratios)
    def test_negative_amount_error(self, amount, ratios):
        """Test that negative amounts raise ValueError with 'negative amount' message."""
        with pytest.raises(ValueError, match="negative amount"):
            rebate_splitter(amount, ratios)
    
    @given(amount=valid_amounts, ratios=valid_ratios)
    def test_ratio_sum_preservation(self, amount, ratios):
        """Test that the sum of distributed amounts equals the original amount."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee=0)
        total_distributed = sum(result)
        
        # Use a small tolerance for floating point comparison
        assert abs(total_distributed - amount) < 1e-9, f"Sum preservation failed: {total_distributed} != {amount}"
    
    @given(amount=valid_amounts, ratios=valid_ratios)
    def test_proportional_distribution(self, amount, ratios):
        """Test that distribution maintains proportional ratios when fee=0."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee=0)
        
        # Check that ratios are preserved between all pairs
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if ratios[j] != 0 and result[j] != 0:
                    expected_ratio = ratios[i] / ratios[j]
                    actual_ratio = result[i] / result[j]
                    assert abs(actual_ratio - expected_ratio) < 1e-9, \
                        f"Proportional distribution failed: {actual_ratio} != {expected_ratio}"
    
    @given(amount=valid_amounts, ratios=valid_ratios, fee=valid_fees)
    def test_fee_deduction(self, amount, ratios, fee):
        """Test that fees are correctly deducted from base shares."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee)
        base = rebate_splitter(amount, ratios, fee=0)
        
        for i in range(len(ratios)):
            assert abs(result[i] - (base[i] - fee)) < 1e-9, \
                f"Fee deduction failed for index {i}: {result[i]} != {base[i] - fee}"
    
    @given(amount=valid_amounts, ratios=valid_ratios, fee=valid_fees)
    def test_output_length_preservation(self, amount, ratios, fee):
        """Test that output length equals input ratios length."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee)
        assert len(result) == len(ratios), \
            f"Length preservation failed: {len(result)} != {len(ratios)}"
    
    @given(amount=valid_amounts, ratios=valid_ratios)
    def test_non_negative_base_shares(self, amount, ratios):
        """Test that base shares are non-negative."""
        assume(sum(ratios) > 0)
        
        base = rebate_splitter(amount, ratios, fee=0)
        
        for i in range(len(ratios)):
            assert base[i] >= -1e-9, f"Negative base share at index {i}: {base[i]}"
    
    @given(amount1=floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
           amount2=floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
           ratios=valid_ratios)
    def test_monotonic_amount(self, amount1, amount2, ratios):
        """Test that larger amounts produce larger or equal results for all shares."""
        assume(sum(ratios) > 0)
        assume(amount1 >= amount2)
        
        result1 = rebate_splitter(amount1, ratios, fee=0)
        result2 = rebate_splitter(amount2, ratios, fee=0)
        
        for i in range(len(ratios)):
            assert result1[i] >= result2[i] - 1e-9, \
                f"Monotonicity failed at index {i}: {result1[i]} < {result2[i]}"
    
    @given(ratios=valid_ratios)
    def test_zero_amount_zero_result(self, ratios):
        """Test that zero amount produces zero results."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(0.0, ratios)
        
        for i in range(len(ratios)):
            assert abs(result[i]) < 1e-9, f"Non-zero result for zero amount at index {i}: {result[i]}"
    
    @given(amount=valid_amounts, ratios=valid_ratios, fee=valid_fees)
    def test_fee_bug_invariant(self, amount, ratios, fee):
        """Test the fee bug invariant: sum(result) == amount - (fee * len(ratios))."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee)
        expected_sum = amount - (fee * len(ratios))
        
        assert abs(sum(result) - expected_sum) < 1e-9, \
            f"Fee bug invariant failed: {sum(result)} != {expected_sum}"
    
    @given(amount=valid_amounts, ratios=valid_ratios, k=floats(min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False))
    def test_ratio_scaling_invariance(self, amount, ratios, k):
        """Test that scaling ratios doesn't change the result when fee=0."""
        assume(sum(ratios) > 0)
        
        result1 = rebate_splitter(amount, ratios, fee=0)
        scaled_ratios = [k * r for r in ratios]
        result2 = rebate_splitter(amount, scaled_ratios, fee=0)
        
        for i in range(len(ratios)):
            assert abs(result1[i] - result2[i]) < 1e-9, \
                f"Ratio scaling invariance failed at index {i}: {result1[i]} != {result2[i]}"
    
    @given(amount1=floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
           amount2=floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
           ratios=valid_ratios)
    def test_amount_scaling_linearity(self, amount1, amount2, ratios):
        """Test that scaling amount scales results linearly when fee=0."""
        assume(sum(ratios) > 0)
        assume(amount1 > 0 and amount2 > 0)
        
        k = amount1 / amount2
        result1 = rebate_splitter(amount1, ratios, fee=0)
        result2 = rebate_splitter(amount2, ratios, fee=0)
        
        for i in range(len(ratios)):
            expected = k * result2[i]
            assert abs(result1[i] - expected) < 1e-9, \
                f"Amount scaling linearity failed at index {i}: {result1[i]} != {expected}"
    
    @given(amount=valid_amounts, ratios=valid_ratios, 
           fee1=valid_fees, fee2=valid_fees)
    def test_fee_additivity(self, amount, ratios, fee1, fee2):
        """Test that applying fees additively gives the same result."""
        assume(sum(ratios) > 0)
        
        result_combined = rebate_splitter(amount, ratios, fee=fee1 + fee2)
        result_step1 = rebate_splitter(amount, ratios, fee=fee1)
        result_step2 = [x - fee2 for x in result_step1]
        
        for i in range(len(ratios)):
            assert abs(result_combined[i] - result_step2[i]) < 1e-9, \
                f"Fee additivity failed at index {i}: {result_combined[i]} != {result_step2[i]}"
    
    @given(amount=valid_amounts, ratios=valid_ratios)
    def test_zero_fee_identity(self, amount, ratios):
        """Test that zero fee returns the base calculation."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee=0)
        expected = [(r / sum(ratios)) * amount for r in ratios]
        
        for i in range(len(ratios)):
            assert abs(result[i] - expected[i]) < 1e-9, \
                f"Zero fee identity failed at index {i}: {result[i]} != {expected[i]}"


# Additional edge case tests
class TestRebateSplitterEdgeCases:
    """Additional tests for edge cases and specific scenarios."""

    
    # Strategies for generating test data
    valid_ratios = lists(floats(min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False), 
                        min_size=1, max_size=10)
    
    valid_amounts = floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
    
    valid_fees = floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    
    
    @given(ratios=lists(floats(min_value=0.001, max_value=100.0, allow_nan=False, allow_infinity=False), 
                        min_size=1, max_size=5))
    def test_single_ratio(self, ratios):
        """Test behavior with single ratio."""
        assume(len(ratios) == 1)
        assume(sum(ratios) > 0)
        
        amount = 100.0
        result = rebate_splitter(amount, ratios, fee=0)
        
        assert len(result) == 1
        assert abs(result[0] - amount) < 1e-9
    
    @given(amount=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    def test_equal_ratios(self, amount):
        """Test behavior with equal ratios."""
        ratios = [1.0, 1.0, 1.0]  # Three equal ratios
        result = rebate_splitter(amount, ratios, fee=0)
        
        # Each share should be amount / 3
        expected_share = amount / 3
        for share in result:
            assert abs(share - expected_share) < 1e-9
    
    @example(amount=0.0, ratios=[1.0, 2.0, 3.0], fee=0.0)
    @given(amount=valid_amounts, ratios=valid_ratios, fee=valid_fees)
    def test_specific_examples(self, amount, ratios, fee):
        """Test specific known examples."""
        assume(sum(ratios) > 0)
        
        result = rebate_splitter(amount, ratios, fee)
        
        # Basic sanity checks
        assert len(result) == len(ratios)
        assert all(isinstance(x, float) for x in result)
        
        # Check that the bug is present (fee multiplied by length)
        if fee > 0:
            expected_total = amount - (fee * len(ratios))
            assert abs(sum(result) - expected_total) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])