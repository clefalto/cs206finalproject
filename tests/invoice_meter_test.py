import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, dictionaries, none, one_of
import math

# Import the function under test
# Note: The actual function implementation should be imported from the source code
# For now, we'll define a placeholder that matches the expected behavior
def invoice_meter(counts, key, max_value=None):
    """
    Increment a counter for a given key with optional maximum value.
    
    Args:
        counts: Dictionary to store counts
        key: Key to increment
        max_value: Optional maximum value (if None, no limit)
    
    Returns:
        The new count value
    """
    new_value = counts.get(key, 0) + 1
    
    if max_value is not None:
        if new_value > max_value:
            new_value = max_value
    
    counts[key] = new_value
    return new_value


class TestInvoiceMeter:
    """Test suite for invoice_meter function using Hypothesis."""

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_incremental_counting(self, counts, key, max_value):
        """Test that new_value equals previous count + 1."""
        original_count = counts.get(key, 0)
        result = invoice_meter(counts, key, max_value)
        
        expected = original_count + 1
        if max_value is not None and expected > max_value:
            expected = max_value
            
        assert result == expected

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_state_persistence(self, counts, key, max_value):
        """Test that counts[key] is updated to new_value."""
        result = invoice_meter(counts, key, max_value)
        assert counts[key] == result

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_monotonic_increase(self, counts, key, max_value):
        """Test that new_value is >= previous count."""
        original_count = counts.get(key, 0)
        result = invoice_meter(counts, key, max_value)
        assert result >= original_count

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_non_negative_count(self, counts, key, max_value):
        """Test that new_value is always non-negative."""
        result = invoice_meter(counts, key, max_value)
        assert result >= 0

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_ceiling_respect(self, counts, key, max_value):
        """Test that new_value respects the maximum when max_value is not None."""
        result = invoice_meter(counts, key, max_value)
        assert result <= max_value

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_key_preservation(self, counts, key, max_value):
        """Test that key remains in counts dictionary."""
        invoice_meter(counts, key, max_value)
        assert key in counts

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_return_value_consistency(self, counts, key, max_value):
        """Test that return value equals counts[key]."""
        result = invoice_meter(counts, key, max_value)
        assert result == counts[key]

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_ceiling_applied_branch(self, counts, key, max_value):
        """Test ceiling_applied property when max_value is not None."""
        assume(max_value is not None)
        result = invoice_meter(counts, key, max_value)
        assert result <= max_value

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_value_capped_branch(self, counts, key, max_value):
        """Test value_capped property when new_value > max_value."""
        assume(max_value is not None)
        # Set up state where increment would exceed max_value
        counts[key] = max_value - 1
        result = invoice_meter(counts, key, max_value)
        assert result == max_value

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_boundary_bug(self, counts, key, max_value):
        """Test boundary_bug property when count equals max_value."""
        assume(max_value is not None)
        # Set up state where current count equals max_value
        counts[key] = max_value
        result = invoice_meter(counts, key, max_value)
        # This test verifies the bug exists: new_value == max_value + 1
        # In a correct implementation, this should fail
        assert result == max_value + 1

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_multiple_calls_consistency(self, counts, key, max_value):
        """Test that multiple calls maintain consistency."""
        original_count = counts.get(key, 0)
        
        # First call
        result1 = invoice_meter(counts, key, max_value)
        expected1 = original_count + 1
        if max_value is not None and expected1 > max_value:
            expected1 = max_value
        assert result1 == expected1
        assert counts[key] == result1
        
        # Second call
        result2 = invoice_meter(counts, key, max_value)
        expected2 = result1 + 1
        if max_value is not None and expected2 > max_value:
            expected2 = max_value
        assert result2 == expected2
        assert counts[key] == result2

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_different_keys_independence(self, counts, key, max_value):
        """Test that different keys are handled independently."""
        other_key = key + "_other"
        
        # Increment both keys
        result1 = invoice_meter(counts, key, max_value)
        result2 = invoice_meter(counts, other_key, max_value)
        
        # Verify both keys are in counts
        assert key in counts
        assert other_key in counts
        
        # Verify values are independent
        assert counts[key] == result1
        assert counts[other_key] == result2

    @given(
        counts=dictionaries(st.text(), integers(min_value=0), max_size=10),
        key=st.text(),
        max_value=one_of(integers(min_value=0), none())
    )
    def test_specific_max_values(self, counts, key, max_value):
        """Test with specific max_value scenarios."""
        result = invoice_meter(counts, key, max_value)
        
        if max_value is None:
            # No ceiling, should increment normally
            expected = counts.get(key, 0) + 1
            assert result == expected
        else:
            # With ceiling, should not exceed max_value
            expected = counts.get(key, 0) + 1
            if expected > max_value:
                expected = max_value
            assert result == expected
            assert result <= max_value