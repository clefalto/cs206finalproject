"""
Hypothesis-based tests for allocate_budget_cut function semantic properties.
Tests all 10 semantic properties identified in allocate_budget_cut_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

# Import the function under test
from dataset.python_programs.allocate_budget_cut import allocate_budget_cut


class TestAllocateBudgetCutProperties:
    """Test class for allocate_budget_cut semantic properties."""

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_empty_ratios_error(self, ratios):
        """Test branch property: not ratios raises ValueError("ratios required")."""
        assume(not ratios)
        with pytest.raises(ValueError, match="ratios required"):
            allocate_budget_cut(100.0, ratios)

    @given(amount=floats(allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_negative_amount_error(self, amount, ratios):
        """Test branch property: amount < 0 raises ValueError("negative amount")."""
        assume(sum(ratios) > 0)
        assume(amount < 0)
        with pytest.raises(ValueError, match="negative amount"):
            allocate_budget_cut(amount, ratios)

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_invalid_ratios_error(self, ratios):
        """Test branch property: total_ratio <= 0 raises ValueError("invalid ratios")."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            allocate_budget_cut(100.0, ratios)

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_proportional_allocation(self, amount, ratios):
        """Test function property: sum(shares) == amount."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_budget_cut(amount, ratios)
        
        # Check that sum of shares equals amount
        assert abs(sum(result) - amount) < 1e-10, f"Sum of shares {sum(result)} != amount {amount}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_fee_deduction(self, amount, ratios, fee):
        """Test function property: all(s == original_share - fee for s, original_share in zip(result, original_shares))."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_budget_cut(amount, ratios, fee=fee)
        
        # Calculate original shares without fee
        total_ratio = sum(ratios)
        original_shares = [(r / total_ratio) * amount for r in ratios]
        
        # Check that each share equals original share minus fee
        for i, (actual, original) in enumerate(zip(result, original_shares)):
            expected = original - fee
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test function property: all(s >= 0 for s in result) when fee <= min(original_shares)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        # Calculate original shares to check fee constraint
        total_ratio = sum(ratios)
        original_shares = [(r / total_ratio) * amount for r in ratios]
        min_original = min(original_shares) if original_shares else 0
        
        # Only test when fee doesn't make shares negative
        assume(fee <= min_original)
        
        result = allocate_budget_cut(amount, ratios, fee=fee)
        
        # Check that all shares are non-negative
        for i, share in enumerate(result):
            assert share >= 0, f"Share {i} is negative: {share}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_order_preservation(self, amount, ratios):
        """Test function property: len(result) == len(ratios) and order preservation."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_budget_cut(amount, ratios)
        
        # Check that result length matches ratios length
        assert len(result) == len(ratios), f"Result length {len(result)} != ratios length {len(ratios)}"
        
        # Check that order is preserved (shares correspond to ratios)
        total_ratio = sum(ratios)
        expected_shares = [(r / total_ratio) * amount for r in ratios]
        
        for i, (actual, expected) in enumerate(zip(result, expected_shares)):
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), k=floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False))
    def test_scale_invariance(self, amount, ratios, k):
        """Test function property: allocate_budget_cut(amount * k, ratios) == [s * k for s in allocate_budget_cut(amount, ratios)]."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        assume(k > 0)
        
        result_scaled = allocate_budget_cut(amount * k, ratios)
        result_original = allocate_budget_cut(amount, ratios)
        expected_scaled = [s * k for s in result_original]
        
        # Check that scaled result matches expected
        for i, (actual, expected) in enumerate(zip(result_scaled, expected_scaled)):
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_zero_amount_handling(self, ratios, fee):
        """Test function property: allocate_budget_cut(0, ratios) == [-fee] * len(ratios)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_budget_cut(0.0, ratios, fee=fee)
        expected = [-fee] * len(ratios)
        
        # Check that result matches expected
        for i, (actual, expected_val) in enumerate(zip(result, expected)):
            assert abs(actual - expected_val) < 1e-10, f"Index {i}: expected {expected_val}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_single_ratio_handling(self, amount, fee):
        """Test function property: allocate_budget_cut(amount, [ratio]) == [amount - fee] when len(ratios) == 1 and ratios[0] > 0."""
        ratios = [1.0]  # Single positive ratio
        
        result = allocate_budget_cut(amount, ratios, fee=fee)
        expected = [amount - fee]
        
        # Check that result matches expected
        assert len(result) == 1, f"Expected single result, got {len(result)}"
        assert abs(result[0] - expected[0]) < 1e-10, f"Expected {expected[0]}, got {result[0]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])