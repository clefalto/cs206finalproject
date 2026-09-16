import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import Any, Dict, Tuple, Optional


# Mock store implementation for testing
class MockStore:
    def __init__(self):
        self.data = {}
    
    def get(self, key: str) -> Optional[Tuple[Any, int]]:
        return self.data.get(key)
    
    def set(self, key: str, value: Tuple[Any, int]) -> None:
        self.data[key] = value


def session_memo(store: MockStore, key: str, now: int, default: Any = None) -> Any:
    """
    Session memoization function that caches values with expiration.
    
    Args:
        store: A store object with get() and set() methods
        key: The cache key
        now: Current timestamp
        default: Default value to return if cache miss or expired
    
    Returns:
        Cached value if valid, otherwise default
    """
    record = store.get(key)
    if record is None:
        return default
    
    value, deadline = record
    if now > deadline:
        return default
    
    return value


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={},
    key="test_key",
    now=100,
    default="default_value"
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now=100,
    default="default_value"
)
@example(
    store_data={"test_key": ("cached_value", 150)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_cache_miss_return_default(store_data, key, now, default):
    """Test that cache miss returns default value."""
    store = MockStore()
    store.data = store_data
    
    # Only test when key is not in store
    if key not in store_data:
        result = session_memo(store, key, now, default=default)
        assert result == default, f"Expected default {default}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_expired_return_default(store_data, key, now, default):
    """Test that expired cache entries return default value."""
    store = MockStore()
    store.data = store_data
    
    # Only test when key exists and now > deadline
    if key in store_data:
        value, deadline = store_data[key]
        if now > deadline:
            result = session_memo(store, key, now, default=default)
            assert result == default, f"Expected default {default}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 150)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_valid_cache_return_value(store_data, key, now, default):
    """Test that valid cache entries return the cached value."""
    store = MockStore()
    store.data = store_data
    
    # Only test when key exists and now <= deadline
    if key in store_data:
        value, deadline = store_data[key]
        if now <= deadline:
            result = session_memo(store, key, now, default=default)
            assert result == value, f"Expected cached value {value}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 150)},
    key="test_key",
    now=100,
    default="default_value"
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_cache_consistency(store_data, key, now, default):
    """Test that cache consistency property holds."""
    store = MockStore()
    store.data = store_data
    
    if key in store_data:
        value, deadline = store_data[key]
        if now <= deadline:
            result = session_memo(store, key, now, default=default)
            assert result == value, f"Expected cached value {value}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={},
    key="test_key",
    now=100,
    default="default_value"
)
def test_default_on_miss(store_data, key, now, default):
    """Test that default is returned on cache miss."""
    store = MockStore()
    store.data = store_data
    
    if key not in store_data:
        result = session_memo(store, key, now, default=default)
        assert result == default, f"Expected default {default}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_default_on_expiry(store_data, key, now, default):
    """Test that default is returned when cache entry has expired."""
    store = MockStore()
    store.data = store_data
    
    if key in store_data:
        value, deadline = store_data[key]
        if now > deadline:
            result = session_memo(store, key, now, default=default)
            assert result == default, f"Expected default {default}, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 100)},
    key="test_key",
    now=100,
    default="default_value"
)
def test_boundary_value_bug(store_data, key, now, default):
    """Test boundary value behavior when now == deadline."""
    store = MockStore()
    store.data = store_data
    
    if key in store_data:
        value, deadline = store_data[key]
        if now == deadline:
            result = session_memo(store, key, now, default=default)
            assert result == value, f"Expected cached value {value} at boundary, got {result}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now1=st.integers(min_value=0, max_value=1000),
    now2=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now1=40,
    now2=100,
    default="default_value"
)
@example(
    store_data={"test_key": ("cached_value", 50)},
    key="test_key",
    now1=60,
    now2=100,
    default="default_value"
)
def test_monotonic_expiry(store_data, key, now1, now2, default):
    """Test monotonic expiry property."""
    assume(now1 <= now2)
    
    store = MockStore()
    store.data = store_data
    
    if key in store_data:
        value, deadline = store_data[key]
        if now2 > deadline:
            result2 = session_memo(store, key, now2, default=default)
            if result2 == default:
                result1 = session_memo(store, key, now1, default=default)
                # Either it's also expired at now1, or it was still valid
                assert result1 == default or result1 == value, \
                    f"Monotonic expiry violated: result1={result1}, result2={result2}, value={value}"


@given(
    store_data=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data={"test_key": ("cached_value", 150)},
    key="test_key",
    now=100,
    default="default_value"
)
@example(
    store_data={},
    key="test_key",
    now=100,
    default="default_value"
)
def test_idempotent_read(store_data, key, now, default):
    """Test that reading the same cache entry multiple times returns the same result."""
    store = MockStore()
    store.data = store_data
    
    result1 = session_memo(store, key, now, default=default)
    result2 = session_memo(store, key, now, default=default)
    
    assert result1 == result2, f"Idempotent read failed: result1={result1}, result2={result2}"


@given(
    store_data1=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    store_data2=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.tuples(
            st.one_of(st.integers(), st.text(), st.floats(), st.booleans()),
            st.integers(min_value=0, max_value=1000)
        )
    ),
    key=st.text(min_size=1, max_size=10),
    now=st.integers(min_value=0, max_value=1000),
    default=st.one_of(st.integers(), st.text(), st.floats(), st.booleans(), st.none())
)
@example(
    store_data1={"test_key": ("cached_value", 150)},
    store_data2={"test_key": ("cached_value", 150)},
    key="test_key",
    now=100,
    default="default_value"
)
@example(
    store_data1={},
    store_data2={},
    key="test_key",
    now=100,
    default="default_value"
)
def test_store_independence(store_data1, store_data2, key, now, default):
    """Test that function behavior is independent of store implementation when get() returns same values."""
    assume(key not in store_data1 or key not in store_data2 or store_data1[key] == store_data2[key])
    
    store1 = MockStore()
    store1.data = store_data1
    
    store2 = MockStore()
    store2.data = store_data2
    
    result1 = session_memo(store1, key, now, default=default)
    result2 = session_memo(store2, key, now, default=default)
    
    assert result1 == result2, f"Store independence failed: result1={result1}, result2={result2}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])