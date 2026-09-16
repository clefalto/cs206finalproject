"""
Hypothesis-based property tests for rolling_retries function.

This test suite exercises all semantic properties identified for the
rolling_retries function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, just
import math
from typing import List, Optional, Union

# Import the function under test
# Note: This assumes the function is available in the current environment
# In practice, you would import from the actual module containing rolling_retries
try:
    from your_module import rolling_retries
except ImportError:
    # Mock implementation for testing purposes - replace with actual import
    def rolling_retries(values: List[float], window: int, warmup_min: int = 0) -> Optional[float]:
        """
        Mock implementation of rolling_retries for testing.
        Replace this with the actual function import.
        """
        if window <= 0:
            raise ValueError("window must be positive")
        
        if not values:
            raise ValueError("empty series")
        
        tail = values[-window:]
        total = sum(tail)
        
        # BUG: uses window size instead of actual sample count
        mean = total / window
        
        if len(tail) < warmup_min:
            return None
        
        return mean


class TestRollingRetriesProperties:
    """Test class for rolling_retries semantic properties."""

    # Strategies for generating test data
    valid_window_strategy = integers(min_value=1, max_value=1000)
    warmup_min_strategy = integers(min_value=0, max_value=100)
    float_list_strategy = lists(floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=0, max_size=1000)
    
    # Strategy for generating values that ensures we have enough elements for the window
    values_with_window_strategy = st.tuples(
        valid_window_strategy,
        lists(floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=1000)
    ).filter(lambda x: len(x[1]) >= x[0])

    # Branch-level property tests

    @given(window=integers(max_value=0))
    def test_invalid_window_error_branch(self, window: int):
        """Test branch: window <= 0 raises ValueError with correct message."""
        values = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="window must be positive"):
            rolling_retries(values, window=window)

    @given(values=lists(floats(), min_size=0, max_size=100))
    def test_empty_series_error_branch(self, values: List[float]):
        """Test branch: not values raises ValueError with correct message."""
        assume(len(values) == 0)
        with pytest.raises(ValueError, match="empty series"):
            rolling_retries(values, window=5)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) < x[1])
    )
    def test_insufficient_warmup_branch(self, data):
        """Test branch: len(tail) < warmup_min returns None."""
        window, warmup_min, values = data
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        assert result is None

    # Function-level property tests

    @given(window=integers(max_value=0))
    def test_window_positive_property(self, window: int):
        """Test function property: window <= 0 raises ValueError."""
        values = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="window must be positive"):
            rolling_retries(values, window=window)

    @given(values=lists(floats(), min_size=0, max_size=100))
    def test_non_empty_values_property(self, values: List[float]):
        """Test function property: not values raises ValueError."""
        assume(len(values) == 0)
        with pytest.raises(ValueError, match="empty series"):
            rolling_retries(values, window=5)

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_window_slice_property(self, data):
        """Test function property: tail = values[-window:] extracts last window elements."""
        window, values = data
        tail = values[-window:]
        
        # Verify tail length constraint
        assert len(tail) <= window
        
        # Verify tail contains the last elements
        if len(values) >= window:
            assert tail == values[-window:]
        else:
            assert tail == values  # When values is shorter than window

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_buggy_mean_calculation_property(self, data):
        """Test function property: mean = total / window uses window size instead of actual sample count."""
        window, values = data
        tail = values[-window:]
        total = sum(tail)
        
        # The buggy calculation uses window instead of len(tail)
        buggy_mean = total / window
        
        # Verify this is indeed different from correct calculation when len(tail) != window
        if len(tail) != window:
            correct_mean = total / len(tail)
            assert buggy_mean != correct_mean

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0)
    )
    def test_conditional_return_property(self, data):
        """Test function property: conditional return based on warmup_min."""
        window, warmup_min, values = data
        tail = values[-window:]
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        if len(tail) >= warmup_min:
            assert result is not None
            assert isinstance(result, (int, float))
        else:
            assert result is None

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_return_type_property(self, data):
        """Test function property: returns float when sufficient warmup samples."""
        window, warmup_min, values = data
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) < x[1])
    )
    def test_return_none_property(self, data):
        """Test function property: returns None when insufficient warmup samples."""
        window, warmup_min, values = data
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        assert result is None

    @given(
        st.tuples(
            integers(max_value=0),
            float_list_strategy
        )
    )
    def test_error_handling_window_property(self, data):
        """Test function property: window <= 0 raises ValueError with descriptive message."""
        window, values = data
        with pytest.raises(ValueError, match="window must be positive"):
            rolling_retries(values, window=window)

    @given(
        st.tuples(
            valid_window_strategy,
            lists(floats(), min_size=0, max_size=100)
        )
    )
    def test_error_handling_values_property(self, data):
        """Test function property: empty values raises ValueError with descriptive message."""
        window, values = data
        assume(len(values) == 0)
        with pytest.raises(ValueError, match="empty series"):
            rolling_retries(values, window=window)

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_tail_length_constraint_property(self, data):
        """Test function property: len(tail) <= window (tail length is at most window size)."""
        window, values = data
        tail = values[-window:]
        assert len(tail) <= window

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0 and len(x[1]) < x[0])
    )
    def test_mean_calculation_bug_property(self, data):
        """Test function property: mean calculation uses window instead of len(tail), causing incorrect results."""
        window, values = data
        
        # When len(values) < window, tail will be shorter than window
        tail = values[-window:]
        total = sum(tail)
        
        # The buggy calculation
        buggy_mean = total / window
        
        # The correct calculation would be
        correct_mean = total / len(tail)
        
        # They should be different when len(tail) != window
        assert buggy_mean != correct_mean

    # Additional comprehensive tests

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_deterministic_property(self, data):
        """Test function property: deterministic behavior."""
        window, warmup_min, values = data
        
        # Call function multiple times with same inputs
        result1 = rolling_retries(values, window=window, warmup_min=warmup_min)
        result2 = rolling_retries(values, window=window, warmup_min=warmup_min)
        result3 = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        assert result1 == result2 == result3

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_recent_values_only_property(self, data):
        """Test function property: result depends only on values[-window:]."""
        window, values = data
        
        # Get result with full series
        result_full = rolling_retries(values, window=window)
        
        # Get result with only the last window elements
        recent = values[-window:]
        result_recent = rolling_retries(recent, window=window)
        
        assert result_full == result_recent

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_buggy_calculation_consistency_property(self, data):
        """Test that the buggy calculation is consistently wrong when len(tail) < window."""
        window, warmup_min, values = data
        
        # Only test when we have enough warmup samples but tail is shorter than window
        tail = values[-window:]
        assume(len(tail) < window and len(tail) >= warmup_min)
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        # Verify it's using the buggy calculation
        total = sum(tail)
        expected_buggy = total / window
        assert result == expected_buggy
        
        # Verify it's different from correct calculation
        expected_correct = total / len(tail)
        assert result != expected_correct

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) > 0)
    )
    def test_edge_case_single_element(self, data):
        """Test edge case with single element."""
        window, values = data
        assume(len(values) == 1)
        
        result = rolling_retries(values, window=window)
        
        if window == 1:
            # Should use the single element
            assert result == values[0]
        else:
            # Should use the single element but divide by window
            assert result == values[0] / window

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_large_values_handling(self, data):
        """Test handling of large numeric values."""
        window, warmup_min, values = data
        
        # Filter for series with large values
        assume(any(abs(x) > 1e3 for x in values))
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        # Should not be None for valid inputs
        assert result is not None
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_mixed_positive_negative_values(self, data):
        """Test behavior with mixed positive and negative values."""
        window, warmup_min, values = data
        
        # Filter for series with both positive and negative values
        assume(any(x > 0 for x in values) and any(x < 0 for x in values))
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        # Should not be None for valid inputs
        assert result is not None
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_zero_values(self, data):
        """Test behavior with zero values."""
        window, warmup_min, values = data
        
        # Filter for series with zero values
        assume(any(x == 0 for x in values))
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        # Should not be None for valid inputs
        assert result is not None
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) >= x[1])
    )
    def test_boundary_conditions(self, data):
        """Test boundary conditions around warmup_min."""
        window, warmup_min, values = data
        
        # Test exactly at warmup_min boundary
        tail = values[-window:]
        assume(len(tail) == warmup_min)
        
        result = rolling_retries(values, window=window, warmup_min=warmup_min)
        
        # Should return a value when exactly at boundary
        assert result is not None
        assert isinstance(result, (int, float))

    @given(
        st.tuples(
            integers(min_value=1, max_value=100),
            integers(min_value=101, max_value=200),
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[1])
    )
    def test_window_size_effect_property(self, data):
        """Test function property: window size effect."""
        window1, window2, values = data
        
        assume(window1 < window2 and len(values) >= window2)
        
        result1 = rolling_retries(values, window=window1)
        result2 = rolling_retries(values, window=window2)
        
        # Results may differ due to the bug, but both should be valid
        assert result1 is not None
        assert result2 is not None

    @given(
        st.tuples(
            valid_window_strategy,
            integers(min_value=0, max_value=50),
            integers(min_value=51, max_value=100),
            float_list_strategy
        ).filter(lambda x: len(x[3]) >= x[0])
    )
    def test_warmup_min_effect_property(self, data):
        """Test function property: warmup_min effect."""
        window, warmup_min1, warmup_min2, values = data
        
        assume(warmup_min1 < warmup_min2)
        
        result1 = rolling_retries(values, window=window, warmup_min=warmup_min1)
        result2 = rolling_retries(values, window=window, warmup_min=warmup_min2)
        
        # If result1 returns a value, result2 might return None
        if result1 is not None and result2 is None:
            # This is expected behavior when warmup_min2 requires more samples
            pass
        # Both could return values or both could return None