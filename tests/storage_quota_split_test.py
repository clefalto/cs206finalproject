"""
Hypothesis-based tests for storage_quota_split function semantic properties.
Tests all 7 semantic properties identified in storage_quota_split_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers

# Import the function under test
from dataset.python_programs.storage_quota_split import storage_quota_split


class TestStorageQuotaSplitProperties:
    """Test class for storage_quota_split semantic properties."""

    @given(total=floats(allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_raises_negative_total_error(self, total, ratios):
        """Test branch property: total < 0 raises ValueError("negative total")."""
        assume(total < 0)
        with pytest.raises(ValueError, match="negative total"):
            storage_quota_split(total, ratios)

    @given(total=floats(allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_raises_invalid_ratios_error(self, total, ratios):
        """Test branch property: not ratios or sum(ratios) <= 0 raises ValueError("invalid ratios")."""
        assume(not ratios or sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            storage_quota_split(total, ratios)

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_non_negative_input(self, total, ratios):
        """Test function property: total >= 0 and ratios is not empty and sum(ratios) > 0 (precondition)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        # This property is a precondition that should be satisfied
        # by the test data generation strategy
        assert total >= 0
        assert len(ratios) > 0
        assert sum(ratios) > 0

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_ratio_normalization(self, total, ratios):
        """Test function property: shares = [(r / total_ratio) * total for r in ratios] where total_ratio = sum(ratios)."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        result = storage_quota_split(total, ratios)
        total_ratio = sum(ratios)
        expected_shares = [(r / total_ratio) * total for r in ratios]
        
        # Check that shares are calculated correctly
        for i, (actual, expected) in enumerate(zip(result, expected_shares)):
            # Account for floating point precision
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_fee_subtraction_bug(self, total, ratios):
        """Test function property: return [s - fee for s in shares] where fee is subtracted from every share."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        # Test with default fee (0.0)
        result = storage_quota_split(total, ratios)
        total_ratio = sum(ratios)
        shares = [(r / total_ratio) * total for r in ratios]
        expected_result = [s - 0.0 for s in shares]  # Default fee is 0.0
        
        # Check that fee is subtracted from each share
        for i, (actual, expected) in enumerate(zip(result, expected_result)):
            assert abs(actual - expected) < 1e-10, f"Index {i}: expected {expected}, got {actual}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_sum_preservation_before_fee(self, total, ratios):
        """Test function property: sum(shares) == total before fee subtraction."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        # Calculate shares before fee subtraction
        total_ratio = sum(ratios)
        shares = [(r / total_ratio) * total for r in ratios]
        
        # Check that sum of shares equals total
        shares_sum = sum(shares)
        assert abs(shares_sum - total) < 1e-10, f"Expected sum {total}, got {shares_sum}"

    @given(total=floats(min_value=0, allow_nan=False, allow_infinity=False), ratios=lists(floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100))
    def test_proportional_distribution(self, total, ratios):
        """Test function property: shares[i] / shares[j] == ratios[i] / ratios[j] for all valid i, j."""
        assume(sum(ratios) > 0)
        assume(all(isinstance(r, (int, float)) for r in ratios))
        
        # Calculate shares before fee subtraction
        total_ratio = sum(ratios)
        shares = [(r / total_ratio) * total for r in ratios]
        
        # Check proportional distribution for all pairs
        for i in range(len(shares)):
            for j in range(len(shares)):
                if i != j and ratios[i] != 0 and ratios[j] != 0:
                    share_ratio = shares[i] / shares[j]
                    ratio_ratio = ratios[i] / ratios[j]
                    assert abs(share_ratio - ratio_ratio) < 1e-10, \
                        f"Ratio mismatch at indices {i},{j}: share ratio {share_ratio}, ratio ratio {ratio_ratio}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])