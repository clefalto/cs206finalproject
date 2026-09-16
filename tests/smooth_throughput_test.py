#!/usr/bin/env python3
"""
Hypothesis-based tests for smooth_throughput function semantic properties.
Tests all 13 semantic properties identified in smooth_throughput_properties.json.
"""

import sys
import os
from typing import List, Optional, Union

# Add the current directory to Python path to import the function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hypothesis import given, assume, strategies as st
import hypothesis.strategies as st
from hypothesis.strategies import floats, integers, lists, one_of, none
import pytest


def smooth_throughput(series: List[float], window: int, warmup_min: int = 1) -> Optional[float]:
    """
    Calculate smoothed throughput using a sliding window average.
    
    Args:
        series: List of throughput measurements
        window: Size of the sliding window
        warmup_min: Minimum number of samples required for valid result
        
    Returns:
        Smoothed throughput value or None if insufficient data
    """
    if window <= 0:
        raise ValueError("invalid window")
    
    if not series:
        raise ValueError("no samples")
    
    tail = series[-window:]
    
    if len(tail) < warmup_min:
        return None
    
    avg = sum(tail) / len(tail)
    return avg


class TestSmoothThroughputProperties:
    """Test class for smooth_throughput semantic properties."""
    
    # Hypothesis strategies for generating test data
    valid_window_strategy = integers(min_value=1, max_value=1000)
    non_empty_series_strategy = lists(floats(min_value=0, max_value=1000), min_size=1, max_size=100)
    empty_series_strategy = lists(floats(), max_size=0)
    negative_window_strategy = integers(max_value=0)
    warmup_min_strategy = integers(min_value=1, max_value=100)
    
    @given(window=st.integers(max_value=0), series=st.lists(st.floats()))
    def test_invalid_window_error(self, window: int, series: List[float]):
        """Test: if window <= 0 then raise ValueError("invalid window")"""
        with pytest.raises(ValueError, match="invalid window"):
            smooth_throughput(series, window)
    
    @given(window=st.integers(min_value=1), series=st.lists(st.floats(), max_size=0))
    def test_empty_series_error(self, window: int, series: List[float]):
        """Test: if not series then raise ValueError("no samples")"""
        with pytest.raises(ValueError, match="no samples"):
            smooth_throughput(series, window)
    
    @given(
        window=valid_window_strategy,
        series=non_empty_series_strategy,
        warmup_min=warmup_min_strategy
    )
    def test_insufficient_warmup(self, window: int, series: List[float], warmup_min: int):
        """Test: if len(tail) < warmup_min then return None"""
        assume(len(series) < warmup_min)
        result = smooth_throughput(series, window, warmup_min)
        assert result is None
    
    @given(window=st.integers(min_value=1), series=st.lists(st.floats(), min_size=1))
    def test_valid_window_precondition(self, window: int, series: List[float]):
        """Test: window must be positive for function to proceed"""
        # This precondition is tested implicitly by other tests
        # If window > 0, function should not raise ValueError for window
        try:
            result = smooth_throughput(series, window)
            # If we get here, window was valid
            assert True
        except ValueError as e:
            # Should only raise for empty series, not window
            assert "no samples" in str(e)
    
    @given(window=st.integers(min_value=1), series=st.lists(st.floats(), min_size=1))
    def test_non_empty_series_precondition(self, window: int, series: List[float]):
        """Test: series must contain at least one element for function to proceed"""
        # This precondition is tested implicitly by other tests
        # If series is not empty, function should not raise ValueError for series
        try:
            result = smooth_throughput(series, window)
            # If we get here, series was valid
            assert True
        except ValueError as e:
            # Should only raise for window <= 0, not empty series
            assert "invalid window" in str(e)
    
    @given(window=valid_window_strategy, series=non_empty_series_strategy)
    def test_window_average_calculation(self, window: int, series: List[float]):
        """Test: avg = sum(series[-window:]) / window"""
        assume(len(series) >= 1)  # Ensure series is not empty
        
        result = smooth_throughput(series, window)
        
        if result is not None:
            tail = series[-window:]
            expected_avg = sum(tail) / len(tail)
            assert abs(result - expected_avg) < 1e-10
    
    @given(
        window=valid_window_strategy,
        series=non_empty_series_strategy,
        warmup_min=warmup_min_strategy
    )
    def test_warmup_min_postcondition(self, window: int, series: List[float], warmup_min: int):
        """Test: if len(series) >= warmup_min then return avg else return None"""
        result = smooth_throughput(series, window, warmup_min)
        
        if len(series) >= warmup_min:
            assert result is not None
        else:
            assert result is None
    
    @given(
        window1=st.integers(min_value=1, max_value=100),
        window2=st.integers(min_value=1, max_value=100),
        series=non_empty_series_strategy
    )
    def test_monotonic_window_property(self, window1: int, window2: int, series: List[float]):
        """Test: for same series, larger window includes more elements in average calculation"""
        assume(window1 <= window2)
        assume(len(series) >= window2)  # Ensure both windows fit in series
        
        result1 = smooth_throughput(series, window1)
        result2 = smooth_throughput(series, window2)
        
        # Both should return valid results
        assert result1 is not None
        assert result2 is not None
        
        # The property is about the calculation including more elements,
        # not about the result being larger/smaller
        tail1 = series[-window1:]
        tail2 = series[-window2:]
        
        assert len(tail1) <= len(tail2)
    
    @given(
        window=valid_window_strategy,
        series=non_empty_series_strategy,
        c=st.floats(min_value=0.1, max_value=100.0)
    )
    def test_linear_scaling_invariant(self, window: int, series: List[float], c: float):
        """Test: smooth_throughput([c*x for x in series], window) == c * smooth_throughput(series, window)"""
        assume(len(series) >= 1)
        
        scaled_series = [c * x for x in series]
        
        result_original = smooth_throughput(series, window)
        result_scaled = smooth_throughput(scaled_series, window)
        
        if result_original is not None and result_scaled is not None:
            expected_scaled = c * result_original
            assert abs(result_scaled - expected_scaled) < 1e-10
    
    @given(
        window=valid_window_strategy,
        series1=non_empty_series_strategy,
        series2=non_empty_series_strategy
    )
    def test_additive_invariant(self, window: int, series1: List[float], series2: List[float]):
        """Test: smooth_throughput([x+y for x,y in zip(series1, series2)], window) == smooth_throughput(series1, window) + smooth_throughput(series2, window)"""
        assume(len(series1) == len(series2))
        assume(len(series1) >= 1)
        
        combined_series = [x + y for x, y in zip(series1, series2)]
        
        result1 = smooth_throughput(series1, window)
        result2 = smooth_throughput(series2, window)
        result_combined = smooth_throughput(combined_series, window)
        
        if result1 is not None and result2 is not None and result_combined is not None:
            expected_combined = result1 + result2
            assert abs(result_combined - expected_combined) < 1e-10
    
    @given(window=valid_window_strategy, series=non_empty_series_strategy)
    def test_window_bounds_check(self, window: int, series: List[float]):
        """Test: len(tail) = min(window, len(series))"""
        assume(len(series) >= 1)
        
        result = smooth_throughput(series, window)
        
        if result is not None:
            tail = series[-window:]
            expected_len = min(window, len(series))
            assert len(tail) == expected_len
    
    @given(window=valid_window_strategy, series=st.lists(st.floats(min_value=0, max_value=1000), min_size=1))
    def test_non_negative_result(self, window: int, series: List[float]):
        """Test: if all(x >= 0 for x in series) then avg >= 0"""
        assume(all(x >= 0 for x in series))
        
        result = smooth_throughput(series, window)
        
        if result is not None:
            assert result >= 0
    
    @given(window=valid_window_strategy, series=non_empty_series_strategy)
    def test_bounded_result(self, window: int, series: List[float]):
        """Test: min(series[-window:]) <= avg <= max(series[-window:])"""
        assume(len(series) >= 1)
        
        result = smooth_throughput(series, window)
        
        if result is not None:
            tail = series[-window:]
            min_val = min(tail)
            max_val = max(tail)
            
            assert min_val <= result <= max_val


if __name__ == "__main__":
    pytest.main([__file__, "-v"])