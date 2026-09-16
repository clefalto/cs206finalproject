"""
Test file for sales_window_avg function using Hypothesis testing framework.
Tests all semantic properties identified in sales_window_avg_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import integers, lists, floats, composite
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.sales_window_avg import sales_window_avg


class TestSalesWindowAvg:
    """Test class for sales_window_avg function covering all semantic properties."""

    # ============================================================================
    # BRANCH-LEVEL PROPERTIES
    # ============================================================================

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False)), window=st.integers(max_value=0))
    @example(values=[], window=0)
    @example(values=[1.0], window=-1)
    @example(values=[1.0, 2.0], window=-5)
    def test_invalid_window_error(self, values, window):
        """
        Branch property: invalid_window_error
        Formal: if window <= 0 then ValueError("window must be positive") is raised
        """
        with pytest.raises(ValueError, match="window must be positive"):
            sales_window_avg(values, window=window)

    @given(window=st.integers(min_value=1))
    @example(window=1)
    @example(window=10)
    def test_empty_values_error(self, window):
        """
        Branch property: empty_values_error
        Formal: if not values then ValueError("no values") is raised
        """
        with pytest.raises(ValueError, match="no values"):
            sales_window_avg([], window=window)

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=3),
           window=st.integers(min_value=1, max_value=10),
           warmup_min=st.integers(min_value=4, max_value=10))
    @example(values=[1.0], window=1, warmup_min=2)
    @example(values=[1.0, 2.0], window=3, warmup_min=5)
    def test_insufficient_data_none(self, values, window, warmup_min):
        """
        Branch property: insufficient_data_none
        Formal: if len(recent) < warmup_min then return None
        """
        assume(len(values) < warmup_min)
        result = sales_window_avg(values, window=window, warmup_min=warmup_min)
        assert result is None

    # ============================================================================
    # FUNCTION-LEVEL PROPERTIES
    # ============================================================================

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=10))
    @example(values=[1.0], window=1, warmup_min=1)
    @example(values=[1.0, 2.0, 3.0], window=3, warmup_min=2)
    def test_positive_window_requirement(self, values, window, warmup_min):
        """
        Function property: positive_window_requirement
        Precondition: window > 0
        Formal: window must be positive for function to proceed beyond initial validation
        """
        # This test verifies that when window > 0, no ValueError is raised for window validation
        try:
            result = sales_window_avg(values, window=window, warmup_min=warmup_min)
            # If we get here, window validation passed
            assert True
        except ValueError as e:
            # Should only raise ValueError for empty values, not window
            assert "no values" in str(e)

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=10))
    @example(values=[1.0], window=1, warmup_min=1)
    @example(values=[1.0, 2.0, 3.0], window=3, warmup_min=2)
    def test_non_empty_values_requirement(self, values, window, warmup_min):
        """
        Function property: non_empty_values_requirement
        Precondition: values is not empty
        Formal: values must contain at least one element for function to proceed beyond initial validation
        """
        # This test verifies that when values is not empty, no ValueError is raised for empty values
        try:
            result = sales_window_avg(values, window=window, warmup_min=warmup_min)
            # If we get here, values validation passed
            assert True
        except ValueError as e:
            # Should only raise ValueError for window <= 0, not empty values
            assert "window must be positive" in str(e)

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20),
           window=st.integers(min_value=1, max_value=50))
    @example(values=[1.0, 2.0, 3.0, 4.0, 5.0], window=3)
    @example(values=[10.0], window=5)
    @example(values=[1.0, 2.0], window=1)
    def test_window_slice_extraction(self, values, window):
        """
        Function property: window_slice_extraction
        Precondition: window > 0 and values is not empty
        Formal: recent = values[-window:] extracts the last 'window' elements from values
        """
        # Calculate what the slice should be
        expected_recent = values[-window:]
        
        # Get the actual result (we'll verify the calculation logic separately)
        result = sales_window_avg(values, window=window, warmup_min=1)
        
        # Verify that the function uses the correct slice by checking the sum
        # Since we know the bug is in the division, we can verify the slice is correct
        # by checking that total matches sum of expected_recent
        # We'll do this by manually calculating what the mean should be with correct division
        if len(expected_recent) >= 1:  # warmup_min=1 for this test
            expected_mean = sum(expected_recent) / len(expected_recent)
            # The buggy implementation divides by window instead of len(expected_recent)
            buggy_mean = sum(expected_recent) / window
            assert result == buggy_mean  # This verifies the slice is correct and bug exists

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20),
           window=st.integers(min_value=1, max_value=50))
    @example(values=[1.0, 2.0, 3.0], window=3)
    @example(values=[5.0, 10.0], window=4)
    def test_sum_calculation(self, values, window):
        """
        Function property: sum_calculation
        Precondition: window > 0 and values is not empty
        Formal: total = sum(recent) calculates the sum of the recent window elements
        """
        expected_recent = values[-window:]
        expected_total = sum(expected_recent)
        
        # Get result and verify the sum is calculated correctly
        # We can verify this by checking that the mean calculation uses the correct total
        result = sales_window_avg(values, window=window, warmup_min=1)
        
        if len(expected_recent) >= 1:  # warmup_min=1 for this test
            # The buggy mean should be total / window
            expected_buggy_mean = expected_total / window
            assert result == expected_buggy_mean

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20),
           window=st.integers(min_value=1, max_value=50))
    @example(values=[1.0, 2.0, 3.0], window=3)
    @example(values=[4.0, 8.0], window=5)
    def test_mean_calculation_with_bug(self, values, window):
        """
        Function property: mean_calculation_with_bug
        Precondition: window > 0 and values is not empty
        Formal: mean = total / window calculates mean by dividing by full window size (bug: should divide by len(recent) during warmup)
        """
        expected_recent = values[-window:]
        expected_total = sum(expected_recent)
        
        result = sales_window_avg(values, window=window, warmup_min=1)
        
        if len(expected_recent) >= 1:  # warmup_min=1 for this test
            # This should demonstrate the bug: dividing by window instead of len(recent)
            expected_buggy_mean = expected_total / window
            correct_mean = expected_total / len(expected_recent)
            
            assert result == expected_buggy_mean
            # Verify the bug exists by showing it's different from correct calculation when window != len(recent)
            if window != len(expected_recent):
                assert result != correct_mean

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20),
           window=st.integers(min_value=1, max_value=50),
           warmup_min=st.integers(min_value=1, max_value=20))
    @example(values=[1.0, 2.0], window=3, warmup_min=3)
    @example(values=[1.0, 2.0, 3.0], window=2, warmup_min=2)
    def test_warmup_min_check(self, values, window, warmup_min):
        """
        Function property: warmup_min_check
        Precondition: window > 0 and values is not empty
        Formal: if len(recent) < warmup_min then return None, otherwise return mean
        """
        expected_recent = values[-window:]
        
        result = sales_window_avg(values, window=window, warmup_min=warmup_min)
        
        if len(expected_recent) < warmup_min:
            assert result is None
        else:
            # Should return a numeric value (the buggy mean)
            assert result is not None
            assert isinstance(result, (int, float))

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=4, max_size=20),
           window=st.integers(min_value=1, max_value=10),
           warmup_min=st.integers(min_value=1, max_value=3))
    @example(values=[1.0, 2.0, 3.0, 4.0], window=2, warmup_min=2)
    @example(values=[10.0, 20.0, 30.0], window=1, warmup_min=1)
    def test_return_type_constraint(self, values, window, warmup_min):
        """
        Function property: return_type_constraint
        Precondition: window > 0 and values is not empty and len(recent) >= warmup_min
        Formal: return value is a numeric type (float/int) representing the average
        """
        assume(len(values[-window:]) >= warmup_min)
        
        result = sales_window_avg(values, window=window, warmup_min=warmup_min)
        
        assert result is not None
        assert isinstance(result, (int, float))
        # Should be a reasonable numeric value (not NaN or infinity)
        assert not np.isnan(result)
        assert np.isfinite(result)

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5),
           window=st.integers(min_value=1, max_value=50),
           warmup_min=st.integers(min_value=6, max_value=20))
    @example(values=[1.0], window=10, warmup_min=5)
    @example(values=[1.0, 2.0], window=15, warmup_min=8)
    def test_return_none_constraint(self, values, window, warmup_min):
        """
        Function property: return_none_constraint
        Precondition: window > 0 and values is not empty and len(recent) < warmup_min
        Formal: return value is None when insufficient data for warmup period
        """
        assume(len(values[-window:]) < warmup_min)
        
        result = sales_window_avg(values, window=window, warmup_min=warmup_min)
        
        assert result is None

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False)),
           window=st.integers())
    @example(values=[], window=0)
    @example(values=[], window=-1)
    @example(values=[1.0], window=0)
    def test_error_handling(self, values, window):
        """
        Function property: error_handling
        Precondition: None
        Formal: function raises ValueError for invalid window (<= 0) or empty values
        """
        if window <= 0 or not values:
            with pytest.raises(ValueError):
                sales_window_avg(values, window=window)
        else:
            # Should not raise ValueError for valid inputs
            try:
                result = sales_window_avg(values, window=window)
                # If we get here, no ValueError was raised
                assert True
            except ValueError:
                # This should not happen for valid inputs
                pytest.fail("Unexpected ValueError for valid inputs")

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
           window=st.integers(min_value=11, max_value=100))
    @example(values=[1.0, 2.0], window=50)
    @example(values=[5.0], window=100)
    def test_slice_bounds_safety(self, values, window):
        """
        Function property: slice_bounds_safety
        Precondition: window > 0 and values is not empty
        Formal: values[-window:] is safe even when len(values) < window (returns all available elements)
        """
        # This test verifies that the slice operation doesn't crash
        # and returns all available elements when window > len(values)
        try:
            result = sales_window_avg(values, window=window, warmup_min=1)
            # If we get here, the slice was safe
            assert True
        except Exception as e:
            # Should not raise any exception for valid inputs
            pytest.fail(f"Unexpected exception for valid inputs: {e}")

    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20),
           window=st.integers(min_value=2, max_value=50))
    @example(values=[1.0, 2.0], window=5)
    @example(values=[1.0, 2.0, 3.0], window=10)
    def test_buggy_division_behavior(self, values, window):
        """
        Function property: buggy_division_behavior
        Precondition: window > 0 and values is not empty
        Formal: mean calculation uses total / window instead of total / len(recent), causing incorrect averages during warmup period
        """
        expected_recent = values[-window:]
        expected_total = sum(expected_recent)
        
        result = sales_window_avg(values, window=window, warmup_min=1)
        
        if len(expected_recent) >= 1:  # warmup_min=1 for this test
            # Verify the buggy behavior: divides by window instead of len(recent)
            expected_buggy_mean = expected_total / window
            correct_mean = expected_total / len(expected_recent)
            
            assert result == expected_buggy_mean
            
            # When window != len(recent), this demonstrates the bug
            if window != len(expected_recent):
                assert result != correct_mean
                # The buggy result should be smaller when window > len(recent)
                if window > len(expected_recent):
                    assert result < correct_mean
                else:
                    assert result > correct_mean


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])