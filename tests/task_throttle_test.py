import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import List, Tuple, Union

# Import the task_throttle function (assuming it's in the main module)
# from your_module import task_throttle

# Define strategies for generating test data
timestamp_strategy = st.integers(min_value=0, max_value=1000000000)
timestamps_strategy = st.lists(timestamp_strategy, min_size=0, max_size=100)
limit_strategy = st.integers(min_value=1, max_value=100)
now_strategy = st.integers(min_value=0, max_value=1000000000)


def task_throttle(timestamps: List[int], now: int, limit: int = 10) -> Tuple[bool, int]:
    """
    Throttle task execution based on recent timestamps.
    
    Args:
        timestamps: List of recent timestamps
        now: Current timestamp
        limit: Maximum number of recent tasks allowed
        
    Returns:
        Tuple of (allowed, remaining_count)
    """
    # Filter timestamps to only include recent ones (within last 60 seconds)
    recent = [t for t in timestamps if now - t <= 60]
    
    if len(recent) > limit:
        # Throttle when limit exceeded
        return (False, 0)
    else:
        # Allow when within limit
        remaining = limit - len(recent)
        return (True, remaining)


class TestTaskThrottleProperties:
    """Test class for task_throttle semantic properties using Hypothesis."""
    
    @given(timestamps=timestamps_strategy, now=now_strategy, limit=limit_strategy)
    def test_throttle_when_limit_exceeded(self, timestamps: List[int], now: int, limit: int):
        """
        Test property: throttle_when_limit_exceeded
        
        When the number of recent timestamps exceeds the limit,
        the function should return (False, 0).
        """
        # Filter timestamps to only include recent ones (within last 60 seconds)
        recent = [t for t in timestamps if now - t <= 60]
        
        # Only test when the condition is met
        assume(len(recent) > limit)
        
        result = task_throttle(timestamps, now, limit)
        assert result == (False, 0), f"Expected (False, 0) when limit exceeded, got {result}"
    
    @given(timestamps=timestamps_strategy, now=now_strategy, limit=limit_strategy)
    def test_allow_when_within_limit(self, timestamps: List[int], now: int, limit: int):
        """
        Test property: allow_when_within_limit
        
        When the number of recent timestamps is within the limit,
        the function should return (True, limit - len(recent)).
        """
        # Filter timestamps to only include recent ones (within last 60 seconds)
        recent = [t for t in timestamps if now - t <= 60]
        
        # Only test when the condition is met
        assume(not (len(recent) > limit))
        
        result = task_throttle(timestamps, now, limit)
        expected_remaining = limit - len(recent)
        assert result == (True, expected_remaining), f"Expected (True, {expected_remaining}) when within limit, got {result}"
    
    @given(timestamps=timestamps_strategy, now=now_strategy, limit=limit_strategy)
    def test_returns_boolean_and_count(self, timestamps: List[int], now: int, limit: int):
        """
        Test property: returns_boolean_and_count
        
        The function should always return a tuple with a boolean and an integer.
        """
        result = task_throttle(timestamps, now, limit)
        
        # Check that result is a tuple
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        
        # Check that tuple has exactly 2 elements
        assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
        
        # Check that first element is boolean
        assert isinstance(result[0], bool), f"Expected first element to be bool, got {type(result[0])}"
        
        # Check that second element is integer
        assert isinstance(result[1], int), f"Expected second element to be int, got {type(result[1])}"
    
    @given(timestamps=timestamps_strategy, now=now_strategy, limit=limit_strategy)
    def test_non_negative_remaining(self, timestamps: List[int], now: int, limit: int):
        """
        Test property: non_negative_remaining
        
        The remaining count should always be non-negative.
        """
        result = task_throttle(timestamps, now, limit)
        remaining = result[1]
        
        assert remaining >= 0, f"Expected non-negative remaining count, got {remaining}"
    
    @given(timestamps=timestamps_strategy, now=now_strategy, limit=limit_strategy)
    def test_remaining_within_limit(self, timestamps: List[int], now: int, limit: int):
        """
        Test property: remaining_within_limit
        
        The remaining count should never exceed the limit.
        """
        result = task_throttle(timestamps, now, limit)
        remaining = result[1]
        
        assert remaining <= limit, f"Expected remaining count <= limit ({limit}), got {remaining}"
    
    @given(
        timestamps1=timestamps_strategy,
        timestamps2=timestamps_strategy,
        now=now_strategy,
        limit=limit_strategy
    )
    def test_monotonic_remaining(self, timestamps1: List[int], timestamps2: List[int], now: int, limit: int):
        """
        Test property: monotonic_remaining
        
        For any two timestamps lists ts1 and ts2 where ts1 is a subset of ts2,
        task_throttle(ts1, now)[1] >= task_throttle(ts2, now)[1].
        
        This means adding more timestamps should never increase the remaining count.
        """
        # Filter timestamps to only include recent ones (within last 60 seconds)
        recent1 = [t for t in timestamps1 if now - t <= 60]
        recent2 = [t for t in timestamps2 if now - t <= 60]
        
        # Only test when ts1 is a subset of ts2
        assume(set(recent1).issubset(set(recent2)))
        
        result1 = task_throttle(timestamps1, now, limit)
        result2 = task_throttle(timestamps2, now, limit)
        
        remaining1 = result1[1]
        remaining2 = result2[1]
        
        assert remaining1 >= remaining2, f"Expected remaining count to be monotonic (ts1 subset of ts2), got {remaining1} < {remaining2}"


# Additional edge case tests
class TestTaskThrottleEdgeCases:
    """Additional tests for edge cases and specific scenarios."""
    
    def test_empty_timestamps(self):
        """Test with empty timestamps list."""
        result = task_throttle([], 100, 10)
        assert result == (True, 10)
    
    def test_single_timestamp(self):
        """Test with single timestamp."""
        result = task_throttle([50], 100, 10)
        assert result == (True, 9)
    
    def test_exactly_at_limit(self):
        """Test when recent timestamps exactly equal the limit."""
        timestamps = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]  # 10 timestamps within 60 seconds
        result = task_throttle(timestamps, 100, 10)
        assert result == (True, 0)
    
    def test_exceeds_limit(self):
        """Test when recent timestamps exceed the limit."""
        timestamps = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]  # 11 timestamps within 60 seconds
        result = task_throttle(timestamps, 100, 10)
        assert result == (False, 0)
    
    def test_old_timestamps_ignored(self):
        """Test that old timestamps (older than 60 seconds) are ignored."""
        timestamps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 1000]  # 1000 is too old
        result = task_throttle(timestamps, 100, 10)
        assert result == (True, 0)  # Only 10 recent timestamps count
    
    @given(now=now_strategy, limit=limit_strategy)
    def test_all_old_timestamps(self, now: int, limit: int):
        """Test with all old timestamps (should allow all)."""
        # Create timestamps that are all older than 60 seconds
        old_timestamps = [now - 100 - i for i in range(20)]
        result = task_throttle(old_timestamps, now, limit)
        assert result == (True, limit)
    
    @given(now=now_strategy, limit=limit_strategy)
    def test_all_recent_timestamps(self, now: int, limit: int):
        """Test with all recent timestamps (should be throttled)."""
        # Create timestamps that are all within 60 seconds
        recent_timestamps = [now - i for i in range(limit + 5)]
        result = task_throttle(recent_timestamps, now, limit)
        assert result == (False, 0)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])