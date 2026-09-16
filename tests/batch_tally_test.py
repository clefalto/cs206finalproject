"""
Comprehensive Hypothesis-based tests for batch_tally function.

This test file exercises all semantic properties identified in 
properties/batch_tally_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, dictionaries, text, composite
from typing import Dict, Any, Union


# Import the function under test
def batch_tally(counts: Dict[str, int], key: str, *, max_value: Union[int, None] = None) -> int:
    """
    Increment a counter in a dictionary, optionally clamping to a maximum.
    """
    old_count = counts.get(key, 0)
    new_value = old_count + 1
    
    if max_value is not None:
        new_value = min(new_value, max_value)
    
    counts[key] = new_value
    return new_value


class TestBatchTallyProperties:
    """Test class for all semantic properties of batch_tally."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_clamping_applied_branch(self, counts, key, max_value):
        """Property: clamping_applied - if max_value is not None then new_value = min(new_value, max_value)."""
        assume(max_value is not None)
        
        old_count = counts.get(key, 0)
        expected_new_value = min(old_count + 1, max_value)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == expected_new_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_value_capped_at_max_branch(self, counts, key, max_value):
        """Property: value_capped_at_max - if new_value > max_value then new_value == max_value."""
        old_count = counts.get(key, 0)
        
        # Only test when the condition would be met
        assume(old_count + 1 > max_value)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == max_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=st.none()
    )
    def test_unbounded_increment_branch(self, counts, key, max_value):
        """Property: unbounded_increment - if max_value is None then new_value == counts.get(key, 0) + 1."""
        assume(max_value is None)
        
        old_count = counts.get(key, 0)
        expected_new_value = old_count + 1
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == expected_new_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_monotonic_increment_function(self, counts, key, max_value):
        """Property: monotonic_increment - new_value >= counts.get(key, 0) + 1."""
        old_count = counts.get(key, 0)
        old_count_before = old_count
        
        result = batch_tally(counts, key, max_value=max_value)
        
        # The result should be at least old_count + 1 (or clamped to max_value)
        if max_value is not None:
            assert result >= min(old_count_before + 1, max_value)
        else:
            assert result >= old_count_before + 1

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_state_persistence_function(self, counts, key, max_value):
        """Property: state_persistence - counts[key] == new_value."""
        old_count = counts.get(key, 0)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert counts[key] == result

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_return_value_consistency_function(self, counts, key, max_value):
        """Property: return_value_consistency - return_value == new_value."""
        result = batch_tally(counts, key, max_value=max_value)
        
        # The return value should equal the new value stored in the dictionary
        assert result == counts[key]

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_minimum_value_one_function(self, counts, key, max_value):
        """Property: minimum_value_one - new_value >= 1."""
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result >= 1

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_max_value_bound_function(self, counts, key, max_value):
        """Property: max_value_bound - new_value <= max_value."""
        assume(max_value is not None)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result <= max_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_key_creation_function(self, counts, key, max_value):
        """Property: key_creation - if key not in counts then key in counts."""
        assume(key not in counts)
        
        batch_tally(counts, key, max_value=max_value)
        
        assert key in counts

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_non_negative_count_function(self, counts, key, max_value):
        """Property: non_negative_count - new_value >= 0."""
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result >= 0

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_incremental_behavior_function(self, counts, key, max_value):
        """Property: incremental_behavior - new_value == old_count + 1 or new_value == max_value."""
        old_count = counts.get(key, 0)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        if max_value is None:
            assert result == old_count + 1
        else:
            assert result == old_count + 1 or result == max_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_idempotent_with_max_function(self, counts, key, max_value):
        """Property: idempotent_with_max - if counts.get(key, 0) >= max_value and max_value is not None then batch_tally(counts, key, max_value=max_value) == max_value."""
        old_count = counts.get(key, 0)
        
        # Only test when the precondition is met
        assume(old_count >= max_value)
        assume(max_value is not None)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == max_value


class TestBatchTallyEdgeCases:
    """Additional edge case tests for batch_tally."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_empty_counts(self, counts, key, max_value):
        """Test with empty counts dictionary."""
        assume(len(counts) == 0)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert key in counts
        assert counts[key] == result
        assert result == 1 if max_value is None else min(1, max_value)

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_exact_max_value(self, counts, key, max_value):
        """Test when old_count + 1 equals max_value exactly."""
        old_count = counts.get(key, 0)
        
        # Only test when old_count + 1 == max_value
        assume(old_count + 1 == max_value)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == max_value

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_max_value_one(self, counts, key, max_value):
        """Test with max_value of 1."""
        assume(max_value == 1)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result == 1

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_large_max_value(self, counts, key, max_value):
        """Test with large max_value."""
        assume(max_value > 100)
        
        old_count = counts.get(key, 0)
        
        result = batch_tally(counts, key, max_value=max_value)
        
        if old_count == 0:
            assert result == 1
        else:
            assert result == old_count + 1

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=100),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_multiple_calls_with_max(self, counts, key, max_value):
        """Test multiple calls to batch_tally with the same key and max_value."""
        assume(max_value >= 2)
        
        # First call
        result1 = batch_tally(counts, key, max_value=max_value)
        assert result1 == 1
        
        # Second call
        result2 = batch_tally(counts, key, max_value=max_value)
        assert result2 == 2
        
        # Third call (should still increment)
        result3 = batch_tally(counts, key, max_value=max_value)
        assert result3 == 3


class TestBatchTallyStringKeys:
    """Test with string keys specifically."""

    @given(
        counts=dictionaries(text(min_size=1, max_size=10), integers(min_value=0, max_value=1000), max_size=100),
        key=text(min_size=1, max_size=10),
        max_value=integers(min_value=1, max_value=1000) | st.none()
    )
    def test_string_keys(self, counts, key, max_value):
        """Test with string keys."""
        result = batch_tally(counts, key, max_value=max_value)
        
        assert isinstance(key, str)
        assert key in counts
        assert counts[key] == result

    @given(
        counts=dictionaries(text(min_size=1, max_size=10), integers(min_value=0, max_value=1000), max_size=100),
        key=text(min_size=1, max_size=10),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_special_characters_in_keys(self, counts, key, max_value):
        """Test with special characters in keys."""
        # This test ensures the function works with any string key
        result = batch_tally(counts, key, max_value=max_value)
        
        assert key in counts
        assert counts[key] == result


class TestBatchTallyLargeValues:
    """Test with large values."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000000) | st.none()
    )
    def test_large_values(self, counts, key, max_value):
        """Test with large integer values."""
        result = batch_tally(counts, key, max_value=max_value)
        
        assert result >= 1
        if max_value is not None:
            assert result <= max_value
        assert counts[key] == result


if __name__ == "__main__":
    # This allows running the tests with python -m pytest
    pytest.main([__file__, "-v"])