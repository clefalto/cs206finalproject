import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, integers, lists, one_of, none
from typing import List, Optional


def backlog_rolling_avg(values: List[float], window: int) -> Optional[float]:
    """
    Calculate a rolling average of the last 'window' values.
    
    Args:
        values: List of numeric values
        window: Size of the rolling window (must be positive)
        
    Returns:
        Rolling average of the last 'window' values, or None if insufficient data
        
    Raises:
        ValueError: If window <= 0 or values is empty
    """
    if window <= 0:
        raise ValueError("window must be positive")
    
    if not values:
        raise ValueError("no values")
    
    # Get the last 'window' values
    recent = values[-window:]
    
    # Minimum number of values needed for a valid average
    warmup_min = 1
    
    if len(recent) < warmup_min:
        return None
    
    # Calculate the mean
    return sum(recent) / window


class TestBacklogRollingAvg:
    """Test class for backlog_rolling_avg function using Hypothesis."""

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=0),
        window=integers(min_value=-100, max_value=0)
    )
    def test_invalid_window_error(self, values, window):
        """Test that window <= 0 raises ValueError with correct message."""
        assume(window <= 0)
        with pytest.raises(ValueError, match="window must be positive"):
            backlog_rolling_avg(values, window)

    @given(
        window=integers(min_value=1, max_value=100)
    )
    def test_empty_values_error(self, window):
        """Test that empty values list raises ValueError with correct message."""
        with pytest.raises(ValueError, match="no values"):
            backlog_rolling_avg([], window)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=0),
        window=integers(min_value=1, max_value=100)
    )
    def test_insufficient_data_none(self, values, window):
        """Test that insufficient data returns None."""
        # This test covers the case where len(recent) < warmup_min
        # Since warmup_min = 1, this happens when recent is empty
        result = backlog_rolling_avg(values, window)
        assert result is None

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=100)
    )
    def test_positive_window_precondition(self, values, window):
        """Test that window > 0 precondition is satisfied."""
        # This test verifies the precondition window > 0
        # Since we generate window >= 1, this should always pass
        assume(window > 0)
        # If this raises, the precondition is violated
        result = backlog_rolling_avg(values, window)
        # We don't assert on the result, just that it doesn't raise due to window <= 0

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=100)
    )
    def test_non_empty_values_precondition(self, values, window):
        """Test that values is not empty precondition is satisfied."""
        # This test verifies the precondition len(values) > 0
        # Since we generate min_size=1, this should always pass
        assume(len(values) > 0)
        # If this raises ValueError("no values"), the precondition is violated
        result = backlog_rolling_avg(values, window)
        # We don't assert on the result, just that it doesn't raise due to empty values

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=100)
    )
    def test_rolling_average_calculation(self, values, window):
        """Test that the rolling average is calculated correctly."""
        assume(window > 0 and len(values) > 0)
        
        # Get the last 'window' values (this is what the function does)
        recent = values[-window:]
        
        # Since warmup_min = 1 and we have at least 1 value, we should get a result
        assume(len(recent) >= 1)
        
        result = backlog_rolling_avg(values, window)
        
        # Calculate expected result manually
        expected = sum(recent) / window
        
        # Use pytest.approx for floating point comparison
        assert result == pytest.approx(expected)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=0),
        window=integers(min_value=1, max_value=100)
    )
    def test_warmup_min_check(self, values, window):
        """Test the warmup_min check logic."""
        assume(window > 0)
        
        # Get the last 'window' values
        recent = values[-window:] if values else []
        
        result = backlog_rolling_avg(values, window)
        
        if len(recent) < 1:  # warmup_min = 1
            assert result is None
        else:
            # Should return the calculated mean
            expected = sum(recent) / window
            assert result == pytest.approx(expected)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=1000),
        window=integers(min_value=1, max_value=100)
    )
    def test_rolling_average_with_various_windows(self, values, window):
        """Test rolling average calculation with different window sizes."""
        assume(window > 0 and len(values) > 0)
        
        result = backlog_rolling_avg(values, window)
        
        # Should always return a float when we have valid input
        assert isinstance(result, float)
        
        # The result should be within the range of the input values
        recent = values[-window:]
        min_val = min(recent) if recent else float('inf')
        max_val = max(recent) if recent else float('-inf')
        
        assert min_val <= result <= max_val

    @given(
        values=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=50)
    )
    def test_rolling_average_with_bounded_values(self, values, window):
        """Test rolling average with bounded input values to avoid overflow."""
        assume(window > 0 and len(values) > 0)
        
        result = backlog_rolling_avg(values, window)
        
        # Should return a finite float
        assert isinstance(result, float)
        assert not (result != result)  # Check for NaN
        assert abs(result) != float('inf')  # Check for infinity

    @example(values=[1.0, 2.0, 3.0], window=2)
    @example(values=[5.0], window=1)
    @example(values=[1.0, 2.0, 3.0, 4.0, 5.0], window=3)
    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        window=integers(min_value=1, max_value=10)
    )
    def test_specific_examples(self, values, window):
        """Test specific examples to ensure correct behavior."""
        assume(window > 0 and len(values) > 0)
        
        result = backlog_rolling_avg(values, window)
        
        # Manual calculation for verification
        recent = values[-window:]
        expected = sum(recent) / window
        
        assert result == pytest.approx(expected)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])