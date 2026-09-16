"""
Hypothesis tests for metric_rolling_avg function semantic properties.

This test suite exercises all semantic properties identified in
properties/metric_rolling_avg_properties.json using the Hypothesis
testing framework to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats, one_of

from dataset.python_programs.metric_rolling_avg import metric_rolling_avg


class TestMetricRollingAvgSemanticProperties:
    """Test class for metric_rolling_avg semantic properties."""

    # ============================================================================
    # Branch Properties Tests
    # ============================================================================

    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        min_samples=st.integers(min_value=1)
    )
    def test_invalid_window_error(self, window, values, min_samples):
        """
        Branch property: invalid_window_error
        Formal: if window <= 0 then raise ValueError("window must be positive")
        """
        with pytest.raises(ValueError, match="window must be positive"):
            metric_rolling_avg(values, window=window, min_samples=min_samples)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_empty_values_error(self, values, window, min_samples):
        """
        Branch property: empty_values_error
        Formal: if not values then raise ValueError("no values")
        """
        with pytest.raises(ValueError, match="no values"):
            metric_rolling_avg(values, window=window, min_samples=min_samples)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_insufficient_samples_none(self, values, window, min_samples):
        """
        Branch property: insufficient_samples_none
        Formal: if len(tail) < min_samples then return None
        """
        assume(len(values) < min_samples)
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        assert result is None

    # ============================================================================
    # Function Properties Tests
    # ============================================================================

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(max_value=0),
        min_samples=st.integers(min_value=1)
    )
    def test_positive_window_requirement(self, values, window, min_samples):
        """
        Function property: positive_window_requirement
        Precondition: window > 0
        Formal: window must be positive for function to proceed
        """
        # This test verifies that when window <= 0, the function raises an error
        # rather than proceeding with the calculation
        with pytest.raises(ValueError, match="window must be positive"):
            metric_rolling_avg(values, window=window, min_samples=min_samples)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_non_empty_values_requirement(self, values, window, min_samples):
        """
        Function property: non_empty_values_requirement
        Precondition: values is not empty
        Formal: values must contain at least one element for function to proceed
        """
        # This test verifies that when values is empty, the function raises an error
        # rather than proceeding with the calculation
        with pytest.raises(ValueError, match="no values"):
            metric_rolling_avg(values, window=window, min_samples=min_samples)

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_rolling_average_calculation(self, values, window, min_samples):
        """
        Function property: rolling_average_calculation
        Precondition: window > 0 and values is not empty
        Formal: avg = sum(values[-window:]) / window
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Calculate expected average manually
        tail = values[-window:]
        expected_avg = sum(tail) / window
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        # If we have sufficient samples, result should equal expected average
        if len(tail) >= min_samples:
            assert result == expected_avg
        else:
            assert result is None

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_minimum_samples_check(self, values, window, min_samples):
        """
        Function property: minimum_samples_check
        Precondition: window > 0 and values is not empty
        Formal: if len(values[-window:]) < min_samples then return None else return avg
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        tail = values[-window:]
        expected_length = min(len(values), window)
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        if expected_length < min_samples:
            assert result is None
        else:
            # Should return a numeric value
            assert result is not None
            assert isinstance(result, (int, float))

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_tail_extraction(self, values, window, min_samples):
        """
        Function property: tail_extraction
        Precondition: window > 0 and values is not empty
        Formal: tail = values[-window:]
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Calculate what the tail should be
        expected_tail = values[-window:]
        
        # Get the result to ensure the function runs without error
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        # The function should use the correct tail for calculation
        # We verify this indirectly by checking the calculation result
        if len(expected_tail) >= min_samples:
            expected_avg = sum(expected_tail) / window
            assert result == expected_avg

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_sum_calculation(self, values, window, min_samples):
        """
        Function property: sum_calculation
        Precondition: window > 0 and values is not empty
        Formal: total = sum(tail)
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Calculate expected sum manually
        tail = values[-window:]
        expected_total = sum(tail)
        
        # Calculate expected average
        expected_avg = expected_total / window
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        if len(tail) >= min_samples:
            assert result == expected_avg
        else:
            assert result is None

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_division_by_window(self, values, window, min_samples):
        """
        Function property: division_by_window
        Precondition: window > 0 and values is not empty
        Formal: avg = total / window
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Calculate expected result manually
        tail = values[-window:]
        total = sum(tail)
        expected_avg = total / window
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        if len(tail) >= min_samples:
            assert result == expected_avg
        else:
            assert result is None

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_potential_none_return(self, values, window, min_samples):
        """
        Function property: potential_none_return
        Precondition: window > 0 and values is not empty
        Formal: function may return None if insufficient samples
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        # Result can be either None or a numeric value
        assert result is None or isinstance(result, (int, float))

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        window=st.integers(min_value=1),
        min_samples=st.integers(min_value=1)
    )
    def test_numeric_return(self, values, window, min_samples):
        """
        Function property: numeric_return
        Precondition: window > 0 and values is not empty and sufficient samples
        Formal: function returns numeric average when conditions are met
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        # Ensure we have sufficient samples
        tail = values[-window:]
        assume(len(tail) >= min_samples)
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        # Should return a numeric value when conditions are met
        assert result is not None
        assert isinstance(result, (int, float))

    # ============================================================================
    # Additional Edge Case Tests
    # ============================================================================

    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        window=st.integers(min_value=1, max_value=1000),
        min_samples=st.integers(min_value=1, max_value=100)
    )
    def test_edge_cases_with_various_inputs(self, values, window, min_samples):
        """
        Additional test for edge cases with various input combinations.
        """
        # Test that the function handles various combinations of inputs correctly
        try:
            result = metric_rolling_avg(values, window=window, min_samples=min_samples)
            
            # If result is not None, it should be a number
            if result is not None:
                assert isinstance(result, (int, float))
                # Result should be finite (not infinity)
                assert not (result != result)  # Check for NaN
                assert abs(result) != float('inf')  # Check for infinity
                
        except ValueError as e:
            # Only specific error messages are expected
            assert str(e) in ["window must be positive", "no values"]

    @given(
        values=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=50),
        window=st.integers(min_value=1, max_value=50),
        min_samples=st.integers(min_value=1, max_value=50)
    )
    def test_bounded_numeric_inputs(self, values, window, min_samples):
        """
        Test with bounded numeric inputs to ensure predictable behavior.
        """
        assume(window > 0)
        assume(len(values) > 0)
        
        result = metric_rolling_avg(values, window=window, min_samples=min_samples)
        
        if result is not None:
            # Result should be within reasonable bounds
            assert isinstance(result, (int, float))
            assert -1000 <= result <= 1000  # Should be within input value bounds