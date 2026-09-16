"""
Hypothesis-based property tests for attention_mask_merge function.

This test file exercises all semantic properties identified for the
attention_mask_merge function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, booleans


def attention_mask_merge(mask_a, mask_b):
    """
    Merge two attention masks using OR operation.
    
    Args:
        mask_a: First attention mask (list of booleans)
        mask_b: Second attention mask (list of booleans)
        
    Returns:
        Merged attention mask (list of booleans)
        
    Raises:
        ValueError: If masks have different lengths
    """
    if len(mask_a) != len(mask_b):
        raise ValueError("shape mismatch")
    
    return [a or b for a, b in zip(mask_a, mask_b)]


class TestAttentionMaskMergeProperties:
    """Test class for attention_mask_merge semantic properties."""
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_shape_mismatch_error(self, mask_a, mask_b):
        """Test that shape mismatch raises ValueError."""
        assume(len(mask_a) != len(mask_b))
        
        with pytest.raises(ValueError, match="shape mismatch"):
            attention_mask_merge(mask_a, mask_b)
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_merge_with_or(self, mask_a, mask_b):
        """Test that when lengths match, masks are merged with OR operation."""
        assume(len(mask_a) == len(mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        expected = [a or b for a, b in zip(mask_a, mask_b)]
        
        assert result == expected
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_length_preservation(self, mask_a, mask_b):
        """Test that output length equals input length when lengths match."""
        assume(len(mask_a) == len(mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        assert len(result) == len(mask_a)
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_boolean_preservation(self, mask_a, mask_b):
        """Test that all outputs are boolean values."""
        assume(len(mask_a) == len(mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        assert all(isinstance(x, bool) for x in result)
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_commutativity(self, mask_a, mask_b):
        """Test that merge operation is commutative."""
        assume(len(mask_a) == len(mask_b))
        
        result_ab = attention_mask_merge(mask_a, mask_b)
        result_ba = attention_mask_merge(mask_b, mask_a)
        
        assert result_ab == result_ba
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_idempotence(self, mask_a, mask_b):
        """Test that merging a mask with itself returns the original mask."""
        assume(len(mask_a) == len(mask_b))
        
        # Test with mask_a
        result_aa = attention_mask_merge(mask_a, mask_a)
        assert result_aa == mask_a
        
        # Test with mask_b
        result_bb = attention_mask_merge(mask_b, mask_b)
        assert result_bb == mask_b
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=50),
        mask_b=lists(booleans(), min_size=0, max_size=50),
        mask_c=lists(booleans(), min_size=0, max_size=50)
    )
    def test_monotonicity(self, mask_a, mask_b, mask_c):
        """Test that if mask_a <= mask_b, then merged results maintain this relationship."""
        assume(len(mask_a) == len(mask_b) == len(mask_c))
        assume(all(a <= b for a, b in zip(mask_a, mask_b)))
        
        result_ac = attention_mask_merge(mask_a, mask_c)
        result_bc = attention_mask_merge(mask_b, mask_c)
        
        assert all(a <= b for a, b in zip(result_ac, result_bc))
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_zero_element(self, mask_a, mask_b):
        """Test that merging with all-False mask returns the original mask."""
        assume(len(mask_a) == len(mask_b))
        assume(all(x == False for x in mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        assert result == mask_a
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=100),
        mask_b=lists(booleans(), min_size=0, max_size=100)
    )
    def test_one_element(self, mask_a, mask_b):
        """Test that merging with all-True mask returns all-True mask."""
        assume(len(mask_a) == len(mask_b))
        assume(all(x == True for x in mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        assert result == mask_b
    
    @given(
        mask_a=lists(booleans(), min_size=0, max_size=30),
        mask_b=lists(booleans(), min_size=0, max_size=30),
        mask_c=lists(booleans(), min_size=0, max_size=30)
    )
    def test_associativity(self, mask_a, mask_b, mask_c):
        """Test that merge operation is associative."""
        assume(len(mask_a) == len(mask_b) == len(mask_c))
        
        result1 = attention_mask_merge(attention_mask_merge(mask_a, mask_b), mask_c)
        result2 = attention_mask_merge(mask_a, attention_mask_merge(mask_b, mask_c))
        
        assert result1 == result2
    
    @given(
        mask_a=lists(booleans(), min_size=1, max_size=100),
        mask_b=lists(booleans(), min_size=1, max_size=100)
    )
    def test_bug_leak_masked_tokens(self, mask_a, mask_b):
        """Test that if any input has False values, output should have False values."""
        assume(len(mask_a) == len(mask_b))
        assume(any(a == False for a in mask_a))
        assume(any(b == False for b in mask_b))
        
        result = attention_mask_merge(mask_a, mask_b)
        assert any(a == False for a in result)