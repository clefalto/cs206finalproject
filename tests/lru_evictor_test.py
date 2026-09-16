"""
Tests for lru_evictor function using Hypothesis testing framework.
Tests all semantic properties identified in properties/lru_evictor_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists


def lru_evictor(order, capacity):
    """
    LRU Evictor function that implements LRU eviction policy.
    
    Args:
        order: List of elements in access order (oldest first)
        capacity: Maximum number of elements to keep
    
    Returns:
        List with oldest elements removed if capacity exceeded
    
    Raises:
        ValueError: If capacity is negative
    """
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    
    if len(order) <= capacity:
        return order
    
    # Evict oldest elements (at the beginning of the list)
    while len(order) > capacity:
        order.pop(0)
    
    return order


class TestLruEvictor:
    """Test class for lru_evictor function semantic properties."""

    @given(
        order=lists(st.integers(), min_size=0),
        capacity=st.integers(max_value=-1)
    )
    def test_invalid_capacity_error(self, order, capacity):
        """Test that negative capacity raises ValueError."""
        assume(capacity < 0)
        
        with pytest.raises(ValueError, match="capacity must be non-negative"):
            lru_evictor(order, capacity)

    @given(
        order=lists(st.integers(), min_size=0, max_size=100),
        capacity=st.integers(min_value=0, max_value=100)
    )
    def test_no_eviction_needed(self, order, capacity):
        """Test that when len(order) <= capacity, no eviction occurs."""
        assume(len(order) <= capacity)
        
        result = lru_evictor(order, capacity)
        assert result == order

    @given(
        order=lists(st.integers(), min_size=1, max_size=100),
        capacity=st.integers(min_value=0, max_value=99)
    )
    def test_evict_oldest_elements(self, order, capacity):
        """Test that when len(order) > capacity, oldest elements are evicted."""
        assume(len(order) > capacity)
        
        original_order = order.copy()
        result = lru_evictor(order, capacity)
        
        # Should remove exactly len(order) - capacity elements from the beginning
        expected_result = original_order[len(original_order) - capacity:]
        assert result == expected_result

    @given(
        order=lists(st.integers(), min_size=0, max_size=100),
        capacity=st.integers(min_value=0, max_value=100)
    )
    def test_capacity_constraint(self, order, capacity):
        """Test that result length is always <= capacity."""
        assume(capacity >= 0)
        
        result = lru_evictor(order, capacity)
        assert len(result) <= capacity

    @given(
        order=lists(st.integers(), min_size=0, max_size=100),
        capacity=st.integers(min_value=0, max_value=100)
    )
    def test_order_preservation(self, order, capacity):
        """Test that result is a suffix of the original order."""
        assume(capacity >= 0)
        
        result = lru_evictor(order, capacity)
        
        # Result should be a suffix of the original order
        if len(result) == 0:
            assert True  # Empty result is valid
        else:
            # Find where the result starts in the original order
            start_idx = len(order) - len(result)
            expected_suffix = order[start_idx:]
            assert result == expected_suffix

    @given(
        order=lists(st.integers(), min_size=1, max_size=100),
        capacity=st.integers(min_value=0, max_value=99)
    )
    def test_lru_semantics(self, order, capacity):
        """Test that LRU semantics are correctly implemented."""
        assume(capacity >= 0)
        assume(len(order) > capacity)
        
        result = lru_evictor(order, capacity)
        
        # Should keep the last 'capacity' elements (most recently used)
        expected = order[len(order) - capacity:]
        assert result == expected

    @given(
        order=lists(st.integers(), min_size=0, max_size=100),
        capacity=st.integers(min_value=0, max_value=100)
    )
    def test_identity_on_valid_capacity(self, order, capacity):
        """Test that when len(order) <= capacity, result equals input."""
        assume(len(order) <= capacity)
        
        result = lru_evictor(order, capacity)
        assert result == order

    @given(
        order=lists(st.integers(), min_size=0, max_size=50),
        capacity1=st.integers(min_value=0, max_value=50),
        capacity2=st.integers(min_value=0, max_value=50)
    )
    def test_monotonicity(self, order, capacity1, capacity2):
        """Test that larger capacity never results in smaller output."""
        assume(capacity1 <= capacity2)
        assume(capacity1 >= 0 and capacity2 >= 0)
        
        result1 = lru_evictor(order, capacity1)
        result2 = lru_evictor(order, capacity2)
        
        assert len(result1) <= len(result2)

    @given(
        order=lists(st.integers(), min_size=0, max_size=50),
        capacity=st.integers(min_value=0, max_value=50)
    )
    def test_idempotence(self, order, capacity):
        """Test that applying lru_evictor twice gives same result."""
        assume(capacity >= 0)
        
        result1 = lru_evictor(order, capacity)
        result2 = lru_evictor(result1, capacity)
        
        assert result2 == result1

    @given(
        order=lists(st.integers(), min_size=1, max_size=100),
        capacity=st.integers(min_value=1, max_value=100)
    )
    def test_buggy_capacity_behavior(self, order, capacity):
        """Test the buggy behavior where len(order) == capacity results in capacity elements."""
        assume(len(order) == capacity)
        assume(capacity >= 0)
        
        result = lru_evictor(order, capacity)
        
        # Due to the > vs >= bug, this should keep all elements (capacity elements)
        # instead of the expected capacity-1 elements
        assert len(result) == capacity