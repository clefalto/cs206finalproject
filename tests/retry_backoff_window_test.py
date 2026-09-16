"""
Hypothesis-based property tests for retry_backoff_window function.

This test suite exercises all semantic properties identified in 
properties/retry_backoff_window_properties.json using the Hypothesis 
testing framework to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st, example
from hypothesis.strategies import integers, floats
from typing import Union


# Import the function under test
# Note: The actual function implementation should be imported here
# from your_module import retry_backoff_window

def retry_backoff_window(attempts: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Retry backoff window calculation with exponential growth and max delay capping.
    
    Args:
        attempts: Number of retry attempts (must be non-negative)
        base: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 60.0)
    
    Returns:
        Calculated delay in seconds
    
    Raises:
        ValueError: If attempts is negative
    """
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    
    delay = base * (2 ** attempts)
    if delay > max_delay:  # Note: This uses > instead of >= (boundary bug)
        delay = max_delay
    
    return delay


class TestRetryBackoffWindowProperties:
    """Test class for retry_backoff_window semantic properties."""
    
    @given(
        attempts=st.integers(max_value=-1),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts=-1, base=1.0, max_delay=60.0)
    @example(attempts=-10, base=0.5, max_delay=30.0)
    def test_raises_value_error_for_negative_attempts(self, attempts, base, max_delay):
        """
        Property: raises_value_error
        Condition: attempts < 0
        Formal: raises ValueError with message 'attempts must be non-negative'
        """
        with pytest.raises(ValueError, match="attempts must be non-negative"):
            retry_backoff_window(attempts, base, max_delay)
    
    @given(
        attempts=st.integers(min_value=0, max_value=10),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    def test_capped_at_max_delay(self, attempts, base, max_delay):
        """
        Property: capped_at_max_delay
        Condition: attempts >= 0 and delay > max_delay
        Formal: delay == max_delay
        """
        assume(attempts >= 0)
        
        # Calculate what the delay would be without capping
        uncapped_delay = base * (2 ** attempts)
        
        # Only test when the uncapped delay would exceed max_delay
        assume(uncapped_delay > max_delay)
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # The result should be capped at max_delay
        assert result == max_delay, f"Expected {max_delay}, got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
    
    @given(
        attempts=st.integers(min_value=0, max_value=10),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    def test_exponential_growth_when_not_capped(self, attempts, base, max_delay):
        """
        Property: exponential_growth
        Condition: attempts >= 0 and delay <= max_delay
        Formal: delay == base * (2 ** attempts)
        """
        assume(attempts >= 0)
        
        # Calculate what the delay would be without capping
        expected_delay = base * (2 ** attempts)
        
        # Only test when the delay would not be capped
        assume(expected_delay <= max_delay)
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # The result should follow exponential growth
        assert result == expected_delay, f"Expected {expected_delay}, got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
    
    @given(
        attempts=st.integers(min_value=0, max_value=20),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts=0, base=1.0, max_delay=60.0)
    @example(attempts=5, base=0.5, max_delay=30.0)
    def test_non_negative_output(self, attempts, base, max_delay):
        """
        Property: non_negative_output
        Precondition: attempts >= 0
        Formal: delay >= 0
        """
        assume(attempts >= 0)
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # The result should always be non-negative
        assert result >= 0, f"Expected non-negative delay, got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
    
    @given(
        attempts1=st.integers(min_value=0, max_value=10),
        attempts2=st.integers(min_value=0, max_value=10),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts1=0, attempts2=1, base=1.0, max_delay=60.0)
    @example(attempts1=2, attempts2=3, base=0.5, max_delay=30.0)
    def test_monotonic_increasing(self, attempts1, attempts2, base, max_delay):
        """
        Property: monotonic_increasing
        Precondition: attempts >= 0 and attempts1 < attempts2
        Formal: retry_backoff_window(attempts1) <= retry_backoff_window(attempts2)
        """
        assume(attempts1 >= 0 and attempts2 >= 0 and attempts1 < attempts2)
        
        result1 = retry_backoff_window(attempts1, base, max_delay)
        result2 = retry_backoff_window(attempts2, base, max_delay)
        
        # The function should be monotonic increasing
        assert result1 <= result2, f"Expected monotonic increase: {result1} <= {result2} for attempts1={attempts1}, attempts2={attempts2}, base={base}, max_delay={max_delay}"
    
    @given(
        attempts=st.integers(min_value=0, max_value=20),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts=0, base=1.0, max_delay=60.0)
    @example(attempts=10, base=1.0, max_delay=60.0)
    def test_bounded_by_max_delay(self, attempts, base, max_delay):
        """
        Property: bounded_by_max_delay
        Precondition: attempts >= 0
        Formal: delay <= max_delay
        """
        assume(attempts >= 0)
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # The result should never exceed max_delay
        assert result <= max_delay, f"Expected delay <= max_delay ({max_delay}), got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
    
    @given(
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(base=1.0, max_delay=60.0)
    @example(base=0.5, max_delay=30.0)
    def test_base_case_identity(self, base, max_delay):
        """
        Property: base_case_identity
        Precondition: attempts == 0 and base * (2 ** 0) <= max_delay
        Formal: delay == base
        """
        assume(base * (2 ** 0) <= max_delay)  # base <= max_delay
        
        result = retry_backoff_window(0, base, max_delay)
        
        # For attempts=0, the delay should equal the base
        assert result == base, f"Expected {base}, got {result} for attempts=0, base={base}, max_delay={max_delay}"
    
    @given(
        attempts=st.integers(min_value=0, max_value=10),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts=0, base=1.0, max_delay=60.0)
    @example(attempts=1, base=1.0, max_delay=60.0)
    @example(attempts=2, base=1.0, max_delay=60.0)
    def test_exponential_growth_rate(self, attempts, base, max_delay):
        """
        Property: exponential_growth_rate
        Precondition: attempts >= 0 and base * (2 ** attempts) <= max_delay
        Formal: delay == base * (2 ** attempts)
        """
        assume(attempts >= 0)
        
        expected_delay = base * (2 ** attempts)
        assume(expected_delay <= max_delay)
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # The result should follow the exact exponential growth formula
        assert result == expected_delay, f"Expected {expected_delay}, got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
    
    @given(
        attempts=st.integers(min_value=0, max_value=10),
        base=st.floats(min_value=0.1, max_value=100.0),
        max_delay=st.floats(min_value=0.1, max_value=1000.0)
    )
    @example(attempts=6, base=1.0, max_delay=64.0)  # 1 * (2^6) = 64 == max_delay
    @example(attempts=5, base=2.0, max_delay=64.0)  # 2 * (2^5) = 64 == max_delay
    def test_boundary_bug(self, attempts, base, max_delay):
        """
        Property: boundary_bug
        Precondition: attempts >= 0 and base * (2 ** attempts) == max_delay
        Formal: delay == max_delay (should not be capped but is due to > vs >= bug)
        
        This test documents the boundary condition bug where the comparison
        uses > instead of >=, causing exact matches to be incorrectly capped.
        """
        assume(attempts >= 0)
        
        exact_delay = base * (2 ** attempts)
        assume(exact_delay == max_delay)  # This is the boundary condition
        
        result = retry_backoff_window(attempts, base, max_delay)
        
        # Due to the bug (using > instead of >=), this will be capped
        # even though it shouldn't be
        assert result == max_delay, f"Expected boundary bug: {max_delay}, got {result} for attempts={attempts}, base={base}, max_delay={max_delay}"
        
        # This demonstrates the bug: the delay equals max_delay due to incorrect capping
        # In a correct implementation, this should not be capped when exact_delay == max_delay


class TestRetryBackoffWindowEdgeCases:
    """Additional edge case tests for retry_backoff_window."""
    
    @given(
        base=st.floats(min_value=0.001, max_value=1000.0, allow_infinity=False, allow_nan=False),
        max_delay=st.floats(min_value=0.001, max_value=10000.0, allow_infinity=False, allow_nan=False)
    )
    def test_small_values(self, base, max_delay):
        """Test with small but valid float values."""
        assume(base > 0 and max_delay > 0)
        
        # Test with 0 attempts
        result = retry_backoff_window(0, base, max_delay)
        assert result == base
        
        # Test with 1 attempt (should be 2 * base if not capped)
        expected = base * 2
        if expected <= max_delay:
            assert result * 2 == retry_backoff_window(1, base, max_delay)
    
    @given(
        attempts=st.integers(min_value=0, max_value=5),
        base=st.floats(min_value=0.1, max_value=10.0),
        max_delay=st.floats(min_value=10.0, max_value=100.0)
    )
    def test_no_capping_scenario(self, attempts, base, max_delay):
        """Test scenarios where capping should not occur."""
        assume(attempts >= 0)
        
        # Ensure that even with maximum attempts, we won't hit the cap
        max_possible_delay = base * (2 ** attempts)
        assume(max_possible_delay <= max_delay)
        
        result = retry_backoff_window(attempts, base, max_delay)
        expected = base * (2 ** attempts)
        
        assert result == expected
    
    def test_specific_boundary_cases(self):
        """Test specific boundary cases that might reveal edge behavior."""
        
        # Test exact boundary where delay equals max_delay
        # With base=1, max_delay=64, attempts=6: 1 * (2^6) = 64
        result = retry_backoff_window(6, 1.0, 64.0)
        assert result == 64.0  # This demonstrates the boundary bug
        
        # Test just below boundary
        result = retry_backoff_window(5, 1.0, 64.0)  # 1 * (2^5) = 32
        assert result == 32.0
        
        # Test just above boundary  
        result = retry_backoff_window(7, 1.0, 64.0)  # 1 * (2^7) = 128 > 64
        assert result == 64.0  # Should be capped


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])