"""
Tests for task_tally function using Hypothesis testing framework.
Tests all semantic properties identified in properties/task_tally_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, dictionaries, text, none
from collections import defaultdict


def task_tally(counts, key, max_value=None):
    """
    Tally a task occurrence for a given key.
    
    Args:
        counts: Dictionary to store counts
        key: Key to tally
        max_value: Optional maximum value to enforce
    
    Returns:
        The new count value
    """
    new_value = counts.get(key, 0) + 1
    
    if max_value is not None:
        if new_value > max_value:
            new_value = max_value
    
    counts[key] = new_value
    return new_value


class TestTaskTally:
    """Test class for task_tally function semantic properties."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_ceiling_enforcement(self, counts, key, max_value):
        """Test that new_value <= max_value when max_value is not None."""
        assume(max_value is not None)
        
        original_count = counts.get(key, 0)
        result = task_tally(counts, key, max_value=max_value)
        
        assert result <= max_value, f"Result {result} should not exceed max_value {max_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_boundary_violation_fix(self, counts, key, max_value):
        """Test that when new_value > max_value, new_value is set to max_value."""
        # Set up a scenario where new_value would exceed max_value
        counts[key] = max_value  # This will make new_value = max_value + 1
        
        result = task_tally(counts, key, max_value=max_value)
        
        assert result == max_value, f"Result {result} should equal max_value {max_value} when boundary is violated"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_incremental_counting(self, counts, key, max_value):
        """Test that new_value == counts.get(key, 0) + 1."""
        original_count = counts.get(key, 0)
        result = task_tally(counts, key, max_value=max_value)
        
        expected = original_count + 1
        if max_value is not None and expected > max_value:
            expected = max_value
            
        assert result == expected, f"Result {result} should equal original_count {original_count} + 1 = {expected}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_state_persistence(self, counts, key, max_value):
        """Test that counts[key] == new_value after the function call."""
        original_count = counts.get(key, 0)
        result = task_tally(counts, key, max_value=max_value)
        
        assert counts[key] == result, f"counts[{key}] should equal result {result}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_return_value_consistency(self, counts, key, max_value):
        """Test that return value equals new_value."""
        result = task_tally(counts, key, max_value=max_value)
        
        # The return value should be the same as what we would calculate as new_value
        expected = counts.get(key, 0) + 1
        if max_value is not None and expected > max_value:
            expected = max_value
            
        assert result == expected, f"Return value {result} should equal expected new_value {expected}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_monotonic_increase(self, counts, key, max_value):
        """Test that new_value >= counts.get(key, 0) + 1 when max_value is None or new_value <= max_value."""
        original_count = counts.get(key, 0)
        result = task_tally(counts, key, max_value=max_value)
        
        if max_value is None or result <= max_value:
            assert result >= original_count + 1, f"Result {result} should be >= original_count {original_count} + 1"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000)
    )
    def test_bounded_counting(self, counts, key, max_value):
        """Test that new_value <= max_value when max_value is not None."""
        result = task_tally(counts, key, max_value=max_value)
        
        assert result <= max_value, f"Result {result} should not exceed max_value {max_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_key_preservation(self, counts, key, max_value):
        """Test that key remains in counts after the function call."""
        result = task_tally(counts, key, max_value=max_value)
        
        assert key in counts, f"Key {key} should be present in counts after function call"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), max_size=10),
        key=text(),
        max_value=integers(min_value=1, max_value=1000) | none()
    )
    def test_non_negative_counting(self, counts, key, max_value):
        """Test that new_value >= 1."""
        result = task_tally(counts, key, max_value=max_value)
        
        assert result >= 1, f"Result {result} should be >= 1"