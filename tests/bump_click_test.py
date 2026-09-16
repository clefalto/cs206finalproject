"""
Tests for bump_click function using Hypothesis testing framework.
Tests all semantic properties identified in properties/bump_click_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from copy import deepcopy


class TestBumpClick:
    """Test class for bump_click function semantic properties."""

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_cap_enforcement(self, counters, key, cap):
        """Test that when cap is not None and counters[key] > cap, counters[key] is set to cap."""
        # Set up initial state where the condition will be met
        if cap is not None:
            counters[key] = cap + 1  # Ensure counters[key] > cap
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        if cap is not None and initial_counters.get(key, 0) > cap:
            assert counters[key] == cap, f"Expected counters[{key}] to be clamped to {cap}, got {counters[key]}"
            assert result == cap, f"Expected return value to be {cap}, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_monotonic_increase(self, counters, key, cap):
        """Test that counters[key] >= initial_counters[key] when counters[key] < cap or cap is None."""
        initial_value = counters.get(key, 0)
        
        # Precondition: counters[key] < cap or cap is None
        assume(cap is None or initial_value < cap)
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert counters[key] >= initial_value, f"Expected counters[{key}] to be >= {initial_value}, got {counters[key]}"
        assert result >= initial_value, f"Expected return value to be >= {initial_value}, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_respect(self, counters, key, cap):
        """Test that counters[key] <= cap when cap is not None."""
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert counters[key] <= cap, f"Expected counters[{key}] to be <= {cap}, got {counters[key]}"
        assert result <= cap, f"Expected return value to be <= {cap}, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_key_preservation(self, counters, key, cap):
        """Test that key remains in counters after the operation."""
        # Precondition: key in counters
        assume(key in counters)
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert key in counters, f"Expected key '{key}' to remain in counters"
        assert result == counters[key], f"Expected return value to equal counters[{key}]"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        other_key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_counter_preservation(self, counters, key, other_key, cap):
        """Test that other counters remain unchanged when other_key != key."""
        assume(other_key != key)
        assume(other_key in counters)  # Ensure other_key exists in counters
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert counters[other_key] == initial_counters[other_key], \
            f"Expected counters[{other_key}] to remain unchanged ({initial_counters[other_key]}), got {counters[other_key]}"
        
        # The function should return the updated value for the target key
        expected_value = initial_counters.get(key, 0) + 1
        if cap is not None and expected_value > cap:
            expected_value = cap
        
        assert result == expected_value, f"Expected return value to be {expected_value}, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_key_creation(self, counters, key, cap):
        """Test that new keys are created when they don't exist in counters."""
        assume(key not in counters)
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert key in counters, f"Expected key '{key}' to be created in counters"
        assert counters[key] == 1, f"Expected counters[{key}] to be 1 for new key, got {counters[key]}"
        assert result == 1, f"Expected return value to be 1 for new key, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_exact_cap_boundary(self, counters, key, cap):
        """Test behavior when counters[key] exactly equals cap before increment."""
        counters[key] = cap  # Set exactly at cap
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        # After incrementing from cap, it should be clamped back to cap
        assert counters[key] == cap, f"Expected counters[{key}] to be clamped to {cap}, got {counters[key]}"
        assert result == cap, f"Expected return value to be {cap}, got {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.none()
    )
    def test_no_cap_behavior(self, counters, key, cap):
        """Test that without cap, counters[key] simply increments by 1."""
        initial_value = counters.get(key, 0)
        
        initial_counters = deepcopy(counters)
        result = bump_click(counters, key, cap=cap)
        
        assert counters[key] == initial_value + 1, \
            f"Expected counters[{key}] to be {initial_value + 1}, got {counters[key]}"
        assert result == initial_value + 1, \
            f"Expected return value to be {initial_value + 1}, got {result}"


# Import the function under test
from dataset.python_programs.bump_click import bump_click