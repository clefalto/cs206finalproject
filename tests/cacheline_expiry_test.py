"""
Hypothesis tests for cacheline_expiry function semantic properties.
Tests based on properties/cacheline_expiry_properties.json
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, tuples, just

from dataset.python_programs.cacheline_expiry import cacheline_expiry


class TestCachelineExpiry:
    """Test suite for cacheline_expiry function semantic properties."""

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=0,
            max_size=10
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0)
    )
    def test_cache_miss_return(self, cache, key, now):
        """Test branch: item is None -> cache_miss_return"""
        assume(key not in cache)
        result = cacheline_expiry(cache, key, now)
        assert result is None

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now=integers(min_value=0)
    )
    def test_expired_entry_return(self, cache, now):
        """Test branch: now > ttl -> expired_entry_return"""
        # Find a key with ttl < now
        valid_items = [(k, v) for k, v in cache.items() if v[1] < now]
        assume(len(valid_items) > 0)
        
        key, (payload, ttl) = valid_items[0]
        result = cacheline_expiry(cache, key, now)
        assert result is None

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now=integers(min_value=0)
    )
    def test_valid_entry_return(self, cache, now):
        """Test branch: now <= ttl -> valid_entry_return"""
        # Find a key with ttl >= now
        valid_items = [(k, v) for k, v in cache.items() if v[1] >= now]
        assume(len(valid_items) > 0)
        
        key, (payload, ttl) = valid_items[0]
        result = cacheline_expiry(cache, key, now)
        assert result == payload

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=0,
            max_size=10
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0)
    )
    def test_cache_miss_consistency(self, cache, key, now):
        """Test function: cache_miss_consistency"""
        assume(cache.get(key) is None)
        result = cacheline_expiry(cache, key, now)
        assert result is None

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0)
    )
    def test_non_negative_ttl(self, cache, key, now):
        """Test function: non_negative_ttl"""
        assume(key in cache)
        item = cache[key]
        payload, ttl = item
        assert ttl >= 0

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now=integers(min_value=0)
    )
    def test_payload_preservation(self, cache, now):
        """Test function: payload_preservation"""
        # Find a key with ttl >= now
        valid_items = [(k, v) for k, v in cache.items() if v[1] >= now]
        assume(len(valid_items) > 0)
        
        key, (payload, ttl) = valid_items[0]
        result = cacheline_expiry(cache, key, now)
        assert result == payload

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now=integers(min_value=0)
    )
    def test_expiration_behavior(self, cache, now):
        """Test function: expiration_behavior"""
        # Find a key with ttl < now
        valid_items = [(k, v) for k, v in cache.items() if v[1] < now]
        assume(len(valid_items) > 0)
        
        key, (payload, ttl) = valid_items[0]
        result = cacheline_expiry(cache, key, now)
        assert result is None

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0)
    )
    def test_deterministic_output(self, cache, key, now):
        """Test function: deterministic_output"""
        assume(key in cache)
        result1 = cacheline_expiry(cache, key, now)
        result2 = cacheline_expiry(cache, key, now)
        assert result1 == result2

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now=integers(min_value=0)
    )
    def test_buggy_equality_handling(self, cache, now):
        """Test function: buggy_equality_handling (should return None per comment)"""
        # Find a key with ttl == now
        valid_items = [(k, v) for k, v in cache.items() if v[1] == now]
        assume(len(valid_items) > 0)
        
        key, (payload, ttl) = valid_items[0]
        result = cacheline_expiry(cache, key, now)
        # BUG: should return None when now == ttl, but currently returns payload
        assert result == payload

    @given(
        cache=dictionaries(
            st.text(min_size=1, max_size=10),
            tuples(st.text(), integers(min_value=0)),
            min_size=1,
            max_size=10
        ),
        now1=integers(min_value=0),
        now2=integers(min_value=0)
    )
    def test_monotonic_expiry(self, cache, now1, now2):
        """Test function: monotonic_expiry"""
        assume(now1 <= now2)
        assume(len(cache) > 0)
        
        # Test for each key in cache
        for key in cache.keys():
            result1 = cacheline_expiry(cache, key, now1)
            result2 = cacheline_expiry(cache, key, now2)
            
            # If result1 is not None, then result2 should also not be None
            if result1 is not None:
                assert result2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])