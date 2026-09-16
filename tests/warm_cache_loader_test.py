import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Tuple, Any, Optional


def warm_cache_loader(cache: Dict[str, Tuple[Any, int]], key: str, now: int, ttl: int = 3600) -> Optional[Any]:
    """
    Load value from cache with TTL-based expiration and cache warming.
    
    Args:
        cache: Dictionary mapping keys to (value, expires_at) tuples
        key: The key to look up
        now: Current timestamp
        ttl: Time-to-live in seconds (default: 3600)
    
    Returns:
        The cached value if valid, None otherwise
    """
    item = cache.get(key)
    
    if item is None:
        return None
    
    value, expires_at = item
    
    if now > expires_at:
        return None
    
    # Cache warming: extend TTL
    new_expires_at = now + ttl
    cache[key] = (value, new_expires_at)
    
    return value


class TestWarmCacheLoader:
    """Test suite for warm_cache_loader function using Hypothesis."""

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=0,
            max_size=100
        ),
        st.text(min_size=1, max_size=10),
        st.integers(min_value=0, max_value=1000000)
    )
    def test_cache_miss_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Test cache_miss property: when item is None, function returns None."""
        assume(key not in cache)
        
        result = warm_cache_loader(cache, key, now)
        assert result is None, f"Expected None for missing key {key}, got {result}"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000)
    )
    def test_expired_entry_property(self, cache: Dict[str, Tuple[Any, int]], now: int):
        """Test expired_entry property: when now > expires_at, function returns None."""
        # Find a key with expired timestamp
        expired_keys = [k for k, (_, expires_at) in cache.items() if now > expires_at]
        
        if not expired_keys:
            pytest.skip("No expired entries in this test case")
        
        key = expired_keys[0]
        result = warm_cache_loader(cache, key, now)
        assert result is None, f"Expected None for expired key {key}, got {result}"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000)
    )
    def test_cache_hit_return_property(self, cache: Dict[str, Tuple[Any, int]], now: int):
        """Test cache_hit_return property: valid entries return their value."""
        # Find a key with valid timestamp
        valid_keys = [k for k, (_, expires_at) in cache.items() if now <= expires_at]
        
        if not valid_keys:
            pytest.skip("No valid entries in this test case")
        
        key = valid_keys[0]
        value, expires_at = cache[key]
        
        result = warm_cache_loader(cache, key, now)
        assert result == value, f"Expected {value} for key {key}, got {result}"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000)
    )
    def test_non_negative_expiry_property(self, cache: Dict[str, Tuple[Any, int]], now: int):
        """Test non_negative_expiry property: expires_at >= now for valid entries."""
        # Find a key with valid timestamp
        valid_keys = [k for k, (_, expires_at) in cache.items() if now <= expires_at]
        
        if not valid_keys:
            pytest.skip("No valid entries in this test case")
        
        key = valid_keys[0]
        value, expires_at = cache[key]
        
        # Call the function to trigger cache warming
        warm_cache_loader(cache, key, now)
        
        # Check that the new expiry is >= now
        new_value, new_expires_at = cache[key]
        assert new_expires_at >= now, f"Expected expires_at >= {now}, got {new_expires_at}"
        assert new_value == value, "Value should remain unchanged during cache warming"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000),
        st.integers(min_value=1, max_value=86400)  # TTL between 1 second and 24 hours
    )
    def test_ttl_extension_property(self, cache: Dict[str, Tuple[Any, int]], now: int, ttl: int):
        """Test ttl_extension property: expires_at == now + ttl for valid entries."""
        # Find a key with valid timestamp
        valid_keys = [k for k, (_, expires_at) in cache.items() if now <= expires_at]
        
        if not valid_keys:
            pytest.skip("No valid entries in this test case")
        
        key = valid_keys[0]
        value, expires_at = cache[key]
        
        # Call the function to trigger cache warming
        warm_cache_loader(cache, key, now, ttl)
        
        # Check that the new expiry equals now + ttl
        new_value, new_expires_at = cache[key]
        assert new_expires_at == now + ttl, f"Expected expires_at == {now + ttl}, got {new_expires_at}"
        assert new_value == value, "Value should remain unchanged during cache warming"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000),
        st.integers(min_value=1, max_value=86400)
    )
    def test_cache_consistency_property(self, cache: Dict[str, Tuple[Any, int]], now: int, ttl: int):
        """Test cache_consistency property: cache[key] == (value, expires_at) after warming."""
        # Find a key with valid timestamp
        valid_keys = [k for k, (_, expires_at) in cache.items() if now <= expires_at]
        
        if not valid_keys:
            pytest.skip("No valid entries in this test case")
        
        key = valid_keys[0]
        value, expires_at = cache[key]
        
        # Call the function to trigger cache warming
        warm_cache_loader(cache, key, now, ttl)
        
        # Check that cache entry is consistent
        stored_value, stored_expires_at = cache[key]
        assert stored_value == value, "Stored value should match original value"
        assert stored_expires_at == now + ttl, f"Stored expires_at should be {now + ttl}, got {stored_expires_at}"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)),
                st.integers(min_value=0, max_value=1000000)
            ),
            min_size=1,
            max_size=100
        ),
        st.integers(min_value=0, max_value=1000000),
        st.integers(min_value=1, max_value=86400)
    )
    def test_cache_warmup_property(self, cache: Dict[str, Tuple[Any, int]], now: int, ttl: int):
        """Test cache_warmup property: cache[key] == (value, now + ttl) after warming."""
        # Find a key with valid timestamp
        valid_keys = [k for k, (_, expires_at) in cache.items() if now <= expires_at]
        
        if not valid_keys:
            pytest.skip("No valid entries in this test case")
        
        key = valid_keys[0]
        value, expires_at = cache[key]
        
        # Call the function to trigger cache warming
        warm_cache_loader(cache, key, now, ttl)
        
        # Check that cache entry was properly warmed up
        stored_value, stored_expires_at = cache[key]
        assert stored_value == value, "Value should remain unchanged during cache warming"
        assert stored_expires_at == now + ttl, f"Cache should be warmed to {now + ttl}, got {stored_expires_at}"
        assert stored_expires_at > expires_at, "New expiry should be greater than old expiry"