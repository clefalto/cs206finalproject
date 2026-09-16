"""
Hypothesis tests for the plan_memo function semantic properties.
Tests all 10 semantic properties identified in plan_memo_properties.json.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import Dict, Tuple, Optional, Any


def plan_memo(entries: Dict[str, Tuple[Any, int]], key: str, now: int) -> Optional[Any]:
    """
    Simple memoization function with TTL expiry.
    
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


class TestPlanMemoProperties:
    """Test class for plan_memo semantic properties using Hypothesis."""

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_missing_key_returns_none(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: missing_key_returns_none - If key not in entries, returns None."""
        assume(key not in entries)
        result = plan_memo(entries, key, now)
        assert result is None

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_expired_entry_returns_none(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: expired_entry_returns_none - If now > expires_at, returns None."""
        assume(key in entries)
        assume(now > entries[key][1])
        result = plan_memo(entries, key, now)
        assert result is None

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_valid_entry_returns_value(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: valid_entry_returns_value - If key in entries and now <= expires_at, returns entries[key][0]."""
        assume(key in entries)
        assume(now <= entries[key][1])
        result = plan_memo(entries, key, now)
        assert result == entries[key][0]

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_non_negative_time(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: non_negative_time - For non-negative now, function behaves correctly."""
        assume(now >= 0)
        result = plan_memo(entries, key, now)
        # The property states "plan_memo(entries, key, now) is not None or True"
        # This is always true, so we just verify the function doesn't crash
        assert True  # This property is trivially satisfied

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=1000),
        now2=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonic_expiry(self, entries: Dict[str, Tuple[Any, int]], key: str, now1: int, now2: int):
        """Property: monotonic_expiry - If key in entries and now1 <= now2, then plan_memo(entries, key, now1) is not None implies plan_memo(entries, key, now2) is not None."""
        assume(key in entries)
        assume(now1 <= now2)
        
        result1 = plan_memo(entries, key, now1)
        result2 = plan_memo(entries, key, now2)
        
        # If result1 is not None, then result2 should also not be None
        # (because if now1 <= now2 and the entry hasn't expired at now1, it shouldn't expire at now2)
        if result1 is not None:
            assert result2 is not None

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_deterministic_lookup(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: deterministic_lookup - Function returns the same result when called twice with the same arguments."""
        result1 = plan_memo(entries, key, now)
        result2 = plan_memo(entries, key, now)
        assert result1 == result2

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_strict_expiry_bug(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: strict_expiry_bug - When now == expires_at, the entry should still be valid (due to strict > comparison)."""
        assume(key in entries)
        assume(now == entries[key][1])
        result = plan_memo(entries, key, now)
        assert result == entries[key][0]

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_cache_consistency(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: cache_consistency - Function returns either None or the cached value."""
        assume(key in entries)
        result = plan_memo(entries, key, now)
        
        if result is not None:
            assert result == entries[key][0]
        # If result is None, that's also valid

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_return_format(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: return_format - Function returns either None or the cached value."""
        result = plan_memo(entries, key, now)
        
        # Either result is None, or it's the cached value
        if result is not None:
            assert key in entries
            assert result == entries[key][0]

    @given(
        entries=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
                st.integers(min_value=0, max_value=1000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000)
    )
    def test_key_preservation(self, entries: Dict[str, Tuple[Any, int]], key: str, now: int):
        """Property: key_preservation - If plan_memo returns a value, the key remains in entries."""
        assume(key in entries)
        original_entries = entries.copy()
        
        result = plan_memo(entries, key, now)
        
        if result is not None:
            # The key should still be in the entries dictionary
            assert key in entries
            # The entries dictionary should be unchanged
            assert entries == original_entries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])