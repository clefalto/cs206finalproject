import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


def reservation_booking(interval, existing):
    """
    Book a reservation for a time interval, checking for conflicts with existing reservations.
    
    Args:
        interval: Tuple of (start, end) times
        existing: List of existing (start, end) time intervals
    
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


class TestReservationBooking:
    """Test suite for reservation_booking function using Hypothesis."""

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_invalid_interval_error(self, interval, existing):
        """Test that invalid intervals (start >= end) raise ValueError."""
        start, end = interval
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            reservation_booking(interval, existing)

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_valid_interval_processing(self, interval, existing):
        """Test that valid intervals are processed correctly."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = reservation_booking(interval, existing)
        
        # Should either succeed (True) or fail due to overlap (False)
        assert isinstance(success, bool)
        assert isinstance(result, list)
        
        # Result should always be sorted
        assert result == sorted(result)

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_overlap_detection(self, interval, existing):
        """Test that overlapping intervals are detected and booking fails."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Create an existing interval that overlaps with the new interval
        # Overlap occurs when: not (end <= s or start >= e)
        # Which is equivalent to: end > s and start < e
        overlapping_exists = any(not (end <= s or start >= e) for s, e in existing)
        assume(overlapping_exists)
        
        success, result = reservation_booking(interval, existing)
        
        # Should return False and original existing list unchanged
        assert success is False
        assert result == existing

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_no_overlap_processing(self, interval, existing):
        """Test that non-overlapping intervals are processed successfully."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = reservation_booking(interval, existing)
        
        # Should return True and list with new interval added
        assert success is True
        assert result == sorted(existing + [interval])

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_interval_validation_property(self, interval, existing):
        """Test the interval validation property: start < end."""
        start, end = interval
        
        # If start >= end, should raise ValueError
        if start >= end:
            with pytest.raises(ValueError, match="invalid interval"):
                reservation_booking(interval, existing)
        else:
            # Valid interval should not raise ValueError
            success, result = reservation_booking(interval, existing)
            assert isinstance(success, bool)
            assert isinstance(result, list)

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_overlap_detection_property(self, interval, existing):
        """Test the overlap detection property."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = reservation_booking(interval, existing)
        
        # Check overlap detection logic
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        if has_overlap:
            assert success is False
            assert result == existing
        else:
            assert success is True
            assert result == sorted(existing + [interval])

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_interval_insertion_property(self, interval, existing):
        """Test the interval insertion property."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = reservation_booking(interval, existing)
        
        # Should return True and updated list with new interval
        assert success is True
        assert result == sorted(existing + [interval])

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_sorted_output_property(self, interval, existing):
        """Test that the output is always sorted."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = reservation_booking(interval, existing)
        
        # Result should always be sorted regardless of success
        assert result == sorted(result)

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_no_modification_on_overlap_property(self, interval, existing):
        """Test that existing list is unchanged when booking fails due to overlap."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Check if there's any overlap
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        assume(has_overlap)
        
        success, result = reservation_booking(interval, existing)
        
        # Should return False and original existing list unchanged
        assert success is False
        assert result == existing

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_touching_endpoints_overlap_property(self, interval, existing):
        """Test that touching endpoints are treated as overlap."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Create a case where intervals touch at endpoints
        # For example: new interval (1, 3) and existing (3, 5) - they touch at 3
        touching_exists = any(end == s or start == e for s, e in existing)
        assume(touching_exists)
        
        success, result = reservation_booking(interval, existing)
        
        # Should return False because touching endpoints are treated as overlap
        assert success is False
        assert result == existing

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_timeline_length_property(self, interval, existing):
        """Test that timeline length increases by 1 on successful booking."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = reservation_booking(interval, existing)
        
        # Should be successful and result should have one more element
        assert success is True
        assert len(result) == len(existing) + 1

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_empty_existing_list(self, interval, existing):
        """Test booking with empty existing list."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) == 0)
        
        success, result = reservation_booking(interval, existing)
        
        # Should always succeed with empty list
        assert success is True
        assert result == [interval]

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_single_existing_interval(self, interval, existing):
        """Test booking with single existing interval."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) == 1)
        
        s, e = existing[0]
        
        success, result = reservation_booking(interval, existing)
        
        # Check overlap logic
        has_overlap = not (end <= s or start >= e)
        
        if has_overlap:
            assert success is False
            assert result == existing
        else:
            assert success is True
            assert result == sorted(existing + [interval])

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_negative_time_values(self, interval, existing):
        """Test that function handles negative time values correctly."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = reservation_booking(interval, existing)
        
        # Verify result properties
        assert isinstance(success, bool)
        assert isinstance(result, list)
        assert all(isinstance(res_interval, tuple) and len(res_interval) == 2 for res_interval in result)
        assert all(isinstance(res_start, int) and isinstance(res_end, int) for res_start, res_end in result)
        assert result == sorted(result)  # Should always be sorted

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_commutative_property(self, interval, existing):
        """Test that booking order doesn't affect final result when no overlaps."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        assume(no_overlap)
        
        success, result = reservation_booking(interval, existing)
        
        # The result should be the same as if we sorted the combined list
        expected = sorted(existing + [interval])
        assert success is True
        assert result == expected

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_idempotent_property(self, interval, existing):
        """Test that booking the same interval twice fails appropriately."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        # First booking
        success1, result1 = reservation_booking(interval, existing)
        
        # Second booking with the result from first booking
        success2, result2 = reservation_booking(interval, result1)
        
        # Second booking should always fail because the interval already exists
        assert success2 is False
        assert result2 == result1

    @given(
        interval1=tuples(integers(), integers()),
        interval2=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_multiple_bookings_property(self, interval1, interval2, existing):
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
        success1, result1 = reservation_booking(interval1, existing)
        assert success1 is True
        
        # Book second interval with updated list
        success2, result2 = reservation_booking(interval2, result1)
        assert success2 is True
        
        # Final result should contain both intervals
        expected = sorted(existing + [interval1, interval2])
        assert result2 == expected

    @given(
        interval=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_edge_case_touching_intervals(self, interval, existing):
        """Test edge cases with touching intervals."""
        start, end = interval
        assume(start < end)  # Valid interval
        assume(len(existing) > 0)
        
        # Test various touching scenarios
        for s, e in existing:
            # Case 1: new interval touches existing at start
            if end == s:
                success, result = reservation_booking(interval, existing)
                assert success is False  # Should fail due to touching
                assert result == existing
            
            # Case 2: new interval touches existing at end  
            if start == e:
                success, result = reservation_booking(interval, existing)
                assert success is False  # Should fail due to touching
                assert result == existing

    @given(
        interval=tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_bounded_time_values(self, interval, existing):
        """Test with bounded time values to ensure reasonable test performance."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result = reservation_booking(interval, existing)
        
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