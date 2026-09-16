"""
Hypothesis-based tests for allocate_pool_cut function semantic properties.
Tests all 10 semantic properties identified in allocate_pool_cut_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

from dataset.python_programs.allocate_pool_cut import allocate_pool_cut


class TestAllocatePoolCutProperties:
    """Test class for allocate_pool_cut semantic properties."""

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_empty_ratios_error(self, ratios):
        """Test branch property: not ratios raises ValueError("ratios required")."""
        assume(not ratios)  # Empty list
        with pytest.raises(ValueError, match="ratios required"):
            allocate_pool_cut(100.0, ratios)

    @given(amount=floats(allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_negative_amount_error(self, amount, ratios):
        """Test branch property: amount < 0 raises ValueError("negative amount")."""
        assume(sum(ratios) > 0)
        assume(amount < 0)
        with pytest.raises(ValueError, match="negative amount"):
            allocate_pool_cut(amount, ratios)

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_invalid_ratios_error(self, ratios):
        """Test branch property: total_ratio <= 0 raises ValueError("invalid ratios")."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            allocate_pool_cut(100.0, ratios)

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_proportional_allocation(self, amount, ratios, fee):
        """Test function property: sum([s - fee for s in shares]) == amount - len(ratios) * fee."""
        assume(sum(ratios) > 0)
        
        shares = allocate_pool_cut(amount, ratios, fee=fee)
        
        # Calculate the sum after fee deduction
        total_after_fee = sum([s - fee for s in shares])
        expected_total = amount - len(ratios) * fee
        
        assert abs(total_after_fee - expected_total) < 1e-10, \
            f"Expected {expected_total}, got {total_after_fee}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_fee_deduction(self, amount, ratios, fee):
        """Test function property: all(s - fee < s for s in shares)."""
        assume(sum(ratios) > 0)
        
        shares = allocate_pool_cut(amount, ratios, fee=fee)
        
        # Check that fee deduction makes shares smaller
        for s in shares:
            assert s - fee < s, f"Fee deduction failed for share {s} with fee {fee}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test function property: all(s - fee >= 0 for s in shares) when fee <= min(shares)."""
        assume(sum(ratios) > 0)
        
        shares = allocate_pool_cut(amount, ratios, fee=fee)
        
        # Only test when fee doesn't make shares negative
        min_share = min(shares)
        assume(fee <= min_share)
        
        # Check that all shares remain non-negative after fee deduction
        for s in shares:
            assert s - fee >= 0, f"Share {s} becomes negative after fee {fee}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=2, max_size=100),
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_monotonic_allocation(self, amount, ratios, fee):
        """Test function property: if ratios[i] > ratios[j] then shares[i] > shares[j]."""
        assume(sum(ratios) > 0)
        
        shares = allocate_pool_cut(amount, ratios, fee=fee)
        
        # Check monotonic property
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if ratios[i] > ratios[j]:
                    assert shares[i] > shares[j], \
                        f"Monotonicity violated: ratio[{i}]={ratios[i]} > ratio[{j}]={ratios[j]} " \
                        f"but share[{i}]={shares[i]} <= share[{j}]={shares[j]}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=50),
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
           k=floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False))
    def test_scale_invariance(self, amount, ratios, fee, k):
        """Test function property: allocate_pool_cut(amount * k, [r * k for r in ratios]) == [s * k - fee for s in shares]."""
        assume(sum(ratios) > 0)
        assume(k > 0)
        
        # Calculate original shares
        original_shares = allocate_pool_cut(amount, ratios, fee=fee)
        
        # Calculate scaled shares
        scaled_amount = amount * k
        scaled_ratios = [r * k for r in ratios]
        scaled_shares = allocate_pool_cut(scaled_amount, scaled_ratios, fee=fee)
        
        # Calculate expected shares (original scaled then fee deducted)
        expected_shares = [s * k - fee for s in original_shares]
        
        # Compare scaled shares with expected shares
        for i, (actual, expected) in enumerate(zip(scaled_shares, expected_shares)):
            assert abs(actual - expected) < 1e-10, \
                f"Scale invariance failed at index {i}: expected {expected}, got {actual}"

    @given(ratios=lists(floats(min_value=0.0001, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_zero_amount_handling(self, ratios):
        """Test function property: allocate_pool_cut(0, ratios) == [-fee] * len(ratios)."""
        assume(sum(ratios) > 0)
        
        # Test with default fee (0.0)
        result_default = allocate_pool_cut(0, ratios)
        expected_default = [0.0] * len(ratios)
        
        for i, (actual, expected) in enumerate(zip(result_default, expected_default)):
            assert abs(actual - expected) < 1e-10, \
                f"Zero amount handling failed at index {i} with default fee: expected {expected}, got {actual}"
        
        # Test with non-zero fee
        fee = 5.0
        result_fee = allocate_pool_cut(0, ratios, fee=fee)
        expected_fee = [-fee] * len(ratios)
        
        for i, (actual, expected) in enumerate(zip(result_fee, expected_fee)):
            assert abs(actual - expected) < 1e-10, \
                f"Zero amount handling failed at index {i} with fee {fee}: expected {expected}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), 
           fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_single_ratio_handling(self, amount, fee):
        """Test function property: allocate_pool_cut(amount, ratios) == [amount - fee] when len(ratios) == 1."""
        ratios = [1.0]  # Single positive ratio
        
        result = allocate_pool_cut(amount, ratios, fee=fee)
        expected = [amount - fee]
        
        assert len(result) == 1, f"Expected single share, got {len(result)}"
        assert abs(result[0] - expected[0]) < 1e-10, \
            f"Single ratio handling failed: expected {expected[0]}, got {result[0]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])