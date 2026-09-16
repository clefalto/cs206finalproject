import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.limit_query import limit_query


class TestLimitQueryProperties:
    """Test suite for limit_query semantic properties using Hypothesis."""

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_rate_limited_branch(self, timestamps, now, window, limit):
        """Test the rate_limited branch property: when len(active) > limit, return (False, 0)."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Filter timestamps to get active ones
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition len(active) > limit is met
        assume(len(active) > limit)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_quota_available_branch(self, timestamps, now, window, limit):
        """Test the quota_available branch property: when len(active) <= limit, return (True, limit - len(active))."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Filter timestamps to get active ones
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition len(active) <= limit is met
        assume(len(active) <= limit)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        expected_quota = limit - len(active)
        assert result == (True, expected_quota), f"Expected (True, {expected_quota}) when len(active)={len(active)} <= limit={limit}, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_non_negative_quota(self, timestamps, now, window, limit):
        """Test that the quota returned is always non-negative."""
        assume(limit >= 0)
        assume(window > 0)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        quota = result[1]
        assert quota >= 0, f"Quota should be non-negative, got {quota}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_boolean_allowance(self, timestamps, now, window, limit):
        """Test that the allowance returned is always a boolean."""
        assume(limit >= 0)
        assume(window > 0)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        allowance = result[0]
        assert isinstance(allowance, bool), f"Allowance should be boolean, got {type(allowance)} with value {allowance}"
        assert allowance in [True, False], f"Allowance should be True or False, got {allowance}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_quota_calculation(self, timestamps, now, window, limit):
        """Test that when within limit, quota equals limit - len(active)."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Filter timestamps to get active ones
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when within limit
        assume(len(active) <= limit)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        expected_quota = limit - len(active)
        assert result[1] == expected_quota, f"Expected quota {expected_quota} when len(active)={len(active)} <= limit={limit}, got {result[1]}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_window_filtering(self, timestamps, now, window, limit):
        """Test that active timestamps are correctly filtered by the window."""
        assume(limit >= 0)
        assume(window > 0)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        
        # Calculate active timestamps manually
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # The quota should be based on the number of active timestamps
        # If allowance is True, quota should be limit - len(active)
        # If allowance is False, quota should be 0 (and len(active) > limit)
        if result[0]:  # allowance is True
            assert result[1] == limit - len(active), f"When allowance is True, quota should be limit - len(active), got {result[1]} instead of {limit - len(active)}"
        else:  # allowance is False
            assert len(active) > limit, f"When allowance is False, len(active) should be > limit, but len(active)={len(active)} <= limit={limit}"
            assert result[1] == 0, f"When allowance is False, quota should be 0, got {result[1]}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_rate_limit_enforcement(self, timestamps, now, window, limit):
        """Test that rate limiting is enforced when len(active) > limit."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Filter timestamps to get active ones
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition len(active) > limit is met
        assume(len(active) > limit)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Rate limiting should be enforced when len(active) > limit, expected (False, 0), got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_allowance_when_within_limit(self, timestamps, now, window, limit):
        """Test that allowance is True when within the limit."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Filter timestamps to get active ones
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition len(active) <= limit is met
        assume(len(active) <= limit)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        assert result[0] == True, f"Allowance should be True when len(active) <= limit, got {result[0]}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_edge_cases(self, timestamps, now, window, limit):
        """Test edge cases like empty timestamps, zero limit, etc."""
        assume(limit >= 0)
        assume(window > 0)
        
        result = limit_query(timestamps, now, window=window, limit=limit)
        allowance, quota = result
        
        # Test that the result is a tuple of two elements
        assert isinstance(result, tuple), f"Result should be a tuple, got {type(result)}"
        assert len(result) == 2, f"Result should have 2 elements, got {len(result)}"
        
        # Test that allowance is boolean and quota is non-negative integer
        assert isinstance(allowance, bool), f"Allowance should be boolean, got {type(allowance)}"
        assert isinstance(quota, int), f"Quota should be integer, got {type(quota)}"
        assert quota >= 0, f"Quota should be non-negative, got {quota}"
        
        # Test that if quota is 0, then either limit is 0 or all timestamps are active
        if quota == 0:
            cutoff = now - window
            active = [t for t in timestamps if t >= cutoff]
            # Either limit is 0, or we're at the limit (len(active) >= limit)
            assert limit == 0 or len(active) >= limit, f"When quota is 0, either limit should be 0 or len(active) >= limit, but limit={limit}, len(active)={len(active)}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000),
        window=integers(min_value=1, max_value=100),
        limit=integers(min_value=0, max_value=50)
    )
    def test_monotonicity_property(self, timestamps, now, window, limit):
        """Test that adding more recent timestamps can only decrease allowance or quota."""
        assume(limit >= 0)
        assume(window > 0)
        
        # Get initial result
        result1 = limit_query(timestamps, now, window=window, limit=limit)
        allowance1, quota1 = result1
        
        # Add a timestamp that's within the window
        new_timestamp = now  # This is definitely within the window
        extended_timestamps = timestamps + [new_timestamp]
        
        result2 = limit_query(extended_timestamps, now, window=window, limit=limit)
        allowance2, quota2 = result2
        
        # Adding a timestamp within the window should not increase allowance or quota
        if allowance1:
            # If we had allowance before, we might lose it or keep it with reduced quota
            if allowance2:
                assert quota2 <= quota1, f"Adding a timestamp should not increase quota: {quota2} > {quota1}"
            # If we lost allowance, that's expected when going over the limit
        else:
            # If we had no allowance before, we should still have no allowance
            assert not allowance2, f"Should not gain allowance by adding a timestamp: {allowance2}"
            assert quota2 == 0, f"Quota should be 0 when no allowance: {quota2}"