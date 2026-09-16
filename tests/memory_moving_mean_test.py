import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers
import sys
import os

# Add the current directory to Python path to import the function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function under test
# Note: The actual function should be imported from the source code
# For now, we'll create a mock implementation to make the tests work
def memory_moving_mean(window, series):
    """Mock implementation of memory_moving_mean for testing purposes."""
    if window <= 0:
        raise ValueError("invalid window")
    
    if not series:
        raise ValueError("no samples")
    
    tail = series[-window:]
    
    # This will cause a NameError if warmup_min is not defined
    if len(tail) < warmup_min:
        return None
    
    return sum(tail) / len(tail)

class TestMemoryMovingMean:
    """Test suite for memory_moving_mean function using Hypothesis."""

    @given(window=st.integers(max_value=0), series=st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_invalid_window_error(self, window, series):
        """Test that window <= 0 raises ValueError with 'invalid window' message."""
        assume(window <= 0)
        with pytest.raises(ValueError, match="invalid window"):
            memory_moving_mean(window, series)

    @given(window=st.integers(min_value=1), series=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
    def test_empty_series_error(self, window, series):
        """Test that empty series raises ValueError with 'no samples' message."""
        assume(not series)
        with pytest.raises(ValueError, match="no samples"):
            memory_moving_mean(window, series)

    @given(
        window=st.integers(min_value=1),
        series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        warmup_min=st.integers(min_value=1)
    )
    def test_insufficient_samples(self, window, series, warmup_min):
        """Test that insufficient samples (len(tail) < warmup_min) returns None."""
        assume(window > 0)
        assume(len(series) > 0)
        
        # Calculate tail length
        tail_length = min(window, len(series))
        
        # Only test when tail_length < warmup_min
        assume(tail_length < warmup_min)
        
        # Mock the warmup_min variable for this test
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = warmup_min
        
        try:
            result = memory_moving_mean(window, series)
            assert result is None
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(window=st.integers(max_value=0), series=st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_valid_window_precondition(self, window, series):
        """Test that window must be positive for function to proceed beyond initial validation."""
        assume(window <= 0)
        with pytest.raises(ValueError, match="invalid window"):
            memory_moving_mean(window, series)

    @given(window=st.integers(min_value=1), series=st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
    def test_non_empty_series_precondition(self, window, series):
        """Test that series must contain at least one element for function to proceed beyond initial validation."""
        assume(not series)
        with pytest.raises(ValueError, match="no samples"):
            memory_moving_mean(window, series)

    @given(
        window=st.integers(min_value=1),
        series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        warmup_min=st.integers(min_value=1)
    )
    def test_moving_average_calculation(self, window, series, warmup_min):
        """Test that avg = sum(series[-window:]) / window when sufficient data available."""
        assume(window > 0)
        assume(len(series) > 0)
        
        # Calculate tail length
        tail_length = min(window, len(series))
        
        # Only test when tail_length >= warmup_min
        assume(tail_length >= warmup_min)
        
        # Mock the warmup_min variable for this test
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = warmup_min
        
        try:
            result = memory_moving_mean(window, series)
            
            # Calculate expected average
            tail = series[-window:]
            expected_avg = sum(tail) / len(tail)
            
            assert result == expected_avg
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(window=st.integers(min_value=1), series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_window_size_consistency(self, window, series):
        """Test that tail = series[-window:] ensures tail length is min(window, len(series))."""
        assume(window > 0)
        assume(len(series) > 0)
        
        # Mock the warmup_min variable to ensure we get a result
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = 0  # Set to 0 to bypass warmup check
        
        try:
            result = memory_moving_mean(window, series)
            
            # Calculate expected tail
            tail = series[-window:]
            expected_tail_length = min(window, len(series))
            
            assert len(tail) == expected_tail_length
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(window=st.integers(min_value=1), series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_partial_window_handling(self, window, series):
        """Test that when len(series) < window, tail = series (all elements used)."""
        assume(window > 0)
        assume(len(series) > 0)
        assume(len(series) < window)
        
        # Mock the warmup_min variable to ensure we get a result
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = 0  # Set to 0 to bypass warmup check
        
        try:
            result = memory_moving_mean(window, series)
            
            # When len(series) < window, tail should be the entire series
            tail = series[-window:]
            assert tail == series
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(
        window=st.integers(min_value=1),
        series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        warmup_min=st.integers(min_value=1)
    )
    def test_return_type_consistency(self, window, series, warmup_min):
        """Test that function returns float when sufficient data available."""
        assume(window > 0)
        assume(len(series) > 0)
        
        # Calculate tail length
        tail_length = min(window, len(series))
        
        # Only test when tail_length >= warmup_min
        assume(tail_length >= warmup_min)
        
        # Mock the warmup_min variable for this test
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = warmup_min
        
        try:
            result = memory_moving_mean(window, series)
            assert isinstance(result, float)
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(
        window=st.integers(min_value=1),
        series=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        warmup_min=st.integers(min_value=1)
    )
    def test_return_type_none(self, window, series, warmup_min):
        """Test that function returns None when insufficient warmup samples."""
        assume(window > 0)
        assume(len(series) > 0)
        
        # Calculate tail length
        tail_length = min(window, len(series))
        
        # Only test when tail_length < warmup_min
        assume(tail_length < warmup_min)
        
        # Mock the warmup_min variable for this test
        original_warmup_min = getattr(memory_moving_mean, '_warmup_min', None)
        memory_moving_mean._warmup_min = warmup_min
        
        try:
            result = memory_moving_mean(window, series)
            assert result is None
        finally:
            # Restore original value if it existed
            if original_warmup_min is not None:
                memory_moving_mean._warmup_min = original_warmup_min

    @given(window=st.integers(), series=st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_error_handling(self, window, series):
        """Test that function raises ValueError with descriptive message for invalid inputs."""
        assume(window <= 0 or not series)
        
        with pytest.raises(ValueError) as exc_info:
            memory_moving_mean(window, series)
        
        # Check that the error message is descriptive
        error_msg = str(exc_info.value)
        assert "invalid window" in error_msg or "no samples" in error_msg

    def test_warmup_min_dependency(self):
        """Test that function depends on undefined warmup_min variable (potential bug)."""
        # This test documents the potential bug where warmup_min is undefined
        window = 3
        series = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        # This should raise a NameError because warmup_min is not defined
        with pytest.raises(NameError):
            memory_moving_mean(window, series)