"""
Tests for bump_purchase function using Hypothesis testing framework.
Tests all semantic properties identified in properties/bump_purchase_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from copy import deepcopy


class TestBumpPurchase:
    """Test class for bump_purchase function semantic properties."""

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_applied(self, counters, key, cap):
        """Test that when cap is not None, updated <= cap."""
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        assert result <= cap, f"Expected updated value to be <= {cap}, got {result}"
        assert counters[key] <= cap, f"Expected counters[{key}] to be <= {cap}, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_enforced(self, counters, key, cap):
        """Test that when updated > cap, updated == cap."""
        # Set up initial state where increment would exceed cap
        counters[key] = cap  # This will make updated = cap + 1 > cap
        
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        # After incrementing from cap, it should be clamped back to cap
        assert result == cap, f"Expected updated value to be clamped to {cap}, got {result}"
        assert counters[key] == cap, f"Expected counters[{key}] to be clamped to {cap}, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_incremental(self, counters, key, cap):
        """Test that when counters[key] is not None, updated == counters[key] + 1."""
        # Precondition: counters[key] is not None (i.e., key exists in counters)
        assume(key in counters)
        
        initial_value = counters[key]
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        expected = initial_value + 1
        if cap is not None and expected > cap:
            expected = cap
            
        assert result == expected, f"Expected updated value to be {expected}, got {result}"
        assert counters[key] == expected, f"Expected counters[{key}] to be {expected}, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_initialization(self, counters, key, cap):
        """Test that when counters[key] is None, updated == 1."""
        # Precondition: counters[key] is None (i.e., key not in counters)
        assume(key not in counters)
        
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        assert result == 1, f"Expected updated value to be 1 for new key, got {result}"
        assert counters[key] == 1, f"Expected counters[{key}] to be 1 for new key, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_non_negative(self, counters, key, cap):
        """Test that when counters[key] is not None and counters[key] >= 0, updated >= 0."""
        # Precondition: counters[key] is not None and counters[key] >= 0
        assume(key in counters)
        assume(counters[key] >= 0)
        
        initial_value = counters[key]
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        expected = initial_value + 1
        if cap is not None and expected > cap:
            expected = cap
            
        assert result >= 0, f"Expected updated value to be >= 0, got {result}"
        assert counters[key] >= 0, f"Expected counters[{key}] to be >= 0, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000) | st.none()
    )
    def test_monotonic(self, counters, key, cap):
        """Test that when counters[key] is not None, updated > counters[key]."""
        # Precondition: counters[key] is not None (i.e., key exists in counters)
        assume(key in counters)
        
        initial_value = counters[key]
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        expected = initial_value + 1
        if cap is not None and expected > cap:
            expected = cap
            
        assert result > initial_value, f"Expected updated value to be > {initial_value}, got {result}"
        assert counters[key] > initial_value, f"Expected counters[{key}] to be > {initial_value}, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_bounded(self, counters, key, cap):
        """Test that when cap is not None, updated <= cap."""
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        assert result <= cap, f"Expected updated value to be <= {cap}, got {result}"
        assert counters[key] <= cap, f"Expected counters[{key}] to be <= {cap}, got {counters[key]}"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.none()
    )
    def test_identity_on_no_cap(self, counters, key, cap):
        """Test that when cap is None, updated == counters[key] + 1 if counters[key] is not None else 1."""
        initial_counters = deepcopy(counters)
        result = bump_purchase(counters, key, cap=cap)
        
        if key in counters:
            expected = counters[key] + 1
        else:
            expected = 1
            
        assert result == expected, f"Expected updated value to be {expected}, got {result}"
        assert counters[key] == expected, f"Expected counters[{key}] to be {expected}, got {counters[key]}"


# Import the function under test
from dataset.python_programs.bump_purchase import bump_purchase