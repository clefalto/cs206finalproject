"""
Tests for track_api function using Hypothesis testing framework.
Tests all semantic properties identified in properties/track_api_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, dictionaries, text
from collections import defaultdict


class TestTrackApi:
    """Test class for track_api function semantic properties."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_bounded_by_max(self, counts, key, max_value):
        """Test that new_value <= max_value when max_value is not None."""
        assume(max_value is not None)
        
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert result <= max_value, f"Result {result} should be <= max_value {max_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.integers(min_value=1, max_value=1000)
    )
    def test_clamped_to_max(self, counts, key, max_value):
        """Test that new_value == max_value when new_value > max_value."""
        # Set up the scenario where new_value would exceed max_value
        current_value = counts.get(key, 0)
        assume(current_value + 1 > max_value)
        
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert result == max_value, f"Result {result} should equal max_value {max_value} when clamped"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.integers(min_value=1, max_value=1000)
    )
    def test_unclamped_increment(self, counts, key, max_value):
        """Test that new_value == counts.get(key, 0) + 1 when not clamped."""
        # Set up the scenario where new_value would not exceed max_value
        current_value = counts.get(key, 0)
        assume(current_value + 1 <= max_value)
        
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        expected = current_value + 1
        assert result == expected, f"Result {result} should equal {expected} when not clamped"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_monotonic_increment(self, counts, key, max_value):
        """Test that new_value > counts.get(key, 0)."""
        current_value = counts.get(key, 0)
        
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert result > current_value, f"Result {result} should be > current_value {current_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_state_update(self, counts, key, max_value):
        """Test that counts[key] == new_value after the function call."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert counts_copy[key] == result, f"counts[{key}] should equal result {result}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_return_value_consistency(self, counts, key, max_value):
        """Test that return_value == new_value."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        # Calculate what new_value should be
        current_value = counts.get(key, 0)
        expected_new_value = current_value + 1
        
        if max_value is not None and expected_new_value > max_value:
            expected_new_value = max_value
        
        assert result == expected_new_value, f"Return value {result} should equal expected new_value {expected_new_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_minimum_value(self, counts, key, max_value):
        """Test that new_value >= 1."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert result >= 1, f"Result {result} should be >= 1"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.integers(min_value=1, max_value=1000)
    )
    def test_bounded_output(self, counts, key, max_value):
        """Test that new_value <= max_value when max_value is not None."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=max_value)
        
        assert result <= max_value, f"Result {result} should be <= max_value {max_value}"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text()
    )
    def test_unbounded_output(self, counts, key):
        """Test that new_value == counts.get(key, 0) + 1 when max_value is None."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        result = track_api(counts_copy, key, max_value=None)
        
        expected = counts.get(key, 0) + 1
        assert result == expected, f"Result {result} should equal {expected} when max_value is None"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000), min_size=0),
        key=text(),
        max_value=st.one_of(st.none(), st.integers(min_value=1, max_value=1000))
    )
    def test_key_preservation(self, counts, key, max_value):
        """Test that key in counts after the function call."""
        # Make a copy to avoid modifying the original
        counts_copy = counts.copy()
        
        track_api(counts_copy, key, max_value=max_value)
        
        assert key in counts_copy, f"Key '{key}' should be in counts after function call"


# Import the function under test
from dataset.python_programs.track_api import track_api