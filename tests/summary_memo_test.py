import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import Dict, Tuple, Optional, Any


def summary_memo(entries: Dict[str, Tuple[Any, int]], key: str, now: int) -> Optional[Any]:
    """
    A memoization function that caches results with expiration times.
    
    Args:
        entries: Dictionary mapping keys to (value, expires_at) tuples
        key: The key to look up
        now: Current timestamp
    
    Returns:
        The cached value if it exists and hasn't expired, otherwise None
    """
    if key not in entries:
        return None
    
    value, expires_at = entries[key]
    if now > expires_at:
        return None
    
    return value


class TestSummaryMemo:
    """Test suite for the summary_memo function using Hypothesis."""

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_miss_when_key_not_in_entries(self, entries, key, now):
        """Test that summary_memo returns None when key is not in entries."""
        assume(key not in entries)
        
        result = summary_memo(entries, key, now)
        assert result is None

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_expired_entry_returns_none(self, entries, key, now):
        """Test that summary_memo returns None when entry has expired."""
        assume(key in entries)
        
        value, expires_at = entries[key]
        assume(now > expires_at)
        
        result = summary_memo(entries, key, now)
        assert result is None

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_hit_returns_correct_value(self, entries, key, now):
        """Test that summary_memo returns the correct cached value when not expired."""
        assume(key in entries)
        
        value, expires_at = entries[key]
        assume(now <= expires_at)
        
        result = summary_memo(entries, key, now)
        assert result == value

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10)
    )
    def test_non_negative_expiry_time(self, entries, key):
        """Test that expiry times are non-negative when key exists in entries."""
        assume(key in entries)
        
        value, expires_at = entries[key]
        assert expires_at >= 0

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_deterministic_behavior(self, entries, key, now):
        """Test that summary_memo produces deterministic results for same inputs."""
        result1 = summary_memo(entries, key, now)
        result2 = summary_memo(entries, key, now)
        
        assert result1 == result2

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=1000),
        now2=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonic_expiry(self, entries, key, now1, now2):
        """Test that if an entry expires at now1, it also expires at any later time now2."""
        assume(key in entries)
        assume(now1 <= now2)
        
        result1 = summary_memo(entries, key, now1)
        
        # If the entry has expired at now1, it should also be expired at now2
        if result1 is None:
            result2 = summary_memo(entries, key, now2)
            assert result2 is None

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_function_returns_expected_types(self, entries, key, now):
        """Test that summary_memo returns either a string value or None."""
        result = summary_memo(entries, key, now)
        
        # Result should be either None or a string (the cached value)
        assert result is None or isinstance(result, str)

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_empty_entries_behavior(self, entries, key, now):
        """Test behavior with empty entries dictionary."""
        assume(len(entries) == 0)
        
        result = summary_memo(entries, key, now)
        assert result is None

    @given(
        entries=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.tuples(st.text(), st.integers(min_value=0, max_value=1000))
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_multiple_entries_behavior(self, entries, key, now):
        """Test that function correctly handles multiple entries in the cache."""
        assume(len(entries) > 1)
        assume(key in entries)
        
        value, expires_at = entries[key]
        assume(now <= expires_at)
        
        result = summary_memo(entries, key, now)
        assert result == value
        
        # Verify other entries are not affected
        for other_key in entries:
            if other_key != key:
                other_value, other_expires_at = entries[other_key]
                other_result = summary_memo(entries, other_key, now)
                if now <= other_expires_at:
                    assert other_result == other_value
                else:
                    assert other_result is None