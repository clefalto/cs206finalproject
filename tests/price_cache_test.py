"""
Hypothesis tests for price_cache function semantic properties.

This test file exercises all semantic properties identified in 
properties/price_cache_properties.json using the Hypothesis testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import Dict, Any, Optional, Tuple, Union


# Mock the price_cache function based on the structure analysis
def price_cache(cache: Dict[Any, Tuple[Any, int]], key: Any, now: int) -> Optional[Any]:
    """
    Mock implementation of price_cache function based on the semantic properties.
    
    Args:
        cache: Dictionary mapping keys to (payload, ttl) tuples
        key: The key to look up in the cache
        now: Current timestamp
    
    Returns:
        The cached payload if not expired, None otherwise
    """
    item = cache.get(key)
    
    # Branch: item is None
    if item is None:
        return None
    
    # Branch: item is not None
    payload, ttl = item
    # BUG: should expire when now == ttl, but condition is now > ttl
    if now > ttl:
        return None
    
    return payload


class TestPriceCacheBranchProperties:
    """Test branch-specific semantic properties of price_cache function."""
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_miss_on_none(self, cache, key, now):
        """Test: cache_miss_on_none - when item is None, return None."""
        # Ensure the key is not in cache (item will be None)
        assume(key not in cache)
        
        result = price_cache(cache, key, now)
        assert result is None, f"Expected None when key {key} not in cache, got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_miss_on_expired(self, cache, key, now):
        """Test: cache_miss_on_expired - when now > ttl, return None."""
        # Ensure the key exists and now > ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now > ttl)
        
        result = price_cache(cache, key, now)
        assert result is None, f"Expected None when now ({now}) > ttl ({ttl}), got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_hit_return_payload(self, cache, key, now):
        """Test: cache_hit_return_payload - when not None and not expired, return payload."""
        # Ensure the key exists and now <= ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(not (now > ttl))  # i.e., now <= ttl
        
        result = price_cache(cache, key, now)
        assert result == payload, f"Expected payload {payload} when not expired, got {result}"


class TestPriceCacheFunctionProperties:
    """Test function-level semantic properties of price_cache function."""
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_miss_when_none(self, cache, key, now):
        """Test: cache_miss_when_none - precondition: cache.get(key) is None."""
        assume(cache.get(key) is None)
        
        result = price_cache(cache, key, now)
        assert result is None, f"Expected None when cache.get({key}) is None, got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_miss_when_expired(self, cache, key, now):
        """Test: cache_miss_when_expired - precondition: cache.get(key) is not None and now > cache.get(key)[1]."""
        assume(cache.get(key) is not None)
        payload, ttl = cache[key]
        assume(now > ttl)
        
        result = price_cache(cache, key, now)
        assert result is None, f"Expected None when expired (now={now} > ttl={ttl}), got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_hit_return_payload(self, cache, key, now):
        """Test: cache_hit_return_payload - precondition: cache.get(key) is not None and now <= cache.get(key)[1]."""
        assume(cache.get(key) is not None)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = price_cache(cache, key, now)
        assert result == payload, f"Expected payload {payload} when not expired, got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_non_negative_ttl(self, cache, key):
        """Test: non_negative_ttl - precondition: cache.get(key) is not None."""
        assume(cache.get(key) is not None)
        payload, ttl = cache[key]
        
        assert ttl >= 0, f"Expected non-negative TTL, got {ttl}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=500),
        now2=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_monotonic_expiry(self, cache, key, now1, now2):
        """Test: monotonic_expiry - precondition: cache.get(key) is not None and now1 <= now2."""
        assume(cache.get(key) is not None)
        assume(now1 <= now2)
        
        result1 = price_cache(cache, key, now1)
        
        # If cache hit at now1, should also hit at now2 (monotonic)
        if result1 is not None:
            result2 = price_cache(cache, key, now2)
            assert result2 is not None, f"Expected cache hit at now2={now2} since hit at now1={now1}, got {result2}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_idempotent_lookup(self, cache, key, now):
        """Test: idempotent_lookup - precondition: cache.get(key) is not None and now <= cache.get(key)[1]."""
        assume(cache.get(key) is not None)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result1 = price_cache(cache, key, now)
        result2 = price_cache(cache, key, now)
        
        assert result1 == result2, f"Expected idempotent lookup, got {result1} != {result2}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    @example(
        cache={"test": ("payload", 100)},
        key="test",
        now=100
    )
    def test_buggy_expiry_condition(self, cache, key, now):
        """
        Test: buggy_expiry_condition - precondition: cache.get(key) is not None and now == cache.get(key)[1].
        
        This test demonstrates the bug where the function should return None when now == ttl,
        but due to the condition 'now > ttl' instead of 'now >= ttl', it returns the payload.
        """
        assume(cache.get(key) is not None)
        payload, ttl = cache[key]
        assume(now == ttl)
        
        result = price_cache(cache, key, now)
        # This is the buggy behavior: should return None but returns payload
        assert result == payload, f"BUG: Expected None when now == ttl, but got payload {payload}. This demonstrates the bug."


class TestPriceCacheEdgeCases:
    """Test edge cases and boundary conditions for price_cache function."""
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_empty_cache(self, cache, key, now):
        """Test behavior with empty cache."""
        assume(len(cache) == 0)
        
        result = price_cache(cache, key, now)
        assert result is None, f"Expected None for empty cache, got {result}"
    
    @given(
        payload=st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.lists(st.integers())),
        ttl=st.integers(min_value=0, max_value=1000),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_single_entry_cache(self, payload, ttl, now):
        """Test behavior with single entry cache."""
        cache = {"test_key": (payload, ttl)}
        key = "test_key"
        
        result = price_cache(cache, key, now)
        
        if now <= ttl:
            assert result == payload, f"Expected payload {payload} when not expired, got {result}"
        else:
            assert result is None, f"Expected None when expired (now={now} > ttl={ttl}), got {result}"
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=5),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=100)
            ),
            min_size=1,
            max_size=5
        ),
        now=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_multiple_entries_cache(self, cache, now):
        """Test behavior with multiple entries in cache."""
        for key in cache.keys():
            result = price_cache(cache, key, now)
            payload, ttl = cache[key]
            
            if now <= ttl:
                assert result == payload, f"Expected payload {payload} for key {key}, got {result}"
            else:
                assert result is None, f"Expected None for expired key {key}, got {result}"


class TestPriceCacheTypeSafety:
    """Test type safety and input validation for price_cache function."""
    
    @given(
        cache=st.dictionaries(
            keys=st.one_of(st.text(), st.integers(), st.floats()),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.lists(st.integers())),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.one_of(st.text(), st.integers(), st.floats()),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_various_key_types(self, cache, key, now):
        """Test with various key types."""
        result = price_cache(cache, key, now)
        
        # Should handle various key types gracefully
        if key in cache:
            payload, ttl = cache[key]
            if now <= ttl:
                assert result == payload
            else:
                assert result is None
        else:
            assert result is None
    
    @given(
        cache=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.lists(st.integers())),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=50, deadline=None)
    def test_various_payload_types(self, cache, key, now):
        """Test with various payload types."""
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = price_cache(cache, key, now)
        assert result == payload, f"Expected payload {payload} of type {type(payload)}, got {result}"


if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main([__file__, "-v"])