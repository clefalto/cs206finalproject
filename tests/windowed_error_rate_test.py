"""
Hypothesis tests for the windowed_error_rate function semantic properties.

This test file exercises all semantic properties identified in 
properties/windowed_error_rate_properties.json using the Hypothesis 
testing framework for property-based testing.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple


# Mock the windowed_error_rate function since it's not provided
# This is a placeholder implementation based on the properties
def windowed_error_rate(events: List[Tuple[int, bool]], now: int) -> float:
    """
    Mock implementation of windowed_error_rate function.
    
    Args:
        events: List of (timestamp, is_error) tuples
        now: Current timestamp
    
    Returns:
        Error rate in the window
    """
    # Window size is typically a constant, let's assume 60 seconds for this test
    WINDOW = 60
    
    # Filter events within the window
    recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
    
    if not recent:
        return 0.0
    
    # Count errors in recent events
    errors = sum(1 for _, is_err in recent if is_err)
    
    # Bug: This should be len(recent), not WINDOW
    # This matches the "error_rate_calculation_with_bug" property
    return errors / WINDOW


class TestWindowedErrorRateProperties:
    """Test class for windowed_error_rate semantic properties."""
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_zero_error_rate_on_empty_window(self, events, now):
        """
        Property: zero_error_rate_on_empty_window
        Condition: not recent (no events in window)
        Formal: windowed_error_rate(events, now) == 0.0
        """
        # Filter events to only those within a 60-second window
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Only test when the window is actually empty
        assume(not recent)
        
        result = windowed_error_rate(events, now)
        assert result == 0.0, f"Expected 0.0 for empty window, got {result}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            ),
            min_size=1
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_error_rate_calculation_with_bug(self, events, now):
        """
        Property: error_rate_calculation_with_bug
        Condition: not (not recent) - i.e., recent is not empty
        Formal: windowed_error_rate(events, now) == errors / window
        """
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Only test when we have events in the window
        assume(recent)
        
        errors = sum(1 for _, is_err in recent if is_err)
        expected = errors / WINDOW
        
        result = windowed_error_rate(events, now)
        assert result == expected, f"Expected {expected}, got {result}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_non_negative_error_rate(self, events, now):
        """
        Property: non_negative_error_rate
        Precondition: true
        Formal: windowed_error_rate(events, now) >= 0.0
        """
        result = windowed_error_rate(events, now)
        assert result >= 0.0, f"Error rate should be non-negative, got {result}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_bounded_error_rate(self, events, now):
        """
        Property: bounded_error_rate
        Precondition: true
        Formal: windowed_error_rate(events, now) <= 1.0
        """
        result = windowed_error_rate(events, now)
        assert result <= 1.0, f"Error rate should be <= 1.0, got {result}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_zero_error_rate_when_no_errors(self, events, now):
        """
        Property: zero_error_rate_when_no_errors
        Precondition: all(not is_err for _, is_err in recent)
        Formal: windowed_error_rate(events, now) == 0.0
        """
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Only test when there are no errors in recent events
        assume(recent and all(not is_err for _, is_err in recent))
        
        result = windowed_error_rate(events, now)
        assert result == 0.0, f"Expected 0.0 when no errors, got {result}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_maximum_error_rate_when_all_errors(self, events, now):
        """
        Property: maximum_error_rate_when_all_errors
        Precondition: all(is_err for _, is_err in recent)
        Formal: windowed_error_rate(events, now) == 1.0
        """
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Only test when all recent events are errors
        assume(recent and all(is_err for _, is_err in recent))
        
        result = windowed_error_rate(events, now)
        assert result == 1.0, f"Expected 1.0 when all errors, got {result}"
    
    @given(
        events1=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        events2=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=500, deadline=None)
    def test_error_rate_monotonicity(self, events1, events2, now):
        """
        Property: error_rate_monotonicity
        Precondition: recent1 is subset of recent2 and all errors in recent1 are also in recent2
        Formal: windowed_error_rate(events1, now) <= windowed_error_rate(events2, now)
        """
        WINDOW = 60
        recent1 = [(ts, is_err) for ts, is_err in events1 if now - ts <= WINDOW]
        recent2 = [(ts, is_err) for ts, is_err in events2 if now - ts <= WINDOW]
        
        # Check if recent1 is a subset of recent2
        recent1_set = set(recent1)
        recent2_set = set(recent2)
        
        # Check if all errors in recent1 are also in recent2
        errors1 = {item for item in recent1 if item[1]}  # items where is_err is True
        errors2 = {item for item in recent2 if item[1]}
        
        assume(recent1_set.issubset(recent2_set) and errors1.issubset(errors2))
        
        result1 = windowed_error_rate(events1, now)
        result2 = windowed_error_rate(events2, now)
        
        assert result1 <= result2, f"Error rate should be monotonic: {result1} <= {result2}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            ),
            min_size=1
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=1000, deadline=None)
    def test_error_rate_invariant(self, events, now):
        """
        Property: error_rate_invariant
        Precondition: recent is not empty
        Formal: windowed_error_rate(events, now) == sum(1 for _, is_err in recent if is_err) / window
        """
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Only test when recent is not empty
        assume(recent)
        
        errors = sum(1 for _, is_err in recent if is_err)
        expected = errors / WINDOW
        
        result = windowed_error_rate(events, now)
        assert result == expected, f"Expected {expected}, got {result}"


class TestWindowedErrorRateEdgeCases:
    """Additional edge case tests for windowed_error_rate."""
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=500, deadline=None)
    def test_consistency_with_different_event_orders(self, events, now):
        """Test that error rate is consistent regardless of event order."""
        # Test with original order
        result1 = windowed_error_rate(events, now)
        
        # Test with reversed order
        result2 = windowed_error_rate(list(reversed(events)), now)
        
        assert result1 == result2, f"Results should be consistent: {result1} == {result2}"
    
    @given(
        events=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            )
        ),
        now=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=500, deadline=None)
    def test_window_boundary_conditions(self, events, now):
        """Test behavior at window boundaries."""
        WINDOW = 60
        
        # Filter events within and exactly at window boundary
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        
        # Calculate expected result manually
        errors = sum(1 for _, is_err in recent if is_err)
        expected = errors / WINDOW if recent else 0.0
        
        result = windowed_error_rate(events, now)
        assert result == expected, f"Boundary condition failed: expected {expected}, got {result}"
    
    @given(
        events=st.lists(st.tuples(st.integers(min_value=0, max_value=1000), st.booleans())), 
        now=st.integers(min_value=0, max_value=1000)
    )
    @example(events=[], now=0)  # Empty events
    @example(events=[(0, False)], now=60)  # Single non-error event at boundary
    @example(events=[(0, True)], now=60)   # Single error event at boundary
    @example(events=[(0, True), (1, True)], now=60)  # Multiple error events
    @settings(max_examples=200, deadline=None)
    def test_specific_examples(self, events, now):
        """Test specific known examples."""
        result = windowed_error_rate(events, now)
        
        # Basic sanity checks
        assert 0.0 <= result <= 1.0, f"Result should be in [0,1]: {result}"
        
        # If no events in window, result should be 0
        WINDOW = 60
        recent = [(ts, is_err) for ts, is_err in events if now - ts <= WINDOW]
        if not recent:
            assert result == 0.0, f"Empty window should give 0.0, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])