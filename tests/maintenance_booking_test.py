import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers


def maintenance_booking(a, b, timeline):
    """
    Book a maintenance window in a timeline.
    
    Args:
        a: start time of maintenance window
        b: end time of maintenance window  
        timeline: list of (start, end) tuples representing existing bookings
    
    Returns:
        tuple: (success: bool, updated_timeline: list)
    """
    # Check for empty window
    if a >= b:
        raise ValueError("empty window")
    
    # Check for conflicts
    if any(not (b <= s or a >= e) for s, e in timeline):
        return False, timeline
    
    # Insert the new window and sort
    timeline.append((a, b))
    timeline.sort()
    return True, timeline


class TestMaintenanceBooking:
    """Test suite for maintenance_booking function using Hypothesis."""

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_empty_window_error(self, a, b, timeline):
        """Test that empty window (a >= b) raises ValueError."""
        assume(a >= b)
        
        with pytest.raises(ValueError, match="empty window"):
            maintenance_booking(a, b, timeline)

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_conflict_detection(self, a, b, timeline):
        """Test that conflicts are detected and original timeline is returned."""
        assume(a < b)  # Valid window
        
        # Check if there's a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_conflict:
            success, result_timeline = maintenance_booking(a, b, timeline)
            assert success is False
            assert result_timeline == timeline

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_window_validity(self, a, b, timeline):
        """Test that valid windows (a < b) are processed correctly."""
        assume(a < b)
        
        # Should not raise ValueError for valid windows
        try:
            success, result_timeline = maintenance_booking(a, b, timeline)
            # If successful, window should be included
            if success:
                assert (a, b) in result_timeline
        except ValueError:
            pytest.fail("Valid window should not raise ValueError")

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_timeline_sorted(self, a, b, timeline):
        """Test that result timeline is sorted by start time."""
        assume(a < b)
        
        try:
            success, result_timeline = maintenance_booking(a, b, timeline)
            # Check that timeline is sorted by start time
            for i in range(len(result_timeline) - 1):
                assert result_timeline[i][0] <= result_timeline[i + 1][0]
        except ValueError:
            # Empty window case, skip sorting check
            pass

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_window_inclusion(self, a, b, timeline):
        """Test that the window is included in the result when no conflicts."""
        assume(a < b)
        
        # Check if there are no conflicts
        no_conflicts = all(b <= s or a >= e for s, e in timeline)
        
        if no_conflicts:
            success, result_timeline = maintenance_booking(a, b, timeline)
            assert success is True
            assert (a, b) in result_timeline

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_conflict_preservation(self, a, b, timeline):
        """Test that original timeline is preserved when conflicts are detected."""
        assume(a < b)
        
        # Make a copy to compare
        original_timeline = timeline.copy()
        
        # Check if there's a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_conflict:
            success, result_timeline = maintenance_booking(a, b, timeline)
            assert success is False
            assert result_timeline == original_timeline

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_non_conflict_insertion(self, a, b, timeline):
        """Test that window is inserted when no conflicts are detected."""
        assume(a < b)
        
        # Check if there are no conflicts
        no_conflicts = all(b <= s or a >= e for s, e in timeline)
        
        if no_conflicts:
            success, result_timeline = maintenance_booking(a, b, timeline)
            assert success is True
            assert len(result_timeline) == len(timeline) + 1
            assert (a, b) in result_timeline

    @given(
        a=st.integers(),
        b=st.integers(),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_timeline_structure(self, a, b, timeline):
        """Test that result contains list of (start, end) tuples."""
        assume(a < b)
        
        try:
            success, result_timeline = maintenance_booking(a, b, timeline)
            
            # Check that result is a list
            assert isinstance(result_timeline, list)
            
            # Check that each element is a tuple of two integers
            for item in result_timeline:
                assert isinstance(item, tuple)
                assert len(item) == 2
                assert isinstance(item[0], int)
                assert isinstance(item[1], int)
                
        except ValueError:
            # Empty window case, skip structure check
            pass

    @given(
        a=st.integers(min_value=0, max_value=100),
        b=st.integers(min_value=0, max_value=100),
        timeline=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=100),
                st.integers(min_value=0, max_value=100)
            ),
            max_size=10
        )
    )
    def test_comprehensive_property_coverage(self, a, b, timeline):
        """Comprehensive test covering all properties with bounded integers."""
        # Filter out invalid intervals in timeline
        valid_timeline = [(s, e) for s, e in timeline if s < e]
        
        try:
            success, result_timeline = maintenance_booking(a, b, valid_timeline)
            
            # Property: timeline_structure
            assert isinstance(result_timeline, list)
            for item in result_timeline:
                assert isinstance(item, tuple) and len(item) == 2
            
            # Property: timeline_sorted
            for i in range(len(result_timeline) - 1):
                assert result_timeline[i][0] <= result_timeline[i + 1][0]
            
            if success:
                # Property: window_inclusion
                assert (a, b) in result_timeline
            else:
                # Property: conflict_preservation
                assert result_timeline == valid_timeline
                
        except ValueError as e:
            # Property: empty_window_error
            assert str(e) == "empty window"
            assert a >= b