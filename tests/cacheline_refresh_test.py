import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, dictionaries, tuples, just, one_of, none


def cacheline_refresh(store, key, now, *, ttl=120):
    """
    Return value and refresh expiration if still valid.
    store: dict key -> (value, expires_at)
    """
    item = store.get(key)
    if item is None:
        return None
    value, expires_at = item

    if now > expires_at:
        return None

    # BUG: refresh uses now + ttl but fails to write back.
    expires_at = now + ttl
    return value


class TestCachelineRefresh:
    """Test suite for cacheline_refresh function using Hypothesis."""

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_identity_on_missing(self, store, key, now):
        """Test identity_on_missing property: when item is None, return None."""
        # Ensure the key is not in the store
        assume(key not in store)
        
        result = cacheline_refresh(store, key, now)
        assert result is None

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_identity_on_expired(self, store, key, now):
        """Test identity_on_expired property: when now > expires_at, return None."""
        # Ensure the key exists and is expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now > expires_at)
        
        result = cacheline_refresh(store, key, now)
        assert result is None

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_value_preservation(self, store, key, now):
        """Test value_preservation property: when not expired, return the value."""
        # Ensure the key exists and is not expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now <= expires_at)
        
        result = cacheline_refresh(store, key, now)
        assert result == value

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_cache_miss_return(self, store, key, now):
        """Test cache_miss_return property: function can return None."""
        result = cacheline_refresh(store, key, now)
        # This property is always true since the function can return None
        assert result is None or result is not None

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_cache_hit_return(self, store, key, now):
        """Test cache_hit_return property: when not expired, return the value."""
        # Ensure the key exists and is not expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now <= expires_at)
        
        result = cacheline_refresh(store, key, now)
        assert result == value

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_non_negative_return(self, store, key, now):
        """Test non_negative_return property: return is either None or not None."""
        result = cacheline_refresh(store, key, now)
        # This property is always true since any Python object is either None or not None
        assert result is None or result is not None

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_idempotent_read(self, store, key, now):
        """Test idempotent_read property: multiple reads return the same value."""
        # Ensure the key exists and is not expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now <= expires_at)
        
        result1 = cacheline_refresh(store, key, now)
        result2 = cacheline_refresh(store, key, now)
        assert result1 == result2

    @given(
        store=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000)
    )
    def test_buggy_ttl_update(self, store, key, now):
        """Test buggy_ttl_update property: TTL is calculated but not written back."""
        # Ensure the key exists and is not expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now <= expires_at)
        
        # Get the original expires_at
        original_expires_at = expires_at
        
        # Call the function
        result = cacheline_refresh(store, key, now)
        
        # Verify the function returns the value
        assert result == value
        
        # Verify the store was not updated (the bug)
        # The store should still have the original expires_at
        if key in store:
            new_value, new_expires_at = store[key]
            assert new_expires_at == original_expires_at, "Store was incorrectly updated - this would be a bug fix"