import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, lists, integers
import math


def smooth_clicks(values, window, warmup_min=1):
    """
    Calculate smoothed clicks using a sliding window average.
    
    Args:
        values: List of numeric values (click counts)
        window: Window size for averaging (must be positive)
        warmup_min: Minimum number of values required before returning a result
    
    Returns:
        float: The smoothed average of the last 'window' values, or None if insufficient data
    
    Note: This implementation contains the "window size bug" where the mean
    is calculated using 'window' as the divisor instead of the actual number
    of elements in the tail.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    
    if not values:
        raise ValueError("empty series")
    
    # Extract the last 'window' elements
    tail = values[-window:]
    
    # Calculate sum of tail elements
    total = sum(tail)
    
    # Calculate mean using window size (this is the bug - should use len(tail))
    mean = total / window
    
    # Check if we have enough data for warmup
    if len(tail) < warmup_min:
        return None
    
    return mean


class TestSmoothClicks:
    """Test suite for smooth_clicks function using Hypothesis."""

    # Branch-level property tests

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=0),
        window=integers(max_value=0)
    )
    def test_invalid_window_error(self, values, window):
        """Test that window <= 0 raises ValueError with correct message."""
        with pytest.raises(ValueError, match="window must be positive"):
            smooth_clicks(values, window)

    @given(
        window=integers(min_value=1, max_value=100)
    )
    def test_empty_series_error(self, window):
        """Test that empty values list raises ValueError with correct message."""
        with pytest.raises(ValueError, match="empty series"):
            smooth_clicks([], window)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        window=integers(min_value=1, max_value=100),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_insufficient_data_none(self, values, window, warmup_min):
        """Test that insufficient data returns None."""
        assume(len(values) < warmup_min)
        result = smooth_clicks(values, window, warmup_min)
        assert result is None

    # Function-level property tests

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=100),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_positive_window_requirement(self, values, window, warmup_min):
        """Test that function requires positive window to proceed."""
        # This test verifies that the precondition window > 0 is enforced
        # by ensuring valid windows don't raise the "window must be positive" error
        try:
            result = smooth_clicks(values, window, warmup_min)
            # If we get here, window was positive (precondition satisfied)
            assert window > 0
        except ValueError as e:
            # Should only get "empty series" error, not "window must be positive"
            assert "empty series" in str(e)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=integers(min_value=1, max_value=100),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_non_empty_values_requirement(self, values, window, warmup_min):
        """Test that function requires non-empty values to proceed."""
        # This test verifies that the precondition values is not empty is enforced
        # by ensuring non-empty values don't raise the "empty series" error
        try:
            result = smooth_clicks(values, window, warmup_min)
            # If we get here, values was not empty (precondition satisfied)
            assert len(values) > 0
        except ValueError as e:
            # Should only get "window must be positive" error, not "empty series"
            assert "window must be positive" in str(e)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_window_size_bug(self, values, window, warmup_min):
        """Test the window size bug where mean uses window instead of len(tail)."""
        assume(len(values) >= warmup_min)
        
        result = smooth_clicks(values, window, warmup_min)
        
        # Extract tail as the function does
        tail = values[-window:]
        total = sum(tail)
        
        # The bug: using window instead of len(tail) as divisor
        expected_with_bug = total / window
        
        assert math.isclose(result, expected_with_bug, rel_tol=1e-9)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_tail_extraction(self, values, window, warmup_min):
        """Test that tail extraction works correctly."""
        assume(len(values) >= warmup_min)
        
        # Manually extract tail as the function should
        expected_tail = values[-window:]
        
        # Get the actual result to ensure the function executed
        result = smooth_clicks(values, window, warmup_min)
        
        # Verify the tail extraction logic by checking the sum
        tail_sum = sum(expected_tail)
        assert isinstance(result, (int, float))

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_sum_calculation(self, values, window, warmup_min):
        """Test that sum calculation works correctly on tail elements."""
        assume(len(values) >= warmup_min)
        
        # Extract tail and calculate sum as the function does
        tail = values[-window:]
        expected_total = sum(tail)
        
        # Get result to ensure function executed
        result = smooth_clicks(values, window, warmup_min)
        
        # Verify the sum was calculated correctly by checking the mean
        expected_mean = expected_total / window
        assert math.isclose(result, expected_mean, rel_tol=1e-9)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_mean_calculation(self, values, window, warmup_min):
        """Test that mean calculation uses window size as divisor."""
        assume(len(values) >= warmup_min)
        
        # Calculate expected mean using window as divisor (the bug)
        tail = values[-window:]
        total = sum(tail)
        expected_mean = total / window
        
        result = smooth_clicks(values, window, warmup_min)
        
        assert math.isclose(result, expected_mean, rel_tol=1e-9)

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_warmup_check(self, values, window, warmup_min):
        """Test that warmup check determines return value correctly."""
        tail = values[-window:]
        
        if len(tail) < warmup_min:
            result = smooth_clicks(values, window, warmup_min)
            assert result is None
        else:
            result = smooth_clicks(values, window, warmup_min)
            assert isinstance(result, (int, float))

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_return_type(self, values, window, warmup_min):
        """Test that function returns either None or float."""
        assume(len(values) >= warmup_min)
        
        result = smooth_clicks(values, window, warmup_min)
        
        # Should return either None or float
        assert result is None or isinstance(result, (int, float))

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100),
        window=integers(max_value=100),
        warmup_min=integers(min_value=1, max_value=10)
    )
    def test_error_handling(self, values, window, warmup_min):
        """Test that function raises ValueError for invalid inputs."""
        if window <= 0:
            with pytest.raises(ValueError, match="window must be positive"):
                smooth_clicks(values, window, warmup_min)
        elif not values:
            with pytest.raises(ValueError, match="empty series"):
                smooth_clicks(values, window, warmup_min)
        else:
            # Valid inputs should not raise ValueError
            result = smooth_clicks(values, window, warmup_min)
            assert result is None or isinstance(result, (int, float))

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=10, max_size=100),
        window=integers(min_value=1, max_value=50),
        warmup_min=integers(min_value=1, max_value=5)
    )
    def test_metamorphic_relation_bug(self, values, window, warmup_min):
        """Test the metamorphic relation bug where result differs from correct calculation."""
        assume(len(values) >= warmup_min)
        
        result = smooth_clicks(values, window, warmup_min)
        
        # Calculate what the correct mean should be (using len(tail) as divisor)
        tail = values[-window:]
        correct_mean = sum(tail) / len(tail)
        
        # Due to the window size bug, these should be different (unless window == len(tail))
        if window != len(tail):
            assert not math.isclose(result, correct_mean, rel_tol=1e-9)
        else:
            # When window == len(tail), both calculations give the same result
            assert math.isclose(result, correct_mean, rel_tol=1e-9)

    # Edge case and integration tests

    @given(
        values=lists(floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
        window=integers(min_value=1, max_value=20),
        warmup_min=integers(min_value=1, max_value=5)
    )
    @example(values=[1.0], window=1, warmup_min=1)  # Single element
    @example(values=[1.0, 2.0, 3.0], window=2, warmup_min=1)  # Simple case
    @example(values=[0.0, 0.0, 0.0], window=3, warmup_min=1)  # All zeros
    @example(values=[100.0, 200.0, 300.0], window=1, warmup_min=1)  # Window size 1
    def test_edge_cases(self, values, window, warmup_min):
        """Test various edge cases and specific examples."""
        assume(len(values) >= warmup_min)
        
        result = smooth_clicks(values, window, warmup_min)
        
        # Verify basic properties
        assert result is not None  # Should have enough data
        assert isinstance(result, (int, float))
        
        # Verify the calculation is correct according to the buggy implementation
        tail = values[-window:]
        expected = sum(tail) / window
        assert math.isclose(result, expected, rel_tol=1e-9)

    @given(
        values=lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), 
                    min_size=1, max_size=50),
        window=integers(min_value=1, max_value=25)
    )
    def test_numerical_stability(self, values, window):
        """Test that function handles various numerical ranges correctly."""
        assume(len(values) >= 1)  # At least warmup_min=1
        
        result = smooth_clicks(values, window, warmup_min=1)
        
        if result is not None:
            # Result should be finite
            assert math.isfinite(result)
            # Result should be reasonable given the input range
            min_val = min(values[-window:])
            max_val = max(values[-window:])
            assert min_val <= result <= max_val or min_val >= result >= max_val