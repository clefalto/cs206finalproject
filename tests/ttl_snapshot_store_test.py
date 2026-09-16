import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, tuples, just, one_of, none


def ttl_snapshot_store(entries, key, now):
    """
    TTL snapshot store function that returns the value if not expired, None otherwise.
    
    Args:
        entries: Dictionary mapping keys to (value, expiry_time) tuples
        key: The key to look up
        now: Current time
    
    Returns:
        The cached value if not expired, None otherwise
    """
    if key not in entries:
        return None
    
    value, expires_at = entries[key]
    if now > expires_at:
        return None
    
    return value


class TestTtlSnapshotStore:
    """Test suite for ttl_snapshot_store function using Hypothesis."""

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
    def test_key_not_found_returns_none(self, entries, key, now):
        """Test that missing keys return None (branch property: key_not_found)."""
        assume(key not in entries)
        result = ttl_snapshot_store(entries, key, now)
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
        """Test that expired entries return None (branch property: expired_entry)."""
        assume(key in entries)
        assume(now > entries[key][1])
        result = ttl_snapshot_store(entries, key, now)
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
    def test_key_not_found_returns_none_function_property(self, entries, key, now):
        """Test that missing keys return None (function property: key_not_found_returns_none)."""
        assume(key not in entries)
        result = ttl_snapshot_store(entries, key, now)
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
    def test_expired_entry_returns_none_function_property(self, entries, key, now):
        """Test that expired entries return None (function property: expired_entry_returns_none)."""
        assume(key in entries)
        assume(now > entries[key][1])
        result = ttl_snapshot_store(entries, key, now)
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
        """Test that valid entries return the stored value (function property: valid_entry_returns_value)."""
        assume(key in entries)
        assume(now <= entries[key][1])
        result = ttl_snapshot_store(entries, key, now)
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
    def test_idempotent(self, entries, key, now):
        """Test that the function is idempotent (function property: idempotent)."""
        assume(key in entries)
        assume(now <= entries[key][1])
        result1 = ttl_snapshot_store(entries, key, now)
        result2 = ttl_snapshot_store(entries, key, now)
        assert result1 == result2

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
    def test_deterministic(self, entries, key, now):
        """Test that the function is deterministic (function property: deterministic)."""
        assume(entries is not None)
        assume(key is not None)
        assume(now is not None)
        result1 = ttl_snapshot_store(entries, key, now)
        result2 = ttl_snapshot_store(entries, key, now)
        assert result1 == result2

    @given(
        entries=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            )
        )
    )
    def test_no_side_effects(self, entries):
        """Test that the function has no side effects (function property: no_side_effects)."""
        original_entries = entries.copy()
        # Try to call the function with any key and time
        if entries:
            key = list(entries.keys())[0]
            now = 0
            ttl_snapshot_store(entries, key, now)
        # Verify the original dictionary is unchanged
        assert entries == original_entries

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
        """Test that expiry is monotonic (function property: monotonic_expiry)."""
        assume(key in entries)
        assume(now1 <= now2)
        
        result1 = ttl_snapshot_store(entries, key, now1)
        result2 = ttl_snapshot_store(entries, key, now2)
        
        # If result1 is None (expired at now1), then result2 should also be None (expired at now2)
        if result1 is None:
            assert result2 is None

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
    def test_bug_expiry_strict(self, entries, key, now):
        """Test that entries are valid exactly at expiry time (function property: bug_expiry_strict)."""
        assume(key in entries)
        assume(now == entries[key][1])
        result = ttl_snapshot_store(entries, key, now)
        assert result == entries[key][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])