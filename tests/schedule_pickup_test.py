"""
Hypothesis-based tests for schedule_pickup function semantic properties.

This test file exercises all semantic properties identified in 
properties/schedule_pickup_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers


def schedule_pickup(a, b, timeline):
    """
    Schedule a pickup window [a, b) into an existing timeline.
    
    Args:
        a: Start time of pickup window
        b: End time of pickup window  
        timeline: List of (start, end) tuples representing existing bookings
        
    Returns:
        tuple: (success: bool, updated_timeline: list)
    """
    # Check for empty window
    if a >= b:
        raise ValueError("empty window")
    
    # Check for conflicts
    if any(not (b <= s or a >= e) for s, e in timeline):
        return False, timeline
    
    # Insert the new window and sort by start time
    new_timeline = timeline + [(a, b)]
    new_timeline.sort(key=lambda x: x[0])
    
    return True, new_timeline


class TestSchedulePickupProperties:
    """Test class for schedule_pickup semantic properties."""
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_empty_window_error(self, a, b, timeline):
        """Test that empty window (a >= b) raises ValueError."""
        assume(a >= b)  # Precondition for this property
        
        with pytest.raises(ValueError, match="empty window"):
            schedule_pickup(a, b, timeline)
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_conflict_detection(self, a, b, timeline):
        """Test that conflicts are detected and original timeline is returned."""
        assume(a < b)  # Ensure valid window
        
        # Check if there's actually a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        assume(has_conflict)  # Precondition for this property
        
        success, result_timeline = schedule_pickup(a, b, timeline)
        
        # Should return False and original timeline unchanged
        assert success is False
        assert result_timeline == timeline
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_non_empty_window(self, a, b, timeline):
        """Test that valid window (a < b) doesn't raise empty window error."""
        assume(a < b)  # Precondition for this property
        
        # Should not raise ValueError for empty window
        try:
            success, result_timeline = schedule_pickup(a, b, timeline)
            # If successful, window should be in result
            if success:
                assert (a, b) in result_timeline
        except ValueError as e:
            # Should not be empty window error
            assert "empty window" not in str(e)
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_conflict_free_insertion(self, a, b, timeline):
        """Test that conflict-free window is inserted into timeline."""
        assume(a < b)  # Valid window precondition
        
        # Ensure no overlap between window and timeline
        no_overlap = all(b <= s or a >= e for s, e in timeline)
        assume(no_overlap)  # Precondition for this property
        
        success, result_timeline = schedule_pickup(a, b, timeline)
        
        # Should succeed and contain all original entries plus new window
        assert success is True
        assert len(result_timeline) == len(timeline) + 1
        assert (a, b) in result_timeline
        for entry in timeline:
            assert entry in result_timeline
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_sorted_output(self, a, b, timeline):
        """Test that result timeline is sorted by start time."""
        assume(a < b)  # Valid window precondition
        
        # Check if there's a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        
        success, result_timeline = schedule_pickup(a, b, timeline)
        
        # Result should always be sorted by start time
        sorted_timeline = sorted(result_timeline, key=lambda x: x[0])
        assert result_timeline == sorted_timeline
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_timeline_preservation(self, a, b, timeline):
        """Test that original timeline is preserved when conflict is detected."""
        assume(a < b)  # Valid window precondition
        
        # Ensure there's a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        assume(has_conflict)  # Precondition for this property
        
        original_timeline = timeline.copy()
        success, result_timeline = schedule_pickup(a, b, timeline)
        
        # Should return False and original timeline unchanged
        assert success is False
        assert result_timeline == original_timeline
        assert timeline == original_timeline  # Original should be unchanged
    
    @given(
        a=st.integers(min_value=0, max_value=1000),
        b=st.integers(min_value=0, max_value=1000),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=1000),
                st.integers(min_value=0, max_value=1000)
            ),
            max_size=10
        )
    )
    def test_boolean_return(self, a, b, timeline):
        """Test that function returns tuple (bool, list) where bool indicates success."""
        assume(a < b)  # Valid input precondition
        
        result = schedule_pickup(a, b, timeline)
        
        # Should return a tuple
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        success, updated_timeline = result
        
        # First element should be boolean indicating success
        assert isinstance(success, bool)
        
        # Second element should be list
        assert isinstance(updated_timeline, list)
        
        # Each timeline entry should be a tuple of two integers
        for entry in updated_timeline:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert all(isinstance(x, int) for x in entry)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])