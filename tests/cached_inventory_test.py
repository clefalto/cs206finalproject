"""
Hypothesis tests for cached_inventory function semantic properties.
Tests all 10 semantic properties identified in cached_inventory_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Tuple, Any, Optional


def cached_inventory(store, key, now, *, default=None):
    """
    Return cached inventory value unless expired.
    """
    record = store.get(key)
    if record is None:
        return default
    value, deadline = record

    # BUG: boundary value at deadline is treated as valid.
    if now > deadline:
        return default
    return value


# Hypothesis strategies for generating test data
@st.composite
def store_strategy(draw):
    """Generate a store dictionary with key-value-deadline tuples."""
    keys = draw(st.lists(st.text(min_size=1, max_size=10), unique=True, min_size=0, max_size=5))
    store = {}
    for key in keys:
        value = draw(st.text() | st.integers() | st.floats() | st.booleans())
        deadline = draw(st.integers(min_value=0, max_value=1000))
        store[key] = (value, deadline)
    return store


@st.composite
def cache_record_strategy(draw):
    """Generate a cache record (value, deadline) tuple."""
    value = draw(st.text() | st.integers() | st.floats() | st.booleans())
    deadline = draw(st.integers(min_value=0, max_value=1000))
    return (value, deadline)


class TestCachedInventory:
    """Test class for cached_inventory function semantic properties."""

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_default_on_missing_key(self, store, key, now, default):
        """
        Branch property: When record is None, return default.
        Formal: cached_inventory(store, key, now, default=default) == default
        """
        # Ensure key is not in store
        assume(key not in store)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == default

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_default_on_expired(self, store, key, now, default):
        """
        Branch property: When now > deadline, return default.
        Formal: cached_inventory(store, key, now, default=default) == default
        """
        # Ensure key exists with a deadline
        assume(key in store)
        value, deadline = store[key]
        assume(now > deadline)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == default

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_return_cached_value(self, store, key, now, default):
        """
        Branch property: When now <= deadline, return cached value.
        Formal: cached_inventory(store, key, now, default=default) == value
        """
        # Ensure key exists with a deadline
        assume(key in store)
        value, deadline = store[key]
        assume(now <= deadline)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == value

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_cache_hit_return(self, store, key, now, default):
        """
        Function property: Cache hit returns cached value.
        Precondition: record is not None and now <= deadline
        Formal: cached_inventory(store, key, now, default=default) == value
        """
        # Ensure cache hit condition
        assume(key in store)
        value, deadline = store[key]
        assume(now <= deadline)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == value

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_cache_miss_return(self, store, key, now, default):
        """
        Function property: Cache miss returns default.
        Precondition: record is None
        Formal: cached_inventory(store, key, now, default=default) == default
        """
        # Ensure cache miss condition
        assume(key not in store)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == default

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_expired_return(self, store, key, now, default):
        """
        Function property: Expired cache returns default.
        Precondition: record is not None and now > deadline
        Formal: cached_inventory(store, key, now, default=default) == default
        """
        # Ensure expired condition
        assume(key in store)
        value, deadline = store[key]
        assume(now > deadline)
        
        result = cached_inventory(store, key, now, default=default)
        assert result == default

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_boundary_value_valid(self, store, key, default):
        """
        Function property: Boundary value at deadline is valid.
        Precondition: record is not None and now == deadline
        Formal: cached_inventory(store, key, now, default=default) == value
        """
        # Ensure boundary condition
        assume(key in store)
        value, deadline = store[key]
        now = deadline  # Exact boundary
        
        result = cached_inventory(store, key, now, default=default)
        assert result == value

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=500),
        now2=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_monotonic_expiry(self, store, key, now1, now2, default):
        """
        Function property: Monotonic expiry behavior.
        Precondition: record is not None and now1 <= now2
        Formal: if cached_inventory(store, key, now1, default=default) == value 
                then cached_inventory(store, key, now2, default=default) == value
        """
        assume(key in store)
        value, deadline = store[key]
        assume(now1 <= now2)
        
        result1 = cached_inventory(store, key, now1, default=default)
        
        # If first call returned value, second call should also return value
        if result1 == value:
            result2 = cached_inventory(store, key, now2, default=default)
            assert result2 == value

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_idempotent(self, store, key, now, default):
        """
        Function property: Function is idempotent.
        Precondition: true
        Formal: cached_inventory(store, key, now, default=default) == cached_inventory(store, key, now, default=default)
        """
        result1 = cached_inventory(store, key, now, default=default)
        result2 = cached_inventory(store, key, now, default=default)
        assert result1 == result2

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.text() | st.integers() | st.floats() | st.booleans()
    )
    def test_read_only(self, store, key, now, default):
        """
        Function property: Function is read-only.
        Precondition: true
        Formal: store remains unchanged after calling cached_inventory
        """
        # Create a deep copy of the store to compare
        original_store = {k: v for k, v in store.items()}
        
        # Call the function
        result = cached_inventory(store, key, now, default=default)
        
        # Verify store is unchanged
        assert store == original_store
        assert len(store) == len(original_store)
        for k in original_store:
            assert k in store
            assert store[k] == original_store[k]