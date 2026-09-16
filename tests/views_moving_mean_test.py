"""
Test file for views_moving_mean function using Hypothesis testing framework.
Tests all semantic properties identified in properties/views_moving_mean_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.views_moving_mean import views_moving_mean


class TestViewsMovingMean:
    """Test class for views_moving_mean function."""

    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_invalid_window_error(self, window, values):
        """
        Test: if window <= 0 then ValueError("window must be positive") is raised
        Property: invalid_window_error
        Scope: branch
        """
        with pytest.raises(ValueError, match="window must be positive"):
            views_moving_mean(values, window=window)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0)
    )
    def test_empty_values_error(self, values):
        """
        Test: if not values then ValueError("no values") is raised
        Property: empty_values_error
        Scope: branch
        """
        with pytest.raises(ValueError, match="no values"):
            views_moving_mean(values)

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        warmup_min=st.integers(min_value=1, max_value=100)
    )
    def test_insufficient_data(self, window, values, warmup_min):
        """
        Test: if len(recent) < warmup_min then None is returned
        Property: insufficient_data
        Scope: branch
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        recent = values[-window:]
        if len(recent) < warmup_min:
            result = views_moving_mean(values, window=window, warmup_min=warmup_min)
            assert result is None

    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_positive_window_requirement(self, window, values):
        """
        Test: window must be positive for valid computation
        Property: positive_window_requirement
        Scope: function
        Precondition: window > 0
        """
        with pytest.raises(ValueError, match="window must be positive"):
            views_moving_mean(values, window=window)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0)
    )
    def test_non_empty_values_requirement(self, values):
        """
        Test: values must contain at least one element for valid computation
        Property: non_empty_values_requirement
        Scope: function
        Precondition: values is not empty
        """
        with pytest.raises(ValueError, match="no values"):
            views_moving_mean(values)

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        warmup_min=st.integers(min_value=1, max_value=100)
    )
    def test_moving_average_computation(self, window, values, warmup_min):
        """
        Test: mean = sum(values[-window:]) / window
        Property: moving_average_computation
        Scope: function
        Precondition: window > 0 and values is not empty and len(recent) >= warmup_min
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        recent = values[-window:]
        if len(recent) >= warmup_min:
            result = views_moving_mean(values, window=window, warmup_min=warmup_min)
            expected = sum(recent) / window
            assert result == expected

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        warmup_min=st.integers(min_value=1, max_value=100)
    )
    def test_warmup_period_handling(self, window, values, warmup_min):
        """
        Test: if len(values[-window:]) < warmup_min then None is returned, otherwise moving average is computed
        Property: warmup_period_handling
        Scope: function
        Precondition: window > 0 and values is not empty
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        recent = values[-window:]
        result = views_moving_mean(values, window=window, warmup_min=warmup_min)
        
        if len(recent) < warmup_min:
            assert result is None
        else:
            expected = sum(recent) / window
            assert result == expected

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100)
    )
    def test_bug_division_by_full_window(self, window, values):
        """
        Test: mean = sum(recent) / window (divides by full window even during warmup period)
        Property: bug_division_by_full_window
        Scope: function
        Precondition: window > 0 and values is not empty and len(recent) < window
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        recent = values[-window:]
        if len(recent) < window:
            # This test verifies the bug behavior where division is by full window
            # even when we have fewer than window elements
            result = views_moving_mean(values, window=window)
            expected = sum(recent) / window  # Bug: should be sum(recent) / len(recent)
            assert result == expected

    # Additional comprehensive tests for edge cases and boundary conditions

    @given(
        window=st.integers(min_value=1, max_value=100),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        warmup_min=st.integers(min_value=0, max_value=100)
    )
    def test_boundary_conditions(self, window, values, warmup_min):
        """
        Test boundary conditions and edge cases for the function.
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Test with warmup_min = 0 (should always return a value)
        if warmup_min == 0:
            result = views_moving_mean(values, window=window, warmup_min=warmup_min)
            recent = values[-window:]
            expected = sum(recent) / window
            assert result == expected
        
        # Test with warmup_min > window (should always return None)
        if warmup_min > window:
            result = views_moving_mean(values, window=window, warmup_min=warmup_min)
            assert result is None

    @given(
        window=st.integers(min_value=1, max_value=50),
        values=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=50)
    )
    def test_numerical_stability(self, window, values):
        """
        Test numerical stability with various input ranges.
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Test with warmup_min = 1 to ensure we get a result
        result = views_moving_mean(values, window=window, warmup_min=1)
        
        # Verify the result is a float or None
        assert result is None or isinstance(result, (int, float))
        
        # If we get a result, verify it's finite
        if result is not None:
            assert np.isfinite(result)

    def test_specific_examples(self):
        """
        Test specific examples to verify expected behavior.
        """
        # Test case 1: Normal case with sufficient data
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = views_moving_mean(values, window=3, warmup_min=2)
        expected = (3.0 + 4.0 + 5.0) / 3  # 4.0
        assert result == expected

        # Test case 2: Insufficient data for warmup
        values = [1.0, 2.0]
        result = views_moving_mean(values, window=3, warmup_min=3)
        assert result is None

        # Test case 3: Warmup_min = 0 (always return value)
        values = [1.0, 2.0]
        result = views_moving_mean(values, window=3, warmup_min=0)
        expected = (1.0 + 2.0) / 3  # Bug: should be / 2
        assert result == expected

        # Test case 4: Error cases
        with pytest.raises(ValueError, match="window must be positive"):
            views_moving_mean([1.0, 2.0], window=0)
        
        with pytest.raises(ValueError, match="no values"):
            views_moving_mean([])