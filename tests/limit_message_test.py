"""
Hypothesis-based tests for the limit_message function semantic properties.

This test file verifies all semantic properties identified in limit_message_properties.json
using the Hypothesis testing framework to generate comprehensive test cases.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple


def limit_message(timestamps: List[int], now: int, limit: int, window: int) -> Tuple[bool, int]:
    """
    Rate limiting function that checks if a message should be allowed based on recent timestamps.
    
    Args:
        timestamps: List of recent message timestamps
        now: Current timestamp
        limit: Maximum number of messages allowed in the window
        window: Time window in seconds
    
    Returns:
        Tuple of (allowed: bool, remaining: int)
    """
    # Filter timestamps within the window
    recent = [t for t in timestamps if now - t <= window]
    
    if len(recent) > limit:
        return False, 0
    else:
        return True, limit - len(recent)


class TestLimitMessageProperties:
    """Test class for limit_message semantic properties."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boolean_status(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that limit_message returns a boolean status indicating if message is allowed."""
        status, remaining = limit_message(timestamps, now, limit, window)
        assert isinstance(status, bool), f"Status should be boolean, got {type(status)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_remaining_count_non_negative(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that remaining count is always non-negative."""
        status, remaining = limit_message(timestamps, now, limit, window)
        assert remaining >= 0, f"Remaining count should be non-negative, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_returns_tuple(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that limit_message returns a tuple of exactly 2 elements."""
        result = limit_message(timestamps, now, limit, window)
        assert isinstance(result, tuple), f"Result should be tuple, got {type(result)}"
        assert len(result) == 2, f"Result should have exactly 2 elements, got {len(result)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_status_boolean_type(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that the status element is of type bool."""
        status, remaining = limit_message(timestamps, now, limit, window)
        assert isinstance(status, bool), f"Status should be bool, got {type(status)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_remaining_integer_type(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that the remaining element is of type int."""
        status, remaining = limit_message(timestamps, now, limit, window)
        assert isinstance(remaining, int), f"Remaining should be int, got {type(remaining)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_limit_respects_capacity(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that remaining count never exceeds the limit."""
        status, remaining = limit_message(timestamps, now, limit, window)
        assert remaining <= limit, f"Remaining should not exceed limit, got remaining={remaining}, limit={limit}"

    @given(
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100, deadline=None)
    def test_empty_window_allowed(self, limit: int, window: int):
        """Test that empty window always allows messages."""
        timestamps = []
        now = 1000
        status, remaining = limit_message(timestamps, now, limit, window)
        assert status is True, "Empty window should always allow messages"
        assert remaining == limit, f"Remaining should equal limit for empty window, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_exceeds_limit_blocked(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that exceeding limit blocks messages."""
        # Filter timestamps to only those within the window
        recent = [t for t in timestamps if now - t <= window]
        
        if len(recent) > limit:
            status, remaining = limit_message(timestamps, now, limit, window)
            assert status is False, "Should block when exceeding limit"
            assert remaining == 0, f"Remaining should be 0 when blocked, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_idempotency(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that same inputs always produce same outputs."""
        result1 = limit_message(timestamps, now, limit, window)
        result2 = limit_message(timestamps, now, limit, window)
        assert result1 == result2, f"Function should be idempotent, got {result1} != {result2}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_deterministic(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that same inputs always produce same outputs (deterministic property)."""
        results = []
        for _ in range(5):  # Test multiple times with same inputs
            results.append(limit_message(timestamps, now, limit, window))
        
        # All results should be identical
        assert all(result == results[0] for result in results), "Function should be deterministic"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=1, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_monotonic_remaining(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that if recent count increases, remaining decreases or stays same."""
        recent = [t for t in timestamps if now - t <= window]
        
        if len(recent) > 0:
            # Test with one fewer recent timestamp
            reduced_timestamps = timestamps[:-1]
            status1, remaining1 = limit_message(reduced_timestamps, now, limit, window)
            status2, remaining2 = limit_message(timestamps, now, limit, window)
            
            # When we add more recent timestamps, remaining should decrease or stay same
            assert remaining2 <= remaining1, f"Remaining should be monotonic, got {remaining2} > {remaining1}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_boundary_conditions(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test boundary conditions: empty window and exceeding limit."""
        recent = [t for t in timestamps if now - t <= window]
        
        # Test empty window condition
        if len(recent) == 0:
            status, remaining = limit_message(timestamps, now, limit, window)
            assert remaining == limit, f"Empty window should have remaining == limit, got {remaining}"
        
        # Test exceeding limit condition
        if len(recent) >= limit:
            status, remaining = limit_message(timestamps, now, limit, window)
            assert status is False, "Should block when exceeding or equaling limit"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_exceeded_branch(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test the branch where len(recent) > limit returns (False, 0)."""
        recent = [t for t in timestamps if now - t <= window]
        
        if len(recent) > limit:
            status, remaining = limit_message(timestamps, now, limit, window)
            assert status is False, "Should return False when exceeding limit"
            assert remaining == 0, f"Should return 0 remaining when exceeding limit, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_rate_limit_allowed_branch(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test the branch where not (len(recent) > limit) returns (True, limit - len(recent))."""
        recent = [t for t in timestamps if now - t <= window]
        
        if not (len(recent) > limit):
            status, remaining = limit_message(timestamps, now, limit, window)
            assert status is True, "Should return True when not exceeding limit"
            expected_remaining = limit - len(recent)
            assert remaining == expected_remaining, f"Expected remaining {expected_remaining}, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_remaining_calculation(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that remaining calculation is correct: limit - len(recent)."""
        recent = [t for t in timestamps if now - t <= window]
        
        status, remaining = limit_message(timestamps, now, limit, window)
        
        if len(recent) <= limit:
            expected_remaining = limit - len(recent)
            assert remaining == expected_remaining, f"Expected remaining {expected_remaining}, got {remaining}"
        else:
            assert remaining == 0, f"Should return 0 when exceeding limit, got {remaining}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000000)),
        now=st.integers(min_value=0, max_value=1000000),
        limit=st.integers(min_value=0, max_value=1000),
        window=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_status_logic(self, timestamps: List[int], now: int, limit: int, window: int):
        """Test that status logic is correct: True when not exceeding, False when exceeding."""
        recent = [t for t in timestamps if now - t <= window]
        
        status, remaining = limit_message(timestamps, now, limit, window)
        
        if len(recent) <= limit:
            assert status is True, "Should allow when not exceeding limit"
        else:
            assert status is False, "Should block when exceeding limit"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])