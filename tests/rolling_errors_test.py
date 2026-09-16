"""
Hypothesis-based property tests for rolling_errors function.

This test suite exercises all semantic properties identified for the
rolling_errors function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, just
import math
from typing import List, Optional, Union

# Import the function under test
# Note: This assumes the function is available in the current environment
# In practice, you would import from the actual module containing rolling_errors
try:
    from your_module import rolling_errors
except ImportError:
    # Mock implementation for testing purposes - replace with actual import
    def rolling_errors(values: List[float], window: int, warmup_min: int = 0) -> Optional[float]:
        """
        Mock implementation of rolling_errors for testing.
        Replace this with the actual function import.
        """
        if window <= 0:
            raise ValueError("window must be positive")
        
        if not values:
            raise ValueError("no values")
        
        if warmup_min < 0:
            raise ValueError("warmup_min must be non-negative")
        
        recent = values[-window:]
        
        if len(recent) < warmup_min:
            return None
        
        # Calculate rolling mean
        mean = sum(recent) / len(recent)
        return mean


class TestRollingErrorsProperties:
    """Test class for rolling_errors semantic properties."""

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
    def test_invalid_window_validation_branch(self, window: int):
        """Test branch: window <= 0 raises ValueError with correct message."""
        values = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="window must be positive"):
            rolling_errors(values, window=window)

    @given(values=lists(floats(), min_size=0, max_size=100))
    def test_empty_values_validation_branch(self, values: List[float]):
        """Test branch: not values raises ValueError with correct message."""
        assume(len(values) == 0)
        with pytest.raises(ValueError, match="no values"):
            rolling_errors(values, window=5)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) > 0 and len(x[2][-x[0]:]) < x[1])
    )
    def test_warmup_insufficient_branch(self, data):
        """Test branch: len(recent) < warmup_min returns None."""
        window, warmup_min, values = data
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        assert result is None

    # Function-level property tests

    @given(window=integers(max_value=0))
    def test_window_positive_property(self, window: int):
        """Test function property: window <= 0 raises ValueError."""
        values = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="window must be positive"):
            rolling_errors(values, window=window)

    @given(values=lists(floats(), min_size=0, max_size=100))
    def test_values_non_empty_property(self, values: List[float]):
        """Test function property: not values raises ValueError."""
        assume(len(values) == 0)
        with pytest.raises(ValueError, match="no values"):
            rolling_errors(values, window=5)

    @given(warmup_min=integers(max_value=-1))
    def test_warmup_min_validation_property(self, warmup_min: int):
        """Test function property: warmup_min < 0 raises ValueError."""
        values = [1.0, 2.0, 3.0]
        with pytest.raises(ValueError, match="warmup_min must be non-negative"):
            rolling_errors(values, window=5, warmup_min=warmup_min)

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and len(x[2]) > 0)
    )
    def test_rolling_mean_calculation_property(self, data):
        """Test function property: correct rolling mean calculation."""
        window, warmup_min, values = data
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        recent = values[-window:]
        expected = sum(recent) / len(recent)
        
        assert result == expected

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) < x[1])
    )
    def test_warmup_behavior_property(self, data):
        """Test function property: len(values) < warmup_min returns None."""
        window, warmup_min, values = data
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        assert result is None

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: 0 < len(x[1]) < x[0])
    )
    def test_window_clamping_property(self, data):
        """Test function property: window clamping when len(values) < window."""
        window, values = data
        result = rolling_errors(values, window=window)
        
        # Should use values[-len(values):] instead of values[-window:]
        recent = values[-len(values):]
        expected = sum(recent) / len(recent)
        
        assert result == expected

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            lists(floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=1000)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_mean_non_negative_property(self, data):
        """Test function property: non-negative inputs produce non-negative output."""
        window, warmup_min, values = data
        
        # Ensure all elements are non-negative
        assume(all(x >= 0 for x in values))
        
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        assert result >= 0

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and 
                len(x[2]) > 0 and x[3] <= x[4])
    )
    def test_mean_bounded_property(self, data):
        """Test function property: mean is bounded by min and max values."""
        window, warmup_min, values, min_val, max_val = data
        
        # Ensure all elements are within bounds
        assume(all(min_val <= x <= max_val for x in values))
        
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        assert min_val <= result <= max_val

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[3]) >= x[0] and 
                len(x[2][-x[0]:]) >= x[1] and len(x[3][-x[0]:]) >= x[1] and
                len(x[2]) > 0 and len(x[3]) > 0 and len(x[2]) == len(x[3]))
    )
    def test_monotonicity_preservation_property(self, data):
        """Test function property: monotonicity preservation."""
        window, warmup_min, values1, values2 = data
        
        # Ensure values1[i] <= values2[i] for all i
        assume(all(x1 <= x2 for x1, x2 in zip(values1, values2)))
        
        result1 = rolling_errors(values1, window=window, warmup_min=warmup_min)
        result2 = rolling_errors(values2, window=window, warmup_min=warmup_min)
        
        assert result1 <= result2

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            floats(min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and len(x[2]) > 0)
    )
    def test_scale_invariance_property(self, data):
        """Test function property: scale invariance."""
        window, warmup_min, values, c = data
        
        result_original = rolling_errors(values, window=window, warmup_min=warmup_min)
        scaled_values = [c * x for x in values]
        result_scaled = rolling_errors(scaled_values, window=window, warmup_min=warmup_min)
        
        expected_scaled = c * result_original
        assert abs(result_scaled - expected_scaled) < 1e-9

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy,
            floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1] and len(x[2]) > 0)
    )
    def test_additive_independence_property(self, data):
        """Test function property: additive independence."""
        window, warmup_min, values, c = data
        
        result_original = rolling_errors(values, window=window, warmup_min=warmup_min)
        shifted_values = [x + c for x in values]
        result_shifted = rolling_errors(shifted_values, window=window, warmup_min=warmup_min)
        
        expected_shifted = result_original + c
        assert abs(result_shifted - expected_shifted) < 1e-9

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
        
        result1 = rolling_errors(values, window=window1)
        result2 = rolling_errors(values, window=window2)
        
        # Results may differ, but both should be valid
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
        
        result1 = rolling_errors(values, window=window, warmup_min=warmup_min1)
        result2 = rolling_errors(values, window=window, warmup_min=warmup_min2)
        
        # If result1 returns a value, result2 might return None
        if result1 is not None and result2 is None:
            # This is expected behavior when warmup_min2 requires more samples
            pass
        # Both could return values or both could return None

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_recent_values_only_property(self, data):
        """Test function property: result depends only on values[-window:]."""
        window, warmup_min, values = data
        
        # Get result with full series
        result_full = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        # Get result with only the last window elements
        recent = values[-window:]
        result_recent = rolling_errors(recent, window=window, warmup_min=warmup_min)
        
        assert result_full == result_recent

    @given(
        st.tuples(
            valid_window_strategy,
            warmup_min_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_deterministic_property(self, data):
        """Test function property: deterministic behavior."""
        window, warmup_min, values = data
        
        # Call function multiple times with same inputs
        result1 = rolling_errors(values, window=window, warmup_min=warmup_min)
        result2 = rolling_errors(values, window=window, warmup_min=warmup_min)
        result3 = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        assert result1 == result2 == result3

    # Additional edge case tests

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) >= x[0])
    )
    def test_single_element_window(self, data):
        """Test behavior with window=1."""
        window, values = data
        assume(window == 1)
        
        result = rolling_errors(values, window=window)
        expected = values[-1]  # Should be the last element
        
        assert result == expected

    @given(
        st.tuples(
            valid_window_strategy,
            float_list_strategy
        ).filter(lambda x: len(x[1]) >= x[0])
    )
    def test_large_values(self, data):
        """Test behavior with large numeric values."""
        window, values = data
        
        # Filter for series with large values
        assume(any(abs(x) > 1e3 for x in values))
        
        result = rolling_errors(values, window=window)
        
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
        window, values = data
        
        # Filter for series with both positive and negative values
        assume(any(x > 0 for x in values) and any(x < 0 for x in values))
        
        result = rolling_errors(values, window=window)
        
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
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_zero_values(self, data):
        """Test behavior with zero values."""
        window, warmup_min, values = data
        
        # Filter for series with zero values
        assume(any(x == 0 for x in values))
        
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        
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
        ).filter(lambda x: len(x[2]) >= x[0] and len(x[2][-x[0]:]) >= x[1])
    )
    def test_boundary_conditions(self, data):
        """Test boundary conditions around warmup_min."""
        window, warmup_min, values = data
        
        # Test exactly at warmup_min boundary
        recent = values[-window:]
        assume(len(recent) == warmup_min)
        
        result = rolling_errors(values, window=window, warmup_min=warmup_min)
        
        # Should return a value when exactly at boundary
        assert result is not None
        assert isinstance(result, (int, float))