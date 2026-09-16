"""
Hypothesis tests for cached_route function semantic properties.
Tests all 12 semantic properties identified in cached_route_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Tuple, Any, Optional


def cached_route(entries, key, now):
    """
    Return cached route value unless expired.
    """
    if key not in entries:
        return None
    
    value, expires_at = entries[key]
    
    # BUG: boundary value at expires_at is treated as valid.
    if now > expires_at:
        return None
    return value


# Hypothesis strategies for generating test data
@st.composite
def entries_strategy(draw):
    """Generate an entries dictionary with key-value-expires_at tuples."""
    keys = draw(st.lists(st.text(min_size=1, max_size=10), unique=True, min_size=0, max_size=5))
    entries = {}
    for key in keys:
        value = draw(st.text() | st.integers() | st.floats() | st.booleans())
        expires_at = draw(st.integers(min_value=0, max_value=1000))
        entries[key] = (value, expires_at)
    return entries


class TestCachedRoute:
    """Test class for cached_route function semantic properties."""

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_miss_return_none_branch(self, entries, key, now):
        """
        Branch property: When key not in entries, return None.
        Formal: cached_route(entries, key, now) == None
        """
        # Ensure key is not in entries
        assume(key not in entries)
        
        result = cached_route(entries, key, now)
        assert result is None

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_expired_entry_return_none_branch(self, entries, key, now):
        """
        Branch property: When now > expires_at, return None.
        Formal: cached_route(entries, key, now) == None
        """
        # Ensure key exists with an expiration
        assume(key in entries)
        value, expires_at = entries[key]
        assume(now > expires_at)
        
        result = cached_route(entries, key, now)
        assert result is None

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_valid_entry_return_value_branch(self, entries, key, now):
        """
        Branch property: When now <= expires_at, return stored value.
        Formal: cached_route(entries, key, now) == entries[key][0]
        """
        # Ensure key exists with an expiration
        assume(key in entries)
        value, expires_at = entries[key]
        assume(now <= expires_at)
        
        result = cached_route(entries, key, now)
        assert result == value

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_hit_return_stored_value(self, entries, key, now):
        """
        Function property: Cache hit returns stored value.
        Precondition: key in entries and now <= entries[key][1]
        Formal: cached_route(entries, key, now) == entries[key][0]
        """
        # Ensure cache hit condition
        assume(key in entries)
        value, expires_at = entries[key]
        assume(now <= expires_at)
        
        result = cached_route(entries, key, now)
        assert result == value

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_miss_return_none_function(self, entries, key, now):
        """
        Function property: Cache miss returns None.
        Precondition: key not in entries
        Formal: cached_route(entries, key, now) == None
        """
        # Ensure cache miss condition
        assume(key not in entries)
        
        result = cached_route(entries, key, now)
        assert result is None

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_expired_entry_return_none_function(self, entries, key, now):
        """
        Function property: Expired entry returns None.
        Precondition: key in entries and now > entries[key][1]
        Formal: cached_route(entries, key, now) == None
        """
        # Ensure expired condition
        assume(key in entries)
        value, expires_at = entries[key]
        assume(now > expires_at)
        
        result = cached_route(entries, key, now)
        assert result is None

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10)
    )
    def test_non_negative_expiry(self, entries, key):
        """
        Function property: Expiry time is non-negative.
        Precondition: key in entries
        Formal: entries[key][1] >= 0
        """
        # Ensure key exists
        assume(key in entries)
        
        expires_at = entries[key][1]
        assert expires_at >= 0

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_deterministic_behavior(self, entries, key, now):
        """
        Function property: Function produces same result given identical inputs.
        Precondition: true
        Formal: cached_route(entries, key, now) produces the same result given identical inputs
        """
        result1 = cached_route(entries, key, now)
        result2 = cached_route(entries, key, now)
        assert result1 == result2

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_no_side_effects(self, entries, key, now):
        """
        Function property: Function does not modify entries or global state.
        Precondition: true
        Formal: cached_route(entries, key, now) does not modify entries or any global state
        """
        # Create a deep copy of entries to compare
        original_entries = {k: v for k, v in entries.items()}
        
        # Call the function
        result = cached_route(entries, key, now)
        
        # Verify entries is unchanged
        assert entries == original_entries
        assert len(entries) == len(original_entries)
        for k in original_entries:
            assert k in entries
            assert entries[k] == original_entries[k]

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10)
    )
    def test_buggy_expiry_behavior(self, entries, key):
        """
        Function property: Boundary value at expires_at is treated as valid (bug).
        Precondition: key in entries and now == entries[key][1]
        Formal: cached_route(entries, key, now) == entries[key][0] (should return None for expired entries)
        """
        # Ensure boundary condition
        assume(key in entries)
        value, expires_at = entries[key]
        now = expires_at  # Exact boundary
        
        result = cached_route(entries, key, now)
        # This test documents the buggy behavior where boundary values are treated as valid
        assert result == value

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        t1=st.integers(min_value=0, max_value=500),
        t2=st.integers(min_value=0, max_value=1000)
    )
    def test_metamorphic_relation_expiry(self, entries, key, t1, t2):
        """
        Function property: Metamorphic relation for expiry.
        Precondition: key in entries and t1 <= t2
        Formal: if cached_route(entries, key, t1) == None then cached_route(entries, key, t2) == None
        """
        assume(key in entries)
        assume(t1 <= t2)
        
        result1 = cached_route(entries, key, t1)
        
        # If first call returned None, second call should also return None
        if result1 is None:
            result2 = cached_route(entries, key, t2)
            assert result2 is None

    @given(
        entries=entries_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_metamorphic_relation_cache_miss(self, entries, key, now):
        """
        Function property: Metamorphic relation for cache miss.
        Precondition: key not in entries
        Formal: for all now: cached_route(entries, key, now) == None
        """
        # Ensure cache miss condition
        assume(key not in entries)
        
        result = cached_route(entries, key, now)
        assert result is None