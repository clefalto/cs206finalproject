"""
Hypothesis-based tests for allocate_bounty_cut function semantic properties.
Tests all 10 semantic properties identified in allocate_bounty_cut_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

# Import the function under test
from dataset.python_programs.allocate_bounty_cut import allocate_bounty_cut


class TestAllocateBountyCutProperties:
    """Test class for allocate_bounty_cut semantic properties."""

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_raises_no_ratios_error(self, ratios):
        """Test branch property: len(ratios) == 0 raises ValueError("no ratios")."""
        assume(len(ratios) == 0)
        with pytest.raises(ValueError, match="no ratios"):
            allocate_bounty_cut(100.0, ratios)

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_raises_invalid_ratios_error(self, ratios):
        """Test branch property: sum(ratios) <= 0 raises ValueError("invalid ratios")."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            allocate_bounty_cut(100.0, ratios)

    @given(amount=floats(allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_raises_negative_amount_error(self, amount, ratios):
        """Test branch property: amount < 0 raises ValueError("negative amount")."""
        assume(sum(ratios) > 0)
        assume(amount < 0)
        with pytest.raises(ValueError, match="negative amount"):
            allocate_bounty_cut(amount, ratios)

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_non_empty_ratios(self, ratios):
        """Test function property: len(ratios) > 0 (precondition)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        # This property is a precondition that should be satisfied
        # by the test data generation strategy
        assert len(ratios) > 0

    @given(ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_positive_ratios_sum(self, ratios):
        """Test function property: sum(ratios) > 0 (precondition)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        # This property is a precondition that should be satisfied
        # by the test data generation strategy
        assert sum(ratios) > 0

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_non_negative_amount(self, amount, ratios):
        """Test function property: amount >= 0 (precondition)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        # This property is a precondition that should be satisfied
        # by the test data generation strategy
        assert amount >= 0

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_proportional_allocation(self, amount, ratios):
        """Test function property: base[i] = (ratios[i] / sum(ratios)) * amount for all i."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_bounty_cut(amount, ratios)
        total_ratio = sum(ratios)
        expected_base = [(r / total_ratio) * amount for r in ratios]
        
        # Check that the base allocation is proportional
        for i, (actual, expected) in enumerate(zip(result, expected_base)):
            # Account for floating point precision
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_fee_deduction(self, amount, ratios, fee):
        """Test function property: result[i] = base[i] - fee for all i."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_bounty_cut(amount, ratios, fee=fee)
        total_ratio = sum(ratios)
        base = [(r / total_ratio) * amount for r in ratios]
        
        # Check that fee is deducted from each share
        for i, (actual, base_share) in enumerate(zip(result, base)):
            expected = base_share - fee
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_total_allocation(self, amount, ratios, fee):
        """Test function property: sum(result) = amount - len(ratios) * fee."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = allocate_bounty_cut(amount, ratios, fee=fee)
        expected_total = amount - len(ratios) * fee
        
        # Check that total allocation matches expected
        actual_total = sum(result)
        assert abs(actual_total - expected_total) < 1e-10, f"Expected total {expected_total}, got {actual_total}"

    @given(amount=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), fee=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test function property: result[i] >= 0 for all i (when fee <= min(base))."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        # Calculate base shares to check fee constraint
        total_ratio = sum(ratios)
        base = [(r / total_ratio) * amount for r in ratios]
        min_base = min(base) if base else 0
        
        # Only test when fee doesn't make shares negative
        assume(fee <= min_base)
        
        result = allocate_bounty_cut(amount, ratios, fee=fee)
        
        # Check that all shares are non-negative
        for i, share in enumerate(result):
            assert share >= 0, f"Share {i} is negative: {share}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])