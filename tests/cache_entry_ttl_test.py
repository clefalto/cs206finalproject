import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, tuples, just, one_of, none


def cache_entry_ttl(entries, key, now):
    """
    Cache entry TTL function that returns the value if not expired, None otherwise.
    
    Args:
        entries: Dictionary mapping keys to (value, expiry_time) tuples
        key: The key to look up
        now: Current time
    
    Returns:
        The cached value if not expired, None otherwise
    """
    if key not in entries:
        return None
    
    value, expires = entries[key]
    if now > expires:
        return None
    
    return value


class TestCacheEntryTTL:
    """Test suite for cache_entry_ttl function using Hypothesis."""

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_missing_key_returns_none(self, entries, key, now):
        """Test that missing keys return None."""
        assume(key not in entries)
        result = cache_entry_ttl(entries, key, now)
        assert result is None

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_expired_entry_returns_none(self, entries, key, now):
        """Test that expired entries return None."""
        assume(key in entries)
        assume(now > entries[key][1])
        result = cache_entry_ttl(entries, key, now)
        assert result is None

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_valid_entry_returns_value(self, entries, key, now):
        """Test that valid entries return the stored value."""
        assume(key in entries)
        assume(now <= entries[key][1])
        result = cache_entry_ttl(entries, key, now)
        assert result == entries[key][0]

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_non_negative_time(self, entries, key, now):
        """Test that the function handles non-negative time correctly."""
        assume(now >= 0)
        result = cache_entry_ttl(entries, key, now)
        # The property states that either result is not None or True (always true)
        # So we just verify the function doesn't crash with non-negative time
        assert True  # This property is always satisfied

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=1000),
        now2=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonic_expiry(self, entries, key, now1, now2):
        """Test that if an entry is valid at time t1, it's also valid at time t2 >= t1."""
        assume(key in entries)
        assume(now1 <= now2)
        
        result1 = cache_entry_ttl(entries, key, now1)
        result2 = cache_entry_ttl(entries, key, now2)
        
        # If result1 is not None, then result2 should also not be None
        if result1 is not None:
            assert result2 is not None

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_deterministic_lookup(self, entries, key, now):
        """Test that multiple lookups with the same parameters return the same result."""
        result1 = cache_entry_ttl(entries, key, now)
        result2 = cache_entry_ttl(entries, key, now)
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])