"""
Hypothesis-based property tests for the schedule_window function.

This test suite exercises all semantic properties identified in
properties/schedule_window_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers, floats


# Import the function under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dataset', 'python_programs'))

from schedule_window import schedule_window


class TestScheduleWindowProperties:
    """Test class for schedule_window semantic properties."""
    
    # Strategies for generating test data
    valid_interval = st.tuples(
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    ).map(lambda x: (min(x), max(x))).filter(lambda x: x[0] < x[1])
    
    invalid_interval = st.tuples(
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    ).filter(lambda x: x[0] >= x[1])
    
    sorted_non_overlapping_intervals = st.lists(
        valid_interval,
        min_size=0,
        max_size=50
    ).map(sorted).filter(
        lambda intervals: all(intervals[i][1] <= intervals[i+1][0] 
                              for i in range(len(intervals)-1))
    )
    
    @given(invalid_interval)
    def test_invalid_interval_detection(self, interval):
        """
        Property: invalid_interval_detection
        Formal: if start >= end then ValueError is raised
        """
        start, end = interval
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            schedule_window(interval, [])
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_overlap_detection(self, existing, interval):
        """
        Property: overlap_detection
        Formal: if intervals overlap then return False, existing
        """
        start, end = interval
        
        # Find an existing interval that overlaps with the new interval
        overlapping_exists = any(
            not (end <= s or start >= e) 
            for s, e in existing
        )
        
        if overlapping_exists:
            success, result = schedule_window(interval, existing)
            assert success is False
            # Property: non_destructive_on_failure
            assert result is existing  # Original list should be unchanged
    
    @given(invalid_interval)
    def test_interval_validation(self, interval):
        """
        Property: interval_validation
        Formal: if start >= end then ValueError('invalid interval')
        """
        start, end = interval
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            schedule_window(interval, [])
    
    @given(sorted_non_overlapping_intervals, valid_interval)
    def test_overlap_preservation(self, existing, interval):
        """
        Property: overlap_preservation
        Formal: if no overlap with existing then return True, updated where updated is sorted and contains all original intervals plus new interval
        """
        start, end = interval
        
        # Check that there's no overlap
        no_overlap = all(
            end <= s or start >= e 
            for s, e in existing
        )
        
        if no_overlap:
            success, updated = schedule_window(interval, existing)
            
            # Should return True for successful scheduling
            assert success is True
            
            # Updated should be sorted
            assert updated == sorted(updated)
            
            # Updated should contain all original intervals plus the new one
            assert len(updated) == len(existing) + 1
            assert interval in updated
            for orig_interval in existing:
                assert orig_interval in updated
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_sorted_output(self, existing, interval):
        """
        Property: sorted_output
        Formal: updated.sort() ensures result is sorted
        """
        # Sort the existing list to satisfy precondition
        existing_sorted = sorted(existing)
        
        success, updated = schedule_window(interval, existing_sorted)
        
        # The result should always be sorted
        assert updated == sorted(updated)
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_interval_addition(self, existing, interval):
        """
        Property: interval_addition
        Formal: updated = existing + [interval] adds new interval to list
        """
        start, end = interval
        
        # Check that there's no overlap (precondition)
        no_overlap = all(
            end <= s or start >= e 
            for s, e in existing
        )
        
        if no_overlap:
            success, updated = schedule_window(interval, existing)
            
            # Should be successful
            assert success is True
            
            # Updated should contain the new interval
            assert interval in updated
            
            # Length should be increased by 1
            assert len(updated) == len(existing) + 1
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_overlap_rejection(self, existing, interval):
        """
        Property: overlap_rejection
        Formal: if overlap detected then return False, existing (original list unchanged)
        """
        start, end = interval
        
        # Check for overlap
        overlap_detected = any(
            not (end <= s or start >= e) 
            for s, e in existing
        )
        
        if overlap_detected:
            success, result = schedule_window(interval, existing)
            
            # Should return False
            assert success is False
            
            # Original list should be unchanged (non-destructive)
            assert result is existing
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_touching_endpoint_overlap_bug(self, existing, interval):
        """
        Property: touching_endpoint_overlap_bug
        Formal: BUG: touching endpoints (end == s or start == e) are treated as overlap due to strict inequality
        """
        start, end = interval
        
        # Look for intervals that touch at endpoints
        touching_exists = any(
            end == s or start == e 
            for s, e in existing
        )
        
        if touching_exists:
            success, result = schedule_window(interval, existing)
            
            # Due to the bug, touching endpoints are treated as overlap
            # So we expect False to be returned
            assert success is False
            assert result is existing
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_non_destructive_on_failure(self, existing, interval):
        """
        Property: non_destructive_on_failure
        Formal: return False, existing preserves original list unchanged
        """
        start, end = interval
        
        # Check for overlap (precondition for failure)
        overlap_detected = any(
            not (end <= s or start >= e) 
            for s, e in existing
        )
        
        if overlap_detected:
            # Keep reference to original list
            original_id = id(existing)
            success, result = schedule_window(interval, existing)
            
            # Should return False
            assert success is False
            
            # Should return the exact same list object (non-destructive)
            assert result is existing
            assert id(result) == original_id
    
    @given(st.lists(valid_interval, max_size=20), valid_interval)
    def test_successful_scheduling(self, existing, interval):
        """
        Property: successful_scheduling
        Formal: return True, updated where updated contains all intervals sorted
        """
        start, end = interval
        
        # Check that there's no overlap (precondition)
        no_overlap = all(
            end <= s or start >= e 
            for s, e in existing
        )
        
        if no_overlap:
            success, updated = schedule_window(interval, existing)
            
            # Should be successful
            assert success is True
            
            # Updated should be sorted
            assert updated == sorted(updated)
            
            # Updated should contain all original intervals plus the new one
            assert len(updated) == len(existing) + 1
            assert interval in updated
            for orig_interval in existing:
                assert orig_interval in updated


class TestEdgeCases:
    """Additional edge case tests for schedule_window."""
    
    def test_empty_existing_list(self):
        """Test scheduling with empty existing list."""
        interval = (1.0, 2.0)
        success, updated = schedule_window(interval, [])
        
        assert success is True
        assert updated == [interval]
    
    def test_single_interval_no_overlap(self):
        """Test scheduling a single non-overlapping interval."""
        existing = [(1.0, 2.0)]
        interval = (3.0, 4.0)
        success, updated = schedule_window(interval, existing)
        
        assert success is True
        assert updated == [(1.0, 2.0), (3.0, 4.0)]
    
    def test_single_interval_overlap(self):
        """Test scheduling a single overlapping interval."""
        existing = [(1.0, 3.0)]
        interval = (2.0, 4.0)
        success, result = schedule_window(interval, existing)
        
        assert success is False
        assert result is existing
    
    def test_touching_intervals(self):
        """Test intervals that touch at endpoints."""
        existing = [(1.0, 2.0)]
        interval = (2.0, 3.0)  # Touching at endpoint
        success, result = schedule_window(interval, existing)
        
        # Due to the bug, touching endpoints are treated as overlap
        assert success is False
        assert result is existing
    
    def test_identical_intervals(self):
        """Test scheduling identical intervals."""
        existing = [(1.0, 2.0)]
        interval = (1.0, 2.0)  # Identical interval
        success, result = schedule_window(interval, existing)
        
        assert success is False
        assert result is existing
    
    def test_zero_length_interval(self):
        """Test scheduling zero-length interval."""
        interval = (2.0, 2.0)  # Zero length
        
        with pytest.raises(ValueError, match="invalid interval"):
            schedule_window(interval, [])
    
    def test_negative_intervals(self):
        """Test with negative time values."""
        existing = [(-5.0, -3.0)]
        interval = (-2.0, -1.0)
        success, updated = schedule_window(interval, existing)
        
        assert success is True
        assert updated == [(-5.0, -3.0), (-2.0, -1.0)]


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])