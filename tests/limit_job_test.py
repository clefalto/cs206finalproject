"""
Hypothesis-based tests for the limit_job function semantic properties.
Tests all properties defined in properties/limit_job_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists


# Import the function under test
from dataset.python_programs.limit_job import limit_job


class TestLimitJobProperties:
    """Test class for limit_job semantic properties using Hypothesis."""

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_throttle_when_exceeds_limit(self, timestamps, now, window, limit):
        """
        Test: if len(recent) > limit then return False, 0
        Property: throttle_when_exceeds_limit
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(recent) > limit)
        
        status, remaining = limit_job(timestamps, now, window=window, limit=limit)
        
        # Should return False status and 0 remaining when limit exceeded
        assert status is False, f"Expected False when len(recent)={len(recent)} > limit={limit}"
        assert remaining == 0, f"Expected remaining=0 when limit exceeded, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_allow_when_within_limit(self, timestamps, now, window, limit):
        """
        Test: if len(recent) <= limit then return True, limit - len(recent)
        Property: allow_when_within_limit
        """
        # Filter timestamps to get recent ones
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met (limit not exceeded)
        assume(len(recent) <= limit)
        
        status, remaining = limit_job(timestamps, now, window=window, limit=limit)
        
        # Should return True status and calculated remaining count
        assert status is True, f"Expected True when len(recent)={len(recent)} <= limit={limit}"
        expected_remaining = limit - len(recent)
        assert remaining == expected_remaining, f"Expected remaining={expected_remaining}, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_returns_boolean_and_count(self, timestamps, now, window, limit):
        """
        Test: limit_job(timestamps, now) returns (bool, int)
        Property: returns_boolean_and_count
        """
        result = limit_job(timestamps, now, window=window, limit=limit)
        
        # Should return a tuple
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 2, f"Expected tuple of length 2, got {len(result)}"
        
        status, remaining = result
        
        # Status should be boolean
        assert isinstance(status, bool), f"Status should be bool, got {type(status)}"
        
        # Remaining should be integer
        assert isinstance(remaining, int), f"Remaining should be int, got {type(remaining)}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_non_negative_remaining_count(self, timestamps, now, window, limit):
        """
        Test: limit_job(timestamps, now)[1] >= 0
        Property: non_negative_remaining_count
        """
        status, remaining = limit_job(timestamps, now, window=window, limit=limit)
        
        # Remaining count should always be non-negative
        assert remaining >= 0, f"Remaining count should be >= 0, got {remaining}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_monotonic_window_filtering(self, timestamps, now, window, limit):
        """
        Test: len([t for t in timestamps if t >= now - window]) <= len(timestamps)
        Property: monotonic_window_filtering
        """
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # Window filtering should not increase the count
        assert len(recent) <= len(timestamps), \
            f"Window filtering should not increase count: len(recent)={len(recent)} > len(timestamps)={len(timestamps)}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_window_consistency(self, timestamps, now, window, limit):
        """
        Test: all(t >= now - window for t in [t for t in timestamps if t >= now - window])
        Property: window_consistency
        """
        cutoff = now - window
        recent = [t for t in timestamps if t >= cutoff]
        
        # All recent timestamps should satisfy the window condition
        assert all(t >= cutoff for t in recent), \
            f"All recent timestamps should be >= cutoff={cutoff}, but found: {recent}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_deterministic_output(self, timestamps, now, window, limit):
        """
        Test: limit_job(timestamps, now) == limit_job(timestamps, now)
        Property: deterministic_output
        """
        result1 = limit_job(timestamps, now, window=window, limit=limit)
        result2 = limit_job(timestamps, now, window=window, limit=limit)
        
        # Same inputs should produce identical outputs
        assert result1 == result2, f"Function should be deterministic, got {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now1=integers(min_value=0, max_value=1000000),
        now2=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_time_monotonicity(self, timestamps, now1, now2, window, limit):
        """
        Test: if now2 >= now1 then limit_job(timestamps, now2)[1] >= limit_job(timestamps, now1)[1]
        Property: time_monotonicity
        """
        assume(now2 >= now1)
        
        _, remaining1 = limit_job(timestamps, now1, window=window, limit=limit)
        _, remaining2 = limit_job(timestamps, now2, window=window, limit=limit)
        
        # Later time should have more or equal remaining count
        assert remaining2 >= remaining1, \
            f"Later time should have more remaining: now2={now2} >= now1={now1}, but remaining2={remaining2} < remaining1={remaining1}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_timestamp_order_invariance(self, timestamps, now, window, limit):
        """
        Test: limit_job(sorted(timestamps), now) == limit_job(timestamps, now)
        Property: timestamp_order_invariance
        """
        result1 = limit_job(sorted(timestamps), now, window=window, limit=limit)
        result2 = limit_job(timestamps, now, window=window, limit=limit)
        
        # Order of timestamps should not affect the result
        assert result1 == result2, \
            f"Function should be order-invariant, got {result1} != {result2}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_limit_respects_window(self, timestamps, now, window, limit):
        """
        Test: limit_job(timestamps, now)[1] <= limit
        Property: limit_respects_window
        """
        status, remaining = limit_job(timestamps, now, window=window, limit=limit)
        
        # Remaining count should not exceed the limit
        assert remaining <= limit, f"Remaining should not exceed limit: remaining={remaining} > limit={limit}"

    @given(
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_empty_timestamps_allowed(self, now, window, limit):
        """
        Test: limit_job([], now) == (True, limit)
        Property: empty_timestamps_allowed
        """
        status, remaining = limit_job([], now, window=window, limit=limit)
        
        # Empty timestamps should always be allowed with full limit
        assert status is True, "Empty timestamps should always be allowed"
        assert remaining == limit, f"Empty timestamps should have full limit remaining: {remaining} != {limit}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0, max_size=100),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=3600),
        limit=integers(min_value=1, max_value=1000)
    )
    def test_all_old_timestamps_allowed(self, timestamps, now, window, limit):
        """
        Test: if all(t < now - window for t in timestamps) then limit_job(timestamps, now) == (True, limit)
        Property: all_old_timestamps_allowed
        """
        cutoff = now - window
        assume(all(t < cutoff for t in timestamps))
        
        status, remaining = limit_job(timestamps, now, window=window, limit=limit)
        
        # All old timestamps should be allowed with full limit
        assert status is True, "All old timestamps should be allowed"
        assert remaining == limit, f"All old timestamps should have full limit remaining: {remaining} != {limit}"


# Additional integration tests for specific scenarios
class TestLimitJobIntegration:
    """Additional integration tests for limit_job."""

    def test_empty_timestamps(self):
        """Test with empty timestamps list."""
        status, remaining = limit_job([], 100, window=60, limit=20)
        assert status is True
        assert remaining == 20

    def test_single_timestamp_within_window(self):
        """Test with single timestamp within window."""
        status, remaining = limit_job([90], 100, window=60, limit=20)
        assert status is True
        assert remaining == 19

    def test_single_timestamp_outside_window(self):
        """Test with single timestamp outside window."""
        status, remaining = limit_job([30], 100, window=60, limit=20)
        assert status is True
        assert remaining == 20

    def test_exactly_at_limit(self):
        """Test when recent count equals limit (should still allow due to bug)."""
        timestamps = list(range(41, 61))  # 20 timestamps in window
        status, remaining = limit_job(timestamps, 100, window=60, limit=20)
        assert status is True
        assert remaining == 0

    def test_over_limit(self):
        """Test when recent count exceeds limit."""
        timestamps = list(range(40, 61))  # 21 timestamps in window
        status, remaining = limit_job(timestamps, 100, window=60, limit=20)
        assert status is False
        assert remaining == 0

    def test_default_parameters(self):
        """Test with default window and limit parameters."""
        status, remaining = limit_job([90], 100)
        assert status is True
        assert remaining == 19