import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


def room_reservation(existing, interval):
    """
    Book a room reservation for a time interval, checking for conflicts with existing reservations.
    
    Args:
        existing: List of existing (start, end) time intervals
        interval: Tuple of (start, end) times
    
    Returns:
        Tuple of (success: bool, result: list) where result is either the updated list
        or the original list if booking failed
    
    Raises:
        ValueError: If interval is invalid (start >= end)
    """
    start, end = interval
    
    # Check for invalid interval
    if start >= end:
        raise ValueError("invalid interval")
    
    # Check for conflicts with existing reservations
    for s, e in existing:
        # BUG: touching endpoints treated as overlap.
        if not (end <= s or start >= e):
            return False, existing
    
    # No conflicts, add the new interval and return sorted list
    updated = existing + [interval]
    updated.sort()
    return True, updated


class TestRoomReservation:
    """Test suite for room_reservation function using Hypothesis."""

    # BRANCH PROPERTIES TESTS

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_invalid_interval_rejection_branch(self, existing, interval):
        """Test branch: start >= end -> ValueError is raised"""
        start, end = interval
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            room_reservation(existing, interval)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_valid_interval_processing_branch(self, existing, interval):
        """Test branch: not (start >= end) -> function continues to overlap checking"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = room_reservation(existing, interval)
        
        # Should either succeed (True) or fail due to overlap (False)
        assert isinstance(success, bool)
        assert isinstance(result, list)
        
        # Result should always be sorted
        assert result == sorted(result)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_overlap_detection_branch(self, existing, interval):
        """Test branch: not (end <= s or start >= e) -> return False, existing"""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Create an existing interval that overlaps with the new interval
        # Overlap occurs when: not (end <= s or start >= e)
        # Which is equivalent to: end > s and start < e
        overlapping_exists = any(not (end <= s or start >= e) for s, e in existing)
        assume(overlapping_exists)
        
        success, result = room_reservation(existing, interval)
        
        # Should return False and original existing list unchanged
        assert success is False
        assert result == existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_non_overlap_continuation_branch(self, existing, interval):
        """Test branch: not (not (end <= s or start >= e)) -> continue checking other intervals"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = room_reservation(existing, interval)
        
        # Should return True and list with new interval added
        assert success is True
        assert result == sorted(existing + [interval])

    # FUNCTION PROPERTIES TESTS

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_interval_validation_property(self, existing, interval):
        """Test property: interval_validation - room_reservation(existing, (start, end)) raises ValueError if start >= end"""
        start, end = interval
        
        # If start >= end, should raise ValueError
        if start >= end:
            with pytest.raises(ValueError, match="invalid interval"):
                room_reservation(existing, interval)
        else:
            # Valid interval should not raise ValueError
            success, result = room_reservation(existing, interval)
            assert isinstance(success, bool)
            assert isinstance(result, list)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_overlap_detection_correctness_property(self, existing, interval):
        """Test property: overlap_detection_correctness - room_reservation(existing, interval) returns False if interval overlaps any existing interval"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = room_reservation(existing, interval)
        
        # Check overlap detection logic
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        if has_overlap:
            assert success is False
            assert result == existing
        else:
            assert success is True
            assert result == sorted(existing + [interval])

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_non_overlap_insertion_property(self, existing, interval):
        """Test property: non_overlap_insertion - room_reservation(existing, interval) returns True, updated where updated contains all existing intervals plus new interval"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = room_reservation(existing, interval)
        
        # Should return True and updated list with new interval
        assert success is True
        assert result == sorted(existing + [interval])

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_result_sorting_property(self, existing, interval):
        """Test property: result_sorting - room_reservation(existing, interval) returns True, updated where updated is sorted by start time"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = room_reservation(existing, interval)
        
        # Result should always be sorted regardless of success
        assert result == sorted(result)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_existing_intervals_preservation_property(self, existing, interval):
        """Test property: existing_intervals_preservation - room_reservation(existing, interval) returns True, updated where existing ⊆ updated"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = room_reservation(existing, interval)
        
        # Should return True and updated list containing all existing intervals
        assert success is True
        assert all(interval in result for interval in existing)
        assert interval in result

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_touching_endpoint_overlap_bug_property(self, existing, interval):
        """Test property: touching_endpoint_overlap_bug - room_reservation(existing, interval) returns False when intervals touch at endpoints (end == s or start == e)"""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Create a case where intervals touch at endpoints
        # For example: new interval (1, 3) and existing (3, 5) - they touch at 3
        touching_exists = any(end == s or start == e for s, e in existing)
        assume(touching_exists)
        
        success, result = room_reservation(existing, interval)
        
        # Should return False because touching endpoints are treated as overlap
        assert success is False
        assert result == existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_monotonicity_property(self, existing, interval):
        """Test property: monotonicity - if room_reservation(existing, interval) returns True, updated then for any subset existing' ⊆ existing, room_reservation(existing', interval) also returns True, updated' where updated' ⊆ updated"""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # First, test with full existing list
        success_full, result_full = room_reservation(existing, interval)
        
        if success_full:
            # If successful with full list, should also be successful with any subset
            for i in range(len(existing)):
                subset = existing[:i] + existing[i+1:]  # Remove one element
                success_subset, result_subset = room_reservation(subset, interval)
                
                # Should also succeed with subset
                assert success_subset is True
                # Result should be subset of full result
                assert all(interval in result_full for interval in result_subset)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval1=tuples(integers(), integers()),
        interval2=tuples(integers(), integers())
    )
    def test_commutativity_property(self, existing, interval1, interval2):
        """Test property: commutativity - room_reservation(existing, (start, end)) returns True, updated1 and room_reservation(existing, (start', end')) returns True, updated2 implies room_reservation(updated1, (start', end')) returns True, final and room_reservation(updated2, (start, end)) returns True, final where final is the same in both cases"""
        start1, end1 = interval1
        start2, end2 = interval2
        assume(start1 < end1 and start2 < end2)  # Both intervals valid
        
        # Check that neither overlaps with existing
        no_overlap1 = not any(not (end1 <= s or start1 >= e) for s, e in existing)
        no_overlap2 = not any(not (end2 <= s or start2 >= e) for s, e in existing)
        assume(no_overlap1 and no_overlap2)
        
        # Book first interval
        success1, result1 = room_reservation(existing, interval1)
        assert success1 is True
        
        # Book second interval with the result from first booking
        success2, result2 = room_reservation(result1, interval2)
        assert success2 is True
        
        # Book second interval with original existing list
        success3, result3 = room_reservation(existing, interval2)
        assert success3 is True
        
        # Book first interval with the result from second booking
        success4, result4 = room_reservation(result3, interval1)
        assert success4 is True
        
        # Both final results should be the same
        assert sorted(result2) == sorted(result4)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_idempotence_property(self, existing, interval):
        """Test property: idempotence - room_reservation(room_reservation(existing, interval)[1], interval) returns True, updated where updated equals the result of the first call"""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        # First booking
        success1, result1 = room_reservation(existing, interval)
        assert success1 is True
        
        # Second booking with the result from first booking
        success2, result2 = room_reservation(result1, interval)
        
        # Second booking should always fail because the interval already exists
        assert success2 is False
        assert result2 == result1

    # ADDITIONAL EDGE CASE TESTS

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_empty_existing_list(self, existing, interval):
        """Test booking with empty existing list."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) == 0)
        
        success, result = room_reservation(existing, interval)
        
        # Should always succeed with empty list
        assert success is True
        assert result == [interval]

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_single_existing_interval(self, existing, interval):
        """Test booking with single existing interval."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) == 1)
        
        s, e = existing[0]
        
        success, result = room_reservation(existing, interval)
        
        # Check overlap logic
        has_overlap = not (end <= s or start >= e)
        
        if has_overlap:
            assert success is False
            assert result == existing
        else:
            assert success is True
            assert result == sorted(existing + [interval])

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_negative_time_values(self, existing, interval):
        """Test that function handles negative time values correctly."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = room_reservation(existing, interval)
        
        # Verify result properties
        assert isinstance(success, bool)
        assert isinstance(result, list)
        assert all(isinstance(res_interval, tuple) and len(res_interval) == 2 for res_interval in result)
        assert all(isinstance(res_start, int) and isinstance(res_end, int) for res_start, res_end in result)
        assert result == sorted(result)  # Should always be sorted

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_timeline_length_property(self, existing, interval):
        """Test that timeline length increases by 1 on successful booking."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = room_reservation(existing, interval)
        
        # Should be successful and result should have one more element
        assert success is True
        assert len(result) == len(existing) + 1

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_edge_case_touching_intervals(self, existing, interval):
        """Test edge cases with touching intervals."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Test various touching scenarios
        for s, e in existing:
            # Case 1: new interval touches existing at start
            if end == s:
                success, result = room_reservation(interval, existing)
                assert success is False  # Should fail due to touching
                assert result == existing
            
            # Case 2: new interval touches existing at end  
            if start == e:
                success, result = room_reservation(interval, existing)
                assert success is False  # Should fail due to touching
                assert result == existing

    @given(
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000))),
        interval=tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000))
    )
    def test_bounded_time_values(self, existing, interval):
        """Test with bounded time values to ensure reasonable test performance."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = room_reservation(existing, interval)
        
        # Verify all time values in result are within bounds
        assert all(0 <= s <= 1000 and 0 <= e <= 1000 for s, e in result)
        
        # Verify result is sorted
        assert result == sorted(result)
        
        # Verify no modification on overlap
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        if has_overlap:
            assert success is False
            assert result == existing
        else:
            assert success is True
            assert result == sorted(existing + [interval])

    @given(
        existing=lists(tuples(integers(), integers())),
        interval1=tuples(integers(), integers()),
        interval2=tuples(integers(), integers())
    )
    def test_multiple_bookings_property(self, existing, interval1, interval2):
        """Test that multiple non-overlapping bookings work correctly."""
        start1, end1 = interval1
        start2, end2 = interval2
        assume(start1 < end1 and start2 < end2)  # Both intervals valid
        assume(start1 < end1 <= start2 < end2)  # interval1 ends before interval2 starts
        
        # Check that neither overlaps with existing
        no_overlap1 = not any(not (end1 <= s or start1 >= e) for s, e in existing)
        no_overlap2 = not any(not (end2 <= s or start2 >= e) for s, e in existing)
        assume(no_overlap1 and no_overlap2)
        
        # Book first interval
        success1, result1 = room_reservation(existing, interval1)
        assert success1 is True
        
        # Book second interval with updated list
        success2, result2 = room_reservation(result1, interval2)
        assert success2 is True
        
        # Final result should contain both intervals
        expected = sorted(existing + [interval1, interval2])
        assert result2 == expected