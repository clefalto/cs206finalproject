import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, dictionaries, fixed_dictionaries
import math

# Import the function under test
from dataset.python_programs.request_token_bucket import request_token_bucket


class TestRequestTokenBucket:
    """Test suite for request_token_bucket function using Hypothesis."""

    @given(
        rate=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_rate_or_capacity_raises_value_error(self, rate, capacity):
        """Test that invalid rate or capacity raises ValueError."""
        tokens = {"available": 5, "last": 0.0}
        assume(rate <= 0 or capacity <= 0)
        
        with pytest.raises(ValueError, match="invalid rate/capacity"):
            request_token_bucket(tokens, 1.0, rate=rate, capacity=capacity)

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_no_token_available_returns_false(self, rate, capacity, available, last, now):
        """Test that when no tokens are available, function returns False."""
        assume(available <= 0)
        
        tokens = {"available": available, "last": last}
        result = request_token_bucket(tokens, now, rate=rate, capacity=capacity)
        
        assert result is False

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_token_consumption_updates_state(self, rate, capacity, available, last, now):
        """Test that when a token is consumed, state is updated correctly."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        initial_available = available
        initial_last = last
        
        result = request_token_bucket(tokens, now, rate=rate, capacity=capacity)
        
        # Should return True when token is consumed
        assert result is True
        
        # available should be decremented by 1
        assert tokens["available"] == initial_available - 1
        
        # last should be updated to current time
        assert tokens["last"] == now

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_token_refill_logic(self, rate, capacity, available, last, now):
        """Test that token refill logic works correctly."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        
        # Calculate expected refill amount
        time_diff = now - last
        expected_refill = int(time_diff * rate)
        expected_available = min(capacity, available + expected_refill)
        
        # Call the function (may or may not consume a token)
        request_token_bucket(tokens, now, rate=rate, capacity=capacity)
        
        # The available tokens should be at least the expected refill amount
        # (minus 1 if a token was consumed)
        assert tokens["available"] >= expected_available - 1

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_capacity_limit_respected(self, rate, capacity, available, last, now):
        """Test that available tokens never exceed capacity."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        
        # Call the function multiple times to potentially refill
        for _ in range(10):
            request_token_bucket(tokens, now, rate=rate, capacity=capacity)
            # available should never exceed capacity
            assert tokens["available"] <= capacity

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_tokens(self, rate, capacity, available, last, now):
        """Test that available tokens are never negative."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        
        # Call the function multiple times
        for _ in range(10):
            request_token_bucket(tokens, now, rate=rate, capacity=capacity)
            # available should never be negative
            assert tokens["available"] >= 0

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_time_update(self, rate, capacity, available, last, now):
        """Test that time updates are monotonic when tokens are consumed."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        previous_now = last
        
        # Call the function
        result = request_token_bucket(tokens, now, rate=rate, capacity=capacity)
        
        if result is True:  # Token was consumed
            # last should be updated to current time
            assert tokens["last"] == now
            # Time should be monotonic (current >= previous)
            assert now >= previous_now

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        available=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        last=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        now=floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_multiple_consecutive_calls(self, rate, capacity, available, last, now):
        """Test behavior with multiple consecutive calls."""
        assume(now >= last)  # Ensure time doesn't go backwards
        
        tokens = {"available": available, "last": last}
        initial_available = available
        
        # Make multiple calls
        results = []
        for i in range(5):
            result = request_token_bucket(tokens, now, rate=rate, capacity=capacity)
            results.append(result)
        
        # Count successful consumptions
        successful_consumptions = sum(1 for r in results if r is True)
        
        # Should not consume more tokens than initially available
        assert successful_consumptions <= initial_available
        
        # Final available should be initial minus successful consumptions
        assert tokens["available"] == initial_available - successful_consumptions

    def test_edge_case_zero_rate_and_capacity(self):
        """Test edge case with zero rate and capacity."""
        tokens = {"available": 0, "last": 0.0}
        
        with pytest.raises(ValueError, match="invalid rate/capacity"):
            request_token_bucket(tokens, 1.0, rate=0, capacity=0)

    def test_edge_case_negative_rate_and_capacity(self):
        """Test edge case with negative rate and capacity."""
        tokens = {"available": 5, "last": 0.0}
        
        with pytest.raises(ValueError, match="invalid rate/capacity"):
            request_token_bucket(tokens, 1.0, rate=-1, capacity=-1)

    @given(
        rate=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        capacity=floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_initial_state_with_default_values(self, rate, capacity):
        """Test behavior with default initial state (empty tokens dict)."""
        tokens = {}
        
        # First call should succeed and initialize state
        result = request_token_bucket(tokens, 1.0, rate=rate, capacity=capacity)
        
        assert result is True
        assert "available" in tokens
        assert "last" in tokens
        assert tokens["available"] == capacity - 1
        assert tokens["last"] == 1.0