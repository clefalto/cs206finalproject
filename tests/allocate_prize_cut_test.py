import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math

# Import the function under test
# Note: The actual function implementation should be imported from the source code
# For now, we'll define a placeholder that matches the expected behavior
def allocate_prize_cut(amount, ratios, fee=0):
    """
    Allocate prize money based on ratios with optional fee deduction.
    
    Args:
        amount: Total prize amount to distribute
        ratios: List of ratios for distribution
        fee: Optional fee to deduct from each share
    
    Returns:
        List of allocated shares
    """
    if not ratios:
        raise ValueError("ratios required")
    
    if amount < 0:
        raise ValueError("negative amount")
    
    total_ratio = sum(ratios)
    if total_ratio <= 0:
        raise ValueError("invalid ratios")
    
    # Calculate original shares before fee
    original_shares = [amount * ratio / total_ratio for ratio in ratios]
    
    # Deduct fee from each share
    result = [share - fee for share in original_shares]
    
    return result


class TestAllocatePrizeCutProperties:
    """Test class for allocate_prize_cut semantic properties using Hypothesis."""
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_empty_ratios_error(self, amount, ratios):
        """Test that empty ratios raises ValueError with 'ratios required' message."""
        # Test with empty list
        with pytest.raises(ValueError, match="ratios required"):
            allocate_prize_cut(amount, [])
        
        # Test with None
        with pytest.raises(ValueError, match="ratios required"):
            allocate_prize_cut(amount, None)
    
    @given(
        amount=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_negative_amount_error(self, amount, ratios):
        """Test that negative amount raises ValueError with 'negative amount' message."""
        with pytest.raises(ValueError, match="negative amount"):
            allocate_prize_cut(amount, ratios)
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=-100, max_value=0, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_invalid_ratios_error(self, amount, ratios):
        """Test that non-positive total ratio raises ValueError with 'invalid ratios' message."""
        assume(sum(ratios) <= 0)
        with pytest.raises(ValueError, match="invalid ratios"):
            allocate_prize_cut(amount, ratios)
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)
    )
    def test_proportional_allocation(self, amount, ratios):
        """Test that sum of shares equals original amount (before fee deduction)."""
        result = allocate_prize_cut(amount, ratios)
        total_allocated = sum(result)
        
        # Allow for floating point precision errors
        assert abs(total_allocated - amount) < 1e-9, f"Sum of shares {total_allocated} != amount {amount}"
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_fee_deduction_bug(self, amount, ratios, fee):
        """Test that fee is correctly deducted from each share."""
        result = allocate_prize_cut(amount, ratios, fee)
        
        # Calculate original shares without fee
        total_ratio = sum(ratios)
        original_shares = [amount * ratio / total_ratio for ratio in ratios]
        
        # Verify each share equals original share minus fee
        for share, original_share in zip(result, original_shares):
            assert abs(share - (original_share - fee)) < 1e-9, \
                f"Share {share} != original_share {original_share} - fee {fee}"
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_shares(self, amount, ratios, fee):
        """Test that all shares are non-negative when fee doesn't exceed minimum share."""
        assume(fee <= min(amount * ratio / sum(ratios) for ratio in ratios))
        
        result = allocate_prize_cut(amount, ratios, fee)
        
        # All shares should be non-negative
        for share in result:
            assert share >= -1e-9, f"Share {share} is negative"
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=10)
    )
    def test_monotonic_allocation(self, amount, ratios):
        """Test that higher ratios get higher shares."""
        result = allocate_prize_cut(amount, ratios)
        
        # Check monotonic property: if ratios[i] > ratios[j] then result[i] > result[j]
        for i in range(len(ratios)):
            for j in range(len(ratios)):
                if ratios[i] > ratios[j]:
                    assert result[i] > result[j] - 1e-9, \
                        f"Ratio {ratios[i]} > {ratios[j]} but share {result[i]} <= {result[j]}"
    
    @given(
        amount=st.floats(min_value=0.1, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        k=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, amount, ratios, k):
        """Test that scaling inputs scales outputs proportionally."""
        result1 = allocate_prize_cut(amount, ratios)
        result2 = allocate_prize_cut(amount * k, [r * k for r in ratios])
        
        # Result2 should equal result1 scaled by k
        for s1, s2 in zip(result1, result2):
            assert abs(s2 - s1 * k) < 1e-6, \
                f"Scale invariance failed: {s2} != {s1} * {k}"


# Additional edge case tests
class TestAllocatePrizeCutEdgeCases:
    """Additional tests for edge cases and boundary conditions."""
    
    def test_zero_amount(self):
        """Test allocation with zero amount."""
        ratios = [1, 2, 3]
        result = allocate_prize_cut(0, ratios)
        assert all(share == 0 for share in result)
    
    def test_single_ratio(self):
        """Test allocation with single ratio."""
        result = allocate_prize_cut(100, [1])
        assert result == [100]
    
    def test_equal_ratios(self):
        """Test allocation with equal ratios."""
        amount = 100
        ratios = [1, 1, 1]
        result = allocate_prize_cut(amount, ratios)
        expected = [amount / len(ratios)] * len(ratios)
        for r, e in zip(result, expected):
            assert abs(r - e) < 1e-9
    
    @given(
        amount=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
        ratios=st.lists(st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=5),
        fee=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_fee_deduction_with_various_fees(self, amount, ratios, fee):
        """Test fee deduction works correctly for various fee amounts."""
        result = allocate_prize_cut(amount, ratios, fee)
        
        # Verify total after fee deduction
        total_ratio = sum(ratios)
        expected_total = amount - (fee * len(ratios))
        actual_total = sum(result)
        
        assert abs(actual_total - expected_total) < 1e-6, \
            f"Total after fee {actual_total} != expected {expected_total}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])