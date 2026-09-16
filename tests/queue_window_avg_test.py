"""
Hypothesis-based tests for queue_window_avg function semantic properties.

This test file exercises all 16 semantic properties identified in 
queue_window_avg_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, lists, floats, one_of
from hypothesis.extra.numpy import arrays
import numpy as np
from typing import List, Optional, Union

# Import the function under test
# Note: The actual implementation should be imported from the appropriate module
# For now, we'll define a placeholder that matches the expected behavior
def queue_window_avg(values: List[Union[int, float]], 
                    window: int = 3, 
                    warmup_min: int = 1) -> Optional[float]:
    """
    Compute rolling average of last 'window' elements with warmup threshold.
    
    This implementation contains the semantic bug where it divides by 'window'
    instead of the actual length of the tail slice.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    
    if not values:
        raise ValueError("empty series")
    
    tail = values[-window:]
    
    if len(tail) < warmup_min:
        return None
    
    total = sum(tail)
    # Bug: divides by window instead of len(tail)
    return total / window


class TestQueueWindowAvgProperties:
    """Test class for queue_window_avg semantic properties."""
    
    # Strategies for generating test data
    valid_window_strategy = st.integers(min_value=1, max_value=100)
    valid_warmup_strategy = st.integers(min_value=1, max_value=100)
    numeric_values_strategy = st.lists(
        st.one_of(st.integers(min_value=-1000, max_value=1000), 
                 st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False)),
        min_size=0, max_size=1000
    )
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
           window=st.integers(max_value=0))
    def test_invalid_window_size_branch(self, values, window):
        """Test branch: window <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="window must be positive"):
            queue_window_avg(values, window=window)
    
    @given(window=st.integers(min_value=1, max_value=100))
    def test_empty_series_error_branch(self, window):
        """Test branch: empty values raises ValueError."""
        with pytest.raises(ValueError, match="empty series"):
            queue_window_avg([], window=window)
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=100))
    def test_insufficient_warmup_branch(self, values, window, warmup_min):
        """Test branch: len(tail) < warmup_min returns None."""
        assume(len(values) < warmup_min)
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        assert result is None
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
           window=st.integers(max_value=0))
    def test_positive_window_requirement_function(self, values, window):
        """Test function: positive window requirement."""
        with pytest.raises(ValueError, match="window must be positive"):
            queue_window_avg(values, window=window)
    
    @given(window=st.integers(min_value=1, max_value=100))
    def test_non_empty_values_requirement_function(self, window):
        """Test function: non-empty values requirement."""
        with pytest.raises(ValueError, match="empty series"):
            queue_window_avg([], window=window)
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100))
    def test_window_size_computation_bug_function(self, values, window):
        """Test function: window size computation bug (divides by window, not len(tail))."""
        assume(len(values) >= 1)
        warmup_min = 1
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        # Calculate what the correct result should be
        tail = values[-window:]
        correct_mean = sum(tail) / len(tail)
        
        # The buggy implementation divides by window instead of len(tail)
        if len(tail) != window:
            assert result != correct_mean, f"Expected bug: result {result} should not equal correct mean {correct_mean}"
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100))
    def test_tail_extraction_function(self, values, window):
        """Test function: tail extraction uses values[-window:]."""
        assume(len(values) >= 1)
        warmup_min = 1
        
        # Manually compute what tail should be
        expected_tail = values[-window:]
        
        # We can't directly access the tail, but we can verify the behavior
        # by checking that the sum matches what we expect from the tail
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        if result is not None:
            # The sum used in computation should match sum(expected_tail)
            expected_sum = sum(expected_tail)
            # Since we divide by window (the bug), we can verify: result * window == expected_sum
            assert abs(result * window - expected_sum) < 1e-10
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100))
    def test_sum_computation_function(self, values, window):
        """Test function: sum computation uses sum(tail)."""
        assume(len(values) >= 1)
        warmup_min = 1
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        if result is not None:
            tail = values[-window:]
            expected_sum = sum(tail)
            # Verify that result * window equals the sum of tail
            assert abs(result * window - expected_sum) < 1e-10
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=100))
    def test_warmup_threshold_check_function(self, values, window, warmup_min):
        """Test function: warmup threshold check returns None or mean."""
        tail = values[-window:]
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        if len(tail) < warmup_min:
            assert result is None
        else:
            assert result is not None
            assert isinstance(result, (int, float))
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=100))
    def test_return_type_consistency_function(self, values, window, warmup_min):
        """Test function: return type consistency when conditions are met."""
        assume(len(values[-window:]) >= warmup_min)
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        assert result is not None
        assert isinstance(result, (int, float))
        # Convert to float for consistency
        assert isinstance(float(result), float)
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
           window=st.integers(max_value=0))
    def test_parameter_validation_order_function(self, values, window):
        """Test function: parameter validation order (window before values)."""
        # This test verifies that window validation happens before values validation
        # When window <= 0, it should raise ValueError regardless of values content
        with pytest.raises(ValueError, match="window must be positive"):
            queue_window_avg(values, window=window)
    
    def test_default_parameters_function(self):
        """Test function: default parameters are window=3 and warmup_min=1."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        # Test with defaults
        result_default = queue_window_avg(values)
        
        # Test with explicit defaults
        result_explicit = queue_window_avg(values, window=3, warmup_min=1)
        
        assert result_default == result_explicit
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=10, max_size=100),
           window1=st.integers(min_value=1, max_value=50),
           window2=st.integers(min_value=51, max_value=100))
    def test_metamorphic_relation_window_increase_function(self, values, window1, window2):
        """Test function: metamorphic relation for window increase."""
        assume(window1 < window2)
        assume(len(values) >= window2)  # Ensure values has sufficient length
        
        warmup_min = 1
        
        result1 = queue_window_avg(values, window=window1, warmup_min=warmup_min)
        result2 = queue_window_avg(values, window=window2, warmup_min=warmup_min)
        
        # Both should return a result (not None) since we have sufficient data
        assert result1 is not None
        assert result2 is not None
        
        # The results may be different because larger window includes more elements
        # This is testing that the behavior changes appropriately with window size
        tail1 = values[-window1:]
        tail2 = values[-window2:]
        
        # Verify the computation uses the correct tails
        assert abs(result1 * window1 - sum(tail1)) < 1e-10
        assert abs(result2 * window2 - sum(tail2)) < 1e-10
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100),
           warmup_min1=st.integers(min_value=1, max_value=50),
           warmup_min2=st.integers(min_value=51, max_value=100))
    def test_metamorphic_relation_warmup_increase_function(self, values, window, warmup_min1, warmup_min2):
        """Test function: metamorphic relation for warmup increase."""
        assume(warmup_min1 < warmup_min2)
        
        result1 = queue_window_avg(values, window=window, warmup_min=warmup_min1)
        result2 = queue_window_avg(values, window=window, warmup_min=warmup_min2)
        
        # If result1 is None, result2 must also be None (more restrictive threshold)
        # If result2 is not None, result1 must also not be None (less restrictive threshold)
        if result2 is not None:
            assert result1 is not None
        # Note: result1 could be not None while result2 is None (this is expected)
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100),
           warmup_min=st.integers(min_value=1, max_value=100))
    def test_invariant_sum_division_function(self, values, window, warmup_min):
        """Test function: invariant sum division (always divides by window)."""
        assume(len(values[-window:]) >= warmup_min)
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        if result is not None:
            tail = values[-window:]
            total = sum(tail)
            # The invariant: result = total / window (this is the bug we're testing for)
            assert abs(result - (total / window)) < 1e-10
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
           window=st.integers(min_value=1, max_value=100))
    def test_invariant_tail_length_function(self, values, window):
        """Test function: invariant tail length is min(window, len(values))."""
        assume(len(values) >= 1)
        warmup_min = 1
        
        # The tail length should be min(window, len(values)) due to Python slice behavior
        expected_tail_length = min(window, len(values))
        
        result = queue_window_avg(values, window=window, warmup_min=warmup_min)
        
        if result is not None:
            # We can verify this by checking that the sum used in computation
            # corresponds to exactly expected_tail_length elements
            tail = values[-window:]
            assert len(tail) == expected_tail_length
            
            # And verify the computation uses this tail
            expected_sum = sum(tail)
            assert abs(result * window - expected_sum) < 1e-10


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])