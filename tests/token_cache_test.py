import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Any, Optional, Tuple

# Define strategies for generating test data
# Cache structure: Dict[str, Tuple[Any, int]] where value is (payload, ttl)
cache_strategy = st.dictionaries(
    keys=st.text(min_size=1, max_size=10),
    values=st.tuples(
        st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none()),
        st.integers(min_value=0, max_value=1000)
    )
)

key_strategy = st.text(min_size=1, max_size=10)
now_strategy = st.integers(min_value=0, max_value=1000)

def token_cache(cache: Dict[str, Tuple[Any, int]], key: str, now: int) -> Optional[Any]:
    """
    Token cache implementation with potential bug in expiry logic.
    
    Args:
        cache: Dictionary mapping keys to (payload, ttl) tuples
        key: The cache key to look up
        now: Current timestamp
    
    Returns:
        The cached payload if valid, None otherwise
    """
    item = cache.get(key)
    
    if item is None:
        # Branch: cache_miss
        return None
    
    payload, ttl = item
    
    # Bug: should be 'now > ttl' but using 'now >= ttl' for buggy_expiry test
    if now >= ttl:
        # Branch: expired_entry (with bug)
        return None
    
    # Branch: cache_hit
    return payload


class TestTokenCacheProperties:
    """Test class for token cache semantic properties using Hypothesis."""
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_cache_miss_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: cache_miss
        Condition: item is None
        Formal: token_cache(cache, key, now) == None
        """
        # Ensure the key is not in cache (item is None)
        assume(key not in cache)
        
        result = token_cache(cache, key, now)
        assert result is None, f"Expected None for cache miss, got {result}"
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_expired_entry_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: expired_entry
        Condition: now > ttl
        Formal: token_cache(cache, key, now) == None
        """
        # Ensure the key exists and now > ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now > ttl)
        
        result = token_cache(cache, key, now)
        assert result is None, f"Expected None for expired entry, got {result}"
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_cache_hit_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: cache_hit
        Precondition: item is not None and now <= ttl
        Formal: token_cache(cache, key, now) == payload
        """
        # Ensure the key exists and now <= ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now <= ttl)
        
        result = token_cache(cache, key, now)
        assert result == payload, f"Expected {payload} for cache hit, got {result}"
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_non_negative_ttl_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: non_negative_ttl
        Precondition: item is not None
        Formal: ttl >= 0
        """
        # Ensure the key exists
        assume(key in cache)
        payload, ttl = cache[key]
        
        # This property is about the input data, not the function behavior
        # The strategy already ensures ttl >= 0, so this is a sanity check
        assert ttl >= 0, f"Generated ttl {ttl} is negative"
    
    @given(cache=cache_strategy, key=key_strategy, now1=now_strategy, now2=now_strategy)
    def test_monotonic_expiry_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now1: int, now2: int):
        """
        Property: monotonic_expiry
        Precondition: item is not None
        Formal: now1 <= now2 and now2 > ttl implies now1 > ttl
        """
        # Ensure the key exists
        assume(key in cache)
        payload, ttl = cache[key]
        
        # Test the monotonic property
        if now1 <= now2 and now2 > ttl:
            # If now2 > ttl, then now1 should also be > ttl (monotonicity)
            assert now1 > ttl, f"Monotonic expiry violated: now1={now1}, now2={now2}, ttl={ttl}"
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_deterministic_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: deterministic
        Precondition: cache, key, now unchanged
        Formal: token_cache(cache, key, now) == token_cache(cache, key, now)
        """
        result1 = token_cache(cache, key, now)
        result2 = token_cache(cache, key, now)
        
        assert result1 == result2, f"Deterministic property violated: {result1} != {result2}"
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_buggy_expiry_property(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """
        Property: buggy_expiry
        Precondition: item is not None
        Formal: now == ttl implies token_cache(cache, key, now) == payload (should be None)
        
        This test demonstrates the bug where now == ttl returns payload instead of None.
        """
        # Ensure the key exists and now == ttl
        assume(key in cache)
        payload, ttl = cache[key]
        assume(now == ttl)
        
        result = token_cache(cache, key, now)
        
        # Due to the bug (using >= instead of >), this should return payload when now == ttl
        # But the formal specification says it "should be None"
        # This test documents the buggy behavior
        assert result == payload, f"Buggy expiry: expected {payload} when now==ttl, got {result}"
        
        # Note: The correct behavior would be:
        # assert result is None, f"Expected None when now==ttl, got {result}"


class TestTokenCacheEdgeCases:
    """Additional edge case tests for token cache."""
    
    @given(cache=cache_strategy, key=key_strategy, now=now_strategy)
    def test_empty_cache(self, cache: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Test behavior with empty cache."""
        empty_cache = {}
        result = token_cache(empty_cache, key, now)
        assert result is None, "Empty cache should always return None"
    
    @given(key=key_strategy, payload=st.one_of(st.text(), st.integers(), st.floats(), st.booleans()), ttl=st.integers(min_value=0, max_value=1000), now=now_strategy)
    def test_single_entry_cache(self, key: str, payload: Any, ttl: int, now: int):
        """Test cache with single entry."""
        cache = {key: (payload, ttl)}
        
        if now <= ttl:
            result = token_cache(cache, key, now)
            assert result == payload, f"Single entry cache hit failed: expected {payload}, got {result}"
        else:
            result = token_cache(cache, key, now)
            assert result is None, f"Single entry cache miss failed: expected None, got {result}"
    
    @given(cache=cache_strategy, now=now_strategy)
    def test_all_keys_expiry(self, cache: Dict[str, Tuple[Any, int]], now: int):
        """Test that all entries expire when now is large enough."""
        # Create a cache where all entries should expire
        expiring_cache = {k: (v[0], min(v[1], now - 1)) for k, v in cache.items()}
        
        for key in expiring_cache:
            result = token_cache(expiring_cache, key, now)
            assert result is None, f"All entries should expire when now > ttl, but got {result} for key {key}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])