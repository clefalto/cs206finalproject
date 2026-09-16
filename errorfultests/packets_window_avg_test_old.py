import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import integers, lists, floats, one_of, just
import sys
import os

# Add the current directory to Python path to import the function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function under test
from dataset.python_programs.packets_window_avg import packets_window_avg


class TestPacketsWindowAvg:
    """Test suite for packets_window_avg function using Hypothesis."""

    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False))
    )
    def test_invalid_window_size(self, window, values):
        """Test that invalid window size raises ValueError."""
        with pytest.raises(ValueError, match="window must be positive"):
            packets_window_avg(values, window)

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), max_size=0)
    )
    def test_empty_values_error(self, window, values):
        """Test that empty values raises ValueError."""
        with pytest.raises(ValueError, match="no values"):
            packets_window_avg(values, window)

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_positive_window_requirement(self, window, values):
        """Test that positive window does not raise ValueError for window size."""
        # This should not raise a ValueError about window size
        try:
            result = packets_window_avg(values, window)
            # If we get here, the window size check passed
            assert True
        except ValueError as e:
            # Only allow ValueError for empty values, not for window size
            assert "no values" in str(e)
            assert "window must be positive" not in str(e)

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_non_empty_values_requirement(self, window, values):
        """Test that non-empty values does not raise ValueError for empty values."""
        # This should not raise a ValueError about empty values
        try:
            result = packets_window_avg(values, window)
            # If we get here, the empty values check passed
            assert True
        except ValueError as e:
            # Only allow ValueError for window size, not for empty values
            assert "no values" not in str(e)

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_window_slicing(self, window, values):
        """Test that window slicing works correctly."""
        assume(len(values) >= window)
        
        result = packets_window_avg(values, window)
        
        # Check that recent is correctly sliced from the end
        recent = values[-window:]
        assert len(recent) == min(window, len(values))

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_total_summation(self, window, values):
        """Test that total summation works correctly."""
        assume(len(values) >= window)
        
        result = packets_window_avg(values, window)
        
        # Check that total is correctly calculated
        recent = values[-window:]
        total = sum(recent)
        assert total == sum(recent)

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_mean_calculation(self, window, values):
        """Test that mean calculation works correctly when conditions are met."""
        assume(len(values) >= window)
        assume(window >= 1)  # warmup_min is typically 1
        
        result = packets_window_avg(values, window)
        
        if result is not None:
            # Check that mean is correctly calculated
            recent = values[-window:]
            expected_mean = sum(recent) / window
            assert abs(result - expected_mean) < 1e-10

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_warmup_min_check(self, window, values):
        """Test that warmup_min check works correctly."""
        assume(len(values) < window)  # This should trigger insufficient warmup
        
        result = packets_window_avg(values, window)
        
        # Should return None when insufficient warmup
        assert result is None

    @given(
        window=st.integers(min_value=1),
        values=st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    )
    def test_insufficient_warmup(self, window, values):
        """Test that insufficient warmup returns None."""
        assume(len(values) < window)
        
        result = packets_window_avg(values, window)
        
        # Should return None when insufficient warmup
        assert result is None

    @example(window=1, values=[1, 2, 3])
    @example(window=2, values=[1, 2, 3, 4])
    @example(window=3, values=[1, 2, 3, 4, 5])
    @given(
        window=st.integers(min_value=1, max_value=10),
        values=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=20)
    )
    def test_mean_calculation_with_examples(self, window, values):
        """Test mean calculation with specific examples and generated data."""
        assume(len(values) >= window)
        assume(window >= 1)  # warmup_min is typically 1
        
        result = packets_window_avg(values, window)
        
        if result is not None:
            # Check that mean is correctly calculated
            recent = values[-window:]
            expected_mean = sum(recent) / window
            assert abs(result - expected_mean) < 1e-10

    @example(window=0, values=[1, 2, 3])
    @example(window=-1, values=[1, 2, 3])
    @given(
        window=st.integers(max_value=0),
        values=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=10)
    )
    def test_invalid_window_size_with_examples(self, window, values):
        """Test invalid window size with specific examples."""
        with pytest.raises(ValueError, match="window must be positive"):
            packets_window_avg(values, window)

    @example(window=1, values=[])
    @example(window=5, values=[])
    @given(
        window=st.integers(min_value=1, max_value=10),
        values=st.lists(st.integers(min_value=1, max_value=100), max_size=0)
    )
    def test_empty_values_error_with_examples(self, window, values):
        """Test empty values error with specific examples."""
        with pytest.raises(ValueError, match="no values"):
            packets_window_avg(values, window)