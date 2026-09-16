import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples
import math


def machine_booking(window, timeline):
    """
    Book a machine for a time window, checking for conflicts with existing bookings.
    
    Args:
        window: Tuple of (start, end) times
        timeline: List of existing (start, end) time intervals
    
    Returns:
        Tuple of (success: bool, result: list) where result is either the updated timeline
        or the original timeline if booking failed
    
    Raises:
        ValueError: If window is empty (start >= end)
    """
    a, b = window
    
    # Check for empty window
    if a >= b:
        raise ValueError("empty window")
    
    # Check for conflicts with existing timeline
    if any(not (b <= s or a >= e) for s, e in timeline):
        # Conflict detected, return original timeline
        return False, timeline
    
    # No conflicts, add the new window and return sorted timeline
    result = sorted(timeline + [window])
    return True, result


class TestMachineBooking:
    """Test suite for machine_booking function using Hypothesis."""

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_empty_window_validation(self, window, timeline):
        """Test that empty windows (a >= b) raise ValueError."""
        a, b = window
        assume(a >= b)
        
        with pytest.raises(ValueError, match="empty window"):
            machine_booking(window, timeline)

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_conflict_detection(self, window, timeline):
        """Test that overlapping windows are detected and booking fails."""
        a, b = window
        assume(a < b)  # Valid window
        
        # Create a timeline with at least one overlapping interval
        assume(len(timeline) > 0)
        
        # Check if there's any overlap
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        assume(has_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should return False and original timeline unchanged
        assert success is False
        assert result == timeline

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_successful_booking(self, window, timeline):
        """Test that non-overlapping windows are successfully booked."""
        a, b = window
        assume(a < b)  # Valid window
        
        # Check that there's no overlap
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        assume(no_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should return True and timeline with new window added
        assert success is True
        assert result == sorted(timeline + [window])

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_timeline_sorted_property(self, window, timeline):
        """Test that the result timeline is always sorted."""
        a, b = window
        assume(a < b)  # Valid window
        
        success, result = machine_booking(window, timeline)
        
        # Result should always be sorted regardless of success
        assert result == sorted(result)

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_conflict_free_booking(self, window, timeline):
        """Test that non-overlapping windows result in successful booking."""
        a, b = window
        assume(a < b)  # Valid window
        
        # Check that there's no overlap
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        assume(no_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should be successful and timeline should be extended
        assert success is True
        assert result == sorted(timeline + [window])

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_timeline_unchanged_on_conflict(self, window, timeline):
        """Test that timeline is unchanged when booking fails due to conflict."""
        a, b = window
        assume(a < b)  # Valid window
        assume(len(timeline) > 0)
        
        # Check if there's any overlap
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        assume(has_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should return False and original timeline unchanged
        assert success is False
        assert result == timeline

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_timeline_extended_on_success(self, window, timeline):
        """Test that timeline length increases by 1 on successful booking."""
        a, b = window
        assume(a < b)  # Valid window
        
        # Check that there's no overlap
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        assume(no_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should be successful and timeline should have one more element
        assert success is True
        assert len(result) == len(timeline) + 1

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_timeline_preserved_on_conflict(self, window, timeline):
        """Test that original timeline is preserved when booking fails."""
        a, b = window
        assume(a < b)  # Valid window
        assume(len(timeline) > 0)
        
        # Check if there's any overlap
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        assume(has_overlap)
        
        success, result = machine_booking(window, timeline)
        
        # Should return False and original timeline should be preserved
        assert success is False
        assert result == timeline

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    def test_no_overlap_condition(self, window, timeline):
        """Test the specific overlap detection logic."""
        a, b = window
        assume(a < b)  # Valid window
        
        success, result = machine_booking(window, timeline)
        
        # Check that our overlap detection logic matches the function's behavior
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_overlap:
            assert success is False
            assert result == timeline
        else:
            assert success is True
            assert result == sorted(timeline + [window])

    @given(
        window=tuples(integers(), integers()),
        timeline=lists(tuples(integers(), integers()))
    )
    @pytest.mark.parametrize("damping", [0.0, 0.5, 1.0])
    def test_edge_cases(self, window, timeline, damping):
        """Test various edge cases and boundary conditions."""
        a, b = window
        
        # Test empty timeline
        if len(timeline) == 0:
            assume(a < b)  # Valid window
            success, result = machine_booking(window, timeline)
            assert success is True
            assert result == [window]
        
        # Test single interval timeline
        elif len(timeline) == 1:
            s, e = timeline[0]
            assume(a < b)  # Valid window
            
            # Test non-overlapping case
            if b <= s or a >= e:
                success, result = machine_booking(window, timeline)
                assert success is True
                assert result == sorted(timeline + [window])
            # Test overlapping case
            else:
                success, result = machine_booking(window, timeline)
                assert success is False
                assert result == timeline
        
        # Test that function handles negative times
        assume(a < b)  # Valid window
        success, result = machine_booking(window, timeline)
        
        # Verify result properties
        assert isinstance(success, bool)
        assert isinstance(result, list)
        assert all(isinstance(interval, tuple) and len(interval) == 2 for interval in result)
        assert all(isinstance(start, int) and isinstance(end, int) for start, end in result)
        assert result == sorted(result)  # Should always be sorted