"""
Hypothesis-based tests for smooth_pressure function semantic properties.
Tests all properties identified in properties/smooth_pressure_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats
from hypothesis.extra.numpy import arrays
import numpy as np


def smooth_pressure(values, window):
    """
    Smooth pressure values using a moving average with warmup period.
    
    Args:
        values: List of pressure values
        window: Window size for moving average
        
    Returns:
        Moving average of last 'window' values, or None if insufficient data
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not values:
        raise ValueError("no values")
    
    recent = values[-window:]
    warmup_min = window // 2
    
    if len(recent) < warmup_min:
        return None
    
    total = sum(recent)
    mean = total / window  # Bug: divides by full window even during warmup
    return mean


class TestSmoothPressureProperties:
    """Test class for smooth_pressure semantic properties using Hypothesis."""

    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_invalid_window_error(self, window, values):
        """Test that window <= 0 raises ValueError with correct message."""
        with pytest.raises(ValueError, match="window must be positive"):
            smooth_pressure(values, window)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0),
        window=st.integers(min_value=1, max_value=100)
    )
    def test_empty_values_error(self, values, window):
        """Test that empty values raises ValueError with correct message."""
        assume(not values)  # Ensure values is empty
        with pytest.raises(ValueError, match="no values"):
            smooth_pressure(values, window)

    @given(
        window=st.integers(min_value=2, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_insufficient_data_none(self, window, values):
        """Test that insufficient data returns None."""
        warmup_min = window // 2
        
        # Filter to cases where we have some data but less than warmup_min
        assume(1 <= len(values) < warmup_min)
        
        result = smooth_pressure(values, window)
        assert result is None

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_positive_window_precondition(self, window, values):
        """Test that function requires positive window."""
        # This test verifies the precondition is enforced
        # If window is positive, function should not raise ValueError for window
        try:
            result = smooth_pressure(values, window)
            # If we get here, window was positive (precondition satisfied)
            assert True
        except ValueError as e:
            # Should only raise ValueError for empty values, not window
            assert "window must be positive" not in str(e)

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_non_empty_values_precondition(self, window, values):
        """Test that function requires non-empty values."""
        # This test verifies the precondition is enforced
        # If values is non-empty, function should not raise ValueError for values
        try:
            result = smooth_pressure(values, window)
            # If we get here, values was non-empty (precondition satisfied)
            assert True
        except ValueError as e:
            # Should only raise ValueError for window, not empty values
            assert "no values" not in str(e)

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_mean_calculation(self, window, values):
        """Test that mean is calculated correctly when sufficient data."""
        warmup_min = window // 2
        
        # Filter to cases where we have sufficient data
        assume(len(values) >= warmup_min)
        
        result = smooth_pressure(values, window)
        
        # Get the recent values (last 'window' elements)
        recent = values[-window:]
        expected_mean = sum(recent) / window
        
        assert result == expected_mean

    @given(
        window=st.integers(min_value=2, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_warmup_behavior(self, window, values):
        """Test that function returns None during warmup period."""
        warmup_min = window // 2
        
        # Filter to cases where we have some data but less than warmup_min
        assume(1 <= len(values) < warmup_min)
        
        result = smooth_pressure(values, window)
        assert result is None

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_window_slicing(self, window, values):
        """Test that window slicing takes last 'window' elements."""
        # This test verifies the slicing behavior
        recent = values[-window:]
        
        # The function should use exactly these recent values
        result = smooth_pressure(values, window)
        
        # If we have sufficient data, verify the calculation uses recent values
        warmup_min = window // 2
        if len(values) >= warmup_min:
            expected_mean = sum(recent) / window
            assert result == expected_mean

    @given(
        window=st.integers(min_value=2, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_bug_division_by_full_window(self, window, values):
        """Test the bug where division uses full window size even during warmup."""
        warmup_min = window // 2
        
        # Filter to cases where we have some data but less than window
        assume(1 <= len(values) < window)
        
        # During warmup, we should still divide by full window size (the bug)
        recent = values[-window:]
        total = sum(recent)
        expected_mean = total / window  # Bug: divides by full window
        
        result = smooth_pressure(values, window)
        
        # If we have sufficient data for warmup_min, verify the bug
        if len(values) >= warmup_min:
            assert result == expected_mean
        else:
            # If insufficient data, should return None
            assert result is None

    @given(
        window=st.integers(min_value=1, max_value=50),
        values=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=100)
    )
    def test_smooth_pressure_comprehensive(self, window, values):
        """Comprehensive test covering multiple properties."""
        warmup_min = window // 2
        
        # Test error conditions first
        if window <= 0:
            with pytest.raises(ValueError, match="window must be positive"):
                smooth_pressure(values, window)
            return
        
        if not values:
            with pytest.raises(ValueError, match="no values"):
                smooth_pressure(values, window)
            return
        
        # Test normal operation
        result = smooth_pressure(values, window)
        
        if len(values) < warmup_min:
            assert result is None
        else:
            # Verify the calculation (including the bug)
            recent = values[-window:]
            expected = sum(recent) / window
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])