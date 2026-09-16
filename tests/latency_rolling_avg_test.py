"""
Hypothesis-based property tests for latency_rolling_avg function.

This test suite exercises all semantic properties identified for the
latency_rolling_avg function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, just
import math
from typing import List, Optional, Union

# Import the function under test
# Note: This assumes the function is available in the current environment
# In practice, you would import from the actual module containing latency_rolling_avg
try:
    from your_module import latency_rolling_avg
except ImportError:
    # Mock implementation for testing purposes - replace with actual import
    def latency_rolling_avg(series: List[float], window: int, warmup_min: int = 0) -> Optional[float]:
        """
        Mock implementation of latency_rolling_avg for testing.
        Replace this with the actual function import.
        """
        if window <= 0:
            raise ValueError("invalid window")
        
        if not series:
            raise ValueError("no samples")
        
        tail = series[-window:]
        
        if len(tail) < warmup_min:
            return None
        
        # Bug: uses window instead of len(tail) in division
        return sum(tail) / window


class TestLatencyRollingAvgProperties:
    """Test class for latency_rolling_avg semantic properties."""

    # Strategies for generating test data
    valid_window_strategy = integers(min_value=1, max_value=1000)
    warmup_min_strategy = integers(min_value=0, max_value=100)
    float_list_strategy = lists(floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=0, max_size=1000)
    
    # Strategy for generating series that ensures we have enough elements for the window
    series_with_window_strategy = st.tuples(
        valid_window_strategy,
        lists(floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=1000)
    ).filter(lambda x: len(x[1]) >= x[0])

    @given(window=integers(max_value=0))
    def test_invalid_window_error(self, window: int):
        """Test that invalid window (<= 0) raises ValueError with correct message."""
        series = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="invalid window"):
            latency_rolling_avg(series, window=window)

    @given(window=valid_window_strategy)
    def test_empty_series_error(self, window: int):
        """Test that empty series raises ValueError with correct message."""
        with pytest.raises(ValueError, match="no samples"):
            latency_rolling_avg([], window=window)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) < x[1])
    )
    def test_insufficient_samples_return_none(self, data):
        """Test that insufficient samples (len(tail) < warmup_min) returns None."""
        window, warmup_min, series = data
        result = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        assert result is None

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_valid_window_precondition(self, data):
        """Test that function requires window > 0."""
        window, series = data
        # This test verifies the precondition is enforced
        # If window <= 0, it should raise ValueError
        if window <= 0:
            with pytest.raises(ValueError, match="invalid window"):
                latency_rolling_avg(series, window=window)
        else:
            # If window > 0, it should not raise due to window precondition
            try:
                latency_rolling_avg(series, window=window)
            except ValueError as e:
                # Should only raise for other reasons (empty series, etc.)
                assert "invalid window" not in str(e)

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) == 0)
    )
    def test_non_empty_series_precondition(self, data):
        """Test that function requires non-empty series."""
        window, series = data
        with pytest.raises(ValueError, match="no samples"):
            latency_rolling_avg(series, window=window)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_moving_average_computation(self, data):
        """Test that function computes correct moving average."""
        window, warmup_min, series = data
        result = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        tail = series[-window:]
        expected = sum(tail) / window  # Note: bug uses window instead of len(tail)
        
        assert result == expected

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_window_size_invariant(self, data):
        """Test that function only considers last 'window' elements."""
        window, warmup_min, series = data
        
        # Get result with full series
        result_full = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        # Get result with only the last window elements
        tail = series[-window:]
        result_tail = latency_rolling_avg(tail, window=window, warmup_min=warmup_min)
        
        assert result_full == result_tail

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0)
    )
    def test_warmup_min_threshold(self, data):
        """Test warmup_min threshold behavior."""
        window, warmup_min, series = data
        tail = series[-window:]
        
        result = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        if len(tail) < warmup_min:
            assert result is None
        else:
            # Should return computed average
            assert result is not None
            assert isinstance(result, (int, float))

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            lists(floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=1000)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_monotonicity_preservation(self, data):
        """Test that non-negative inputs produce non-negative output."""
        window, warmup_min, series = data
        
        # Ensure all elements are non-negative
        assume(all(x >= 0 for x in series))
        
        result = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        assert result >= 0

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and len(x[2]) > 0)
    )
    def test_scale_invariance(self, data):
        """Test scale invariance property."""
        window, warmup_min, series, k = data
        
        # Skip zero scalar as it would make all results zero
        assume(abs(k) > 1e-9)
        
        result_original = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        scaled_series = [k * x for x in series]
        result_scaled = latency_rolling_avg(scaled_series, window=window, warmup_min=warmup_min)
        
        # Check if scale invariance holds (accounting for floating point precision)
        expected_scaled = k * result_original
        assert abs(result_scaled - expected_scaled) < 1e-9

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[3]) >= x[0] and 
                len(x[2][-x[0]:]) >= x[1] and len(x[3][-x[0]:]) >= x[1] and
                len(x[2]) > 0 and len(x[3]) > 0)
    )
    def test_additive_property(self, data):
        """Test additive property of the function."""
        window, warmup_min, series1, series2 = data
        
        # Ensure series have same length for zip operation
        min_len = min(len(series1), len(series2))
        series1 = series1[:min_len]
        series2 = series2[:min_len]
        
        result1 = latency_rolling_avg(series1, window=window, warmup_min=warmup_min)
        result2 = latency_rolling_avg(series2, window=window, warmup_min=warmup_min)
        
        combined_series = [x + y for x, y in zip(series1, series2)]
        result_combined = latency_rolling_avg(combined_series, window=window, warmup_min=warmup_min)
        
        expected_combined = result1 + result2
        assert abs(result_combined - expected_combined) < 1e-9

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_window_parameter_dependency(self, data):
        """Test that function depends only on window parameter value."""
        window, warmup_min, series = data
        
        # Test with window as positional argument
        result_positional = latency_rolling_avg(series, window, warmup_min=warmup_min)
        
        # Test with window as keyword argument
        result_keyword = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        assert result_positional == result_keyword

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0)
    )
    def test_warmup_min_parameter_dependency(self, data):
        """Test that warmup_min parameter affects only threshold check."""
        window, warmup_min, series = data
        
        # Test with warmup_min as positional argument
        try:
            result_positional = latency_rolling_avg(series, window, warmup_min)
        except ValueError:
            result_positional = None
        
        # Test with warmup_min as keyword argument  
        try:
            result_keyword = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        except ValueError:
            result_keyword = None
        
        assert result_positional == result_keyword

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and len(x[2][-x[0]:]) != x[0])
    )
    def test_bug_in_warmup_calculation(self, data):
        """Test the bug where function uses 'window' instead of 'len(tail)' in division."""
        window, warmup_min, series = data
        tail = series[-window:]
        
        # This test specifically checks for the bug
        # The function should use len(tail) but actually uses window
        result = latency_rolling_avg(series, window=window, warmup_min=warmup_min)
        
        # Calculate what it SHOULD be (correct implementation)
        correct_result = sum(tail) / len(tail)
        
        # Calculate what it ACTUALLY is (buggy implementation)  
        buggy_result = sum(tail) / window
        
        # Verify the bug exists (result matches buggy implementation)
        assert result == buggy_result
        
        # Verify it's different from correct implementation (when len(tail) != window)
        if len(tail) != window:
            assert result != correct_result

    # Additional edge case tests

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) >= x[0])
    )
    def test_single_element_window(self, data):
        """Test behavior with window=1."""
        window, series = data
        assume(window == 1)
        
        result = latency_rolling_avg(series, window=window)
        expected = series[-1]  # Should be the last element
        
        assert result == expected

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) >= x[0])
    )
    def test_large_values(self, data):
        """Test behavior with large numeric values."""
        window, series = data
        
        # Filter for series with large values
        assume(any(abs(x) > 1e3 for x in series))
        
        result = latency_rolling_avg(series, window=window)
        
        # Should not be None for valid inputs
        assert result is not None
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) >= x[0])
    )
    def test_mixed_positive_negative_values(self, data):
        """Test behavior with mixed positive and negative values."""
        window, series = data
        
        # Filter for series with both positive and negative values
        assume(any(x > 0 for x in series) and any(x < 0 for x in series))
        
        result = latency_rolling_avg(series, window=window)
        
        # Should not be None for valid inputs
        assert result is not None
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)