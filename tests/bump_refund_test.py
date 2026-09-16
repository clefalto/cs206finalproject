"""
Tests for bump_refund function using Hypothesis testing framework.
Tests all semantic properties identified in properties/bump_refund_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from copy import deepcopy


class TestBumpRefund:
    """Test class for bump_refund function semantic properties."""

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_max_value_clamp_branch(self, counts, key, max_value):
        """Test that when max_value is not None, new_value <= max_value."""
        # Precondition: max_value is not None
        assume(max_value is not None)
        
        # Set up initial state
        initial_counts = deepcopy(counts)
        initial_value = counts.get(key, 0)
        
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] <= max_value, f"Expected counts[{key}] <= {max_value}, got {counts[key]}"
        assert result <= max_value, f"Expected return value <= {max_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000)
    )
    def test_value_capped_branch(self, counts, key, max_value):
        """Test that when new_value > max_value, new_value is set to max_value."""
        # Set up initial state where new_value would exceed max_value
        counts[key] = max_value + 1  # Ensure initial value > max_value
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] == max_value, f"Expected counts[{key}] to be clamped to {max_value}, got {counts[key]}"
        assert result == max_value, f"Expected return value to be {max_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_non_negative_function(self, counts, key, max_value):
        """Test that new_value >= 0 when counts[key] >= 0."""
        # Precondition: counts[key] >= 0 (this is always true with our strategy)
        initial_value = counts.get(key, 0)
        assume(initial_value >= 0)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] >= 0, f"Expected counts[{key}] >= 0, got {counts[key]}"
        assert result >= 0, f"Expected return value >= 0, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=1, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_monotonic_decrease_function(self, counts, key, max_value):
        """Test that new_value <= counts[key] when counts[key] > 0."""
        # Precondition: counts[key] > 0
        initial_value = counts.get(key, 1)  # Strategy ensures min_value=1
        assume(initial_value > 0)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] <= initial_value, f"Expected counts[{key}] <= {initial_value}, got {counts[key]}"
        assert result <= initial_value, f"Expected return value <= {initial_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000)
    )
    def test_max_value_bound_function(self, counts, key, max_value):
        """Test that new_value <= max_value when max_value is not None."""
        # Precondition: max_value is not None
        assume(max_value is not None)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] <= max_value, f"Expected counts[{key}] <= {max_value}, got {counts[key]}"
        assert result <= max_value, f"Expected return value <= {max_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.none()
    )
    def test_identity_when_no_max_function(self, counts, key, max_value):
        """Test that new_value == counts[key] when max_value is None."""
        # Precondition: max_value is None
        assume(max_value is None)
        
        initial_value = counts.get(key, 0)
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[key] == initial_value, f"Expected counts[{key}] == {initial_value}, got {counts[key]}"
        assert result == initial_value, f"Expected return value == {initial_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_key_preservation(self, counts, key, max_value):
        """Test that key remains in counts after the operation."""
        # Precondition: key in counts
        assume(key in counts)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert key in counts, f"Expected key '{key}' to remain in counts"
        assert result == counts[key], f"Expected return value to equal counts[{key}]"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        other_key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_counter_preservation(self, counts, key, other_key, max_value):
        """Test that other counters remain unchanged when other_key != key."""
        assume(other_key != key)
        assume(other_key in counts)  # Ensure other_key exists in counts
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert counts[other_key] == initial_counts[other_key], \
            f"Expected counts[{other_key}] to remain unchanged ({initial_counts[other_key]}), got {counts[other_key]}"
        
        # The function should return the updated value for the target key
        expected_value = max(0, initial_counts.get(key, 0) - 1)
        if max_value is not None and expected_value > max_value:
            expected_value = max_value
        
        assert result == expected_value, f"Expected return value to be {expected_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_key_creation(self, counts, key, max_value):
        """Test that new keys are created when they don't exist in counts."""
        assume(key not in counts)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        assert key in counts, f"Expected key '{key}' to be created in counts"
        assert counts[key] == 0, f"Expected counts[{key}] to be 0 for new key, got {counts[key]}"
        assert result == 0, f"Expected return value to be 0 for new key, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.integers(min_value=0, max_value=1000)
    )
    def test_exact_max_boundary(self, counts, key, max_value):
        """Test behavior when counts[key] exactly equals max_value before decrement."""
        counts[key] = max_value  # Set exactly at max_value
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        # After decrementing from max_value, it should be max_value - 1
        expected_value = max(0, max_value - 1)
        assert counts[key] == expected_value, f"Expected counts[{key}] to be {expected_value}, got {counters[key]}"
        assert result == expected_value, f"Expected return value to be {expected_value}, got {result}"

    @given(
        counts=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        max_value=st.none()
    )
    def test_no_max_behavior(self, counts, key, max_value):
        """Test that without max_value, counts[key] simply decrements by 1 (but not below 0)."""
        initial_value = counts.get(key, 0)
        
        initial_counts = deepcopy(counts)
        result = bump_refund(counts, key, max_value=max_value)
        
        expected_value = max(0, initial_value - 1)
        assert counts[key] == expected_value, \
            f"Expected counts[{key}] to be {expected_value}, got {counts[key]}"
        assert result == expected_value, \
            f"Expected return value to be {expected_value}, got {result}"


# Import the function under test
from dataset.python_programs.bump_refund import bump_refund