"""
Hypothesis tests for cached_preference function semantic properties.
Tests all 10 semantic properties identified in cached_preference_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Tuple, Any, Optional


def cached_preference(cache, key, now):
    """
    Fetch a memoized preference payload.
    """
    item = cache.get(key)
    if item is None:
        return None
    payload, ttl = item

    # BUG: should expire when now == ttl.
    if now > ttl:
        return None
    return payload


# Hypothesis strategies for generating test data
@st.composite
def cache_strategy(draw):
    """Generate a cache dictionary with key-payload-ttl tuples."""
    keys = draw(st.lists(st.text(min_size=1, max_size=10), unique=True, min_size=0, max_size=5))
    cache = {}
    for key in keys:
        payload = draw(st.text() | st.integers() | st.floats() | st.booleans())
        ttl = draw(st.integers(min_value=0, max_value=1000))
        cache[key] = (payload, ttl)
    return cache


@st.composite
def cache_record_strategy(draw):
    """Generate a cache record (payload, ttl) tuple."""
    payload = draw(st.text() | st.integers() | st.floats() | st.booleans())
    ttl = draw(st.integers(min_value=0, max_value=1000))
    return (payload, ttl)


class TestCachedPreference:
    """Test class for cached_preference function semantic properties."""

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_miss(self, cache, key, now):
        """
        Branch property: When item is None, return None.
        Condition: item is None
        Formal: cached_preference(cache, key, now) == None
        """
        # Ensure key is not in cache
        assume(key not in cache)
        
        result = cached_preference(cache, key, now)
        assert result is None

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_expired(self, cache, key, now):
        """
        Branch property: When now > ttl, return None.
        Condition: now > ttl
        Formal: cached_preference(cache, key, now) == None
        """
        # Ensure key exists with a ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now > ttl)
        
        result = cached_preference(cache, key, now)
        assert result is None

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_hit(self, cache, key, now):
        """
        Branch property: When now <= ttl, return payload.
        Condition: now <= ttl
        Formal: cached_preference(cache, key, now) == payload
        """
        # Ensure key exists with a ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = cached_preference(cache, key, now)
        assert result == payload

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_consistency(self, cache, key, now):
        """
        Function property: Cache consistency.
        Precondition: cache[key] exists and is valid
        Formal: cached_preference(cache, key, now) == cache[key][0]
        """
        # Ensure cache hit condition
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = cached_preference(cache, key, now)
        assert result == cache[key][0]

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=500),
        now2=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonic_expiry(self, cache, key, now1, now2):
        """
        Function property: Monotonic expiry.
        Precondition: cache[key] exists with ttl
        Formal: for all now1 <= now2, if cached_preference(cache, key, now1) == None then cached_preference(cache, key, now2) == None
        """
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now1 <= now2)
        
        result1 = cached_preference(cache, key, now1)
        
        # If first call returned None, second call should also return None
        if result1 is None:
            result2 = cached_preference(cache, key, now2)
            assert result2 is None

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_deterministic_lookup(self, cache, key, now):
        """
        Function property: Deterministic lookup.
        Precondition: cache, key, now are unchanged
        Formal: cached_preference(cache, key, now) == cached_preference(cache, key, now)
        """
        result1 = cached_preference(cache, key, now)
        result2 = cached_preference(cache, key, now)
        assert result1 == result2

    @given(
        cache=st.one_of(st.none(), st.dictionaries(st.text(), st.tuples(st.text() | st.integers() | st.floats() | st.booleans(), st.integers()))),
        key=st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_null_safety(self, cache, key, now):
        """
        Function property: Null safety.
        Precondition: cache is None or key is None
        Formal: cached_preference(cache, key, now) == None
        """
        # Only test when cache is None or key is None
        assume(cache is None or key is None)
        
        result = cached_preference(cache, key, now)
        assert result is None

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10)
    )
    def test_bug_invariant(self, cache, key):
        """
        Function property: Bug invariant.
        Precondition: cache[key] exists with ttl
        Formal: cached_preference(cache, key, ttl) == payload  # BUG: should return None
        """
        # Ensure key exists with a ttl
        assume(key in cache)
        payload, ttl = cache[key]
        
        # This tests the bug: at exact ttl boundary, it should return None but doesn't
        result = cached_preference(cache, key, ttl)
        assert result == payload  # This demonstrates the bug

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_payload_preservation(self, cache, key, now):
        """
        Function property: Payload preservation.
        Precondition: cache[key] exists and now <= ttl
        Formal: cached_preference(cache, key, now) == cache[key][0]
        """
        # Ensure cache hit condition
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = cached_preference(cache, key, now)
        assert result == cache[key][0]

    @given(
        cache=cache_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_ttl_preservation(self, cache, key, now):
        """
        Function property: TTL preservation.
        Precondition: cache[key] exists
        Formal: cached_preference(cache, key, now) depends only on cache[key][1] for expiry
        """
        # Ensure key exists
        assume(key in cache)
        payload, ttl = cache[key]
        
        # Test that the result depends only on the ttl value
        result = cached_preference(cache, key, now)
        
        # If now <= ttl, should return payload; otherwise None
        if now <= ttl:
            assert result == payload
        else:
            assert result is None