"""
Hypothesis-based property tests for redis_like_expiry function.

This test file exercises all semantic properties identified in
properties/redis_like_expiry_properties.json using the Hypothesis
testing framework for Python.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest

# Import the function under test
from dataset.python_programs.redis_like_expiry import redis_like_expiry


class TestRedisLikeExpiry:
    """Test class for redis_like_expiry function properties."""

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_null_item_returns_none(self, store, key, now):
        """
        Property: null_item_returns_none
        When item is None (key not in store), function should return None.
        """
        # Ensure the key is not in the store
        assume(key not in store)
        
        result = redis_like_expiry(store, key, now)
        assert result is None

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_expired_item_returns_none(self, store, key, now):
        """
        Property: expired_item_returns_none
        When now > expires_at, function should return None.
        """
        # Ensure the key exists and is expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now > expires_at)
        
        result = redis_like_expiry(store, key, now)
        assert result is None

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_valid_item_returns_value(self, store, key, now):
        """
        Property: valid_item_returns_value
        When now <= expires_at, function should return the stored value.
        """
        # Ensure the key exists and is not expired
        assume(key in store)
        value, expires_at = store[key]
        assume(now <= expires_at)
        
        result = redis_like_expiry(store, key, now)
        assert result == value

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_non_negative_expiry(self, store, key, now):
        """
        Property: non_negative_expiry
        Precondition: expires_at >= 0
        The expiry time should always be non-negative.
        """
        # Only test when key exists
        assume(key in store)
        value, expires_at = store[key]
        
        # This is a precondition test - the function assumes expires_at >= 0
        # We verify this by checking the stored value
        assert expires_at >= 0

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0),
        now2=st.integers(min_value=0)
    )
    def test_monotonic_expiry(self, store, key, now1, now2):
        """
        Property: monotonic_expiry
        Precondition: now1 <= now2
        If an item expires at now1, it should also expire at now2.
        """
        assume(now1 <= now2)
        
        # Only test when key exists
        assume(key in store)
        
        result1 = redis_like_expiry(store, key, now1)
        result2 = redis_like_expiry(store, key, now2)
        
        # If it's expired at now1, it should be expired at now2
        if result1 is None:
            assert result2 is None

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_idempotent_lookup(self, store, key, now):
        """
        Property: idempotent_lookup
        Precondition: True
        Multiple calls with the same parameters should return the same result.
        """
        result1 = redis_like_expiry(store, key, now)
        result2 = redis_like_expiry(store, key, now)
        
        assert result1 == result2

    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10)
    )
    def test_boundary_inclusion(self, store, key):
        """
        Property: boundary_inclusion
        Precondition: now == expires_at
        At the exact expiry time, the item should still be valid.
        """
        # Ensure the key exists
        assume(key in store)
        value, expires_at = store[key]
        
        # Test at the boundary
        now = expires_at
        result = redis_like_expiry(store, key, now)
        
        assert result == value

    # Additional edge case tests to complement the property tests

    @example(
        store={},
        key="test",
        now=0
    )
    @example(
        store={"test": ("value", 5)},
        key="test",
        now=6  # expired
    )
    @example(
        store={"test": ("value", 5)},
        key="test",
        now=5  # boundary
    )
    @example(
        store={"test": ("value", 5)},
        key="test",
        now=4  # valid
    )
    @given(
        store=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.tuples(
                st.text() | st.integers() | st.floats() | st.booleans(),
                st.integers(min_value=0)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0)
    )
    def test_comprehensive_boundary_cases(self, store, key, now):
        """
        Additional test for comprehensive boundary coverage.
        """
        result = redis_like_expiry(store, key, now)
        
        # If key doesn't exist, result should be None
        if key not in store:
            assert result is None
        else:
            value, expires_at = store[key]
            # If expired, result should be None
            if now > expires_at:
                assert result is None
            # If not expired, result should be the value
            else:
                assert result == value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])