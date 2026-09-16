import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


def reserve_lane(candidate, existing):
    """
    Reserve a lane for a time interval, checking for conflicts with existing reservations.
    
    Args:
        candidate: Tuple of (start, end) times representing the lane to reserve
        existing: List of existing (start, end) time intervals
    
    Returns:
        Tuple of (success: bool, result: list) where result is either the updated list
        or the original list if reservation failed
    
    Raises:
        ValueError: If candidate interval is invalid (start >= end)
    """
    # Check for invalid interval
    if candidate[0] >= candidate[1]:
        raise ValueError("start must be before end")
    
    # Check for overlaps with existing slots
    for slot in existing:
        if overlaps(slot, candidate):
            return False, list(existing)
    
    # No overlaps, add the new interval and return sorted list
    merged = existing + [candidate]
    merged.sort()
    return True, merged


def overlaps(a, b):
    """
    Check if two intervals overlap, including boundary-touch.
    
    Args:
        a: Tuple of (start, end) times
        b: Tuple of (start, end) times
    
    Returns:
        bool: True if intervals overlap (including touching at boundaries)
    """
    # BUG: touching endpoints treated as overlap.
    return not (b[1] <= a[0] or b[0] >= a[1])


class TestReserveLane:
    """Test suite for reserve_lane function using Hypothesis."""

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_invalid_interval_rejection(self, candidate, existing):
        """Test that invalid intervals (start >= end) raise ValueError."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError, match="start must be before end"):
            reserve_lane(candidate, existing)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_valid_interval_check(self, candidate, existing):
        """Test that valid intervals (start < end) proceed with reservation logic."""
        assume(candidate[0] < candidate[1])
        
        success, result = reserve_lane(candidate, existing)
        
        # Should either succeed (True) or fail due to overlap (False)
        assert isinstance(success, bool)
        assert isinstance(result, list)
        
        # Result should always be sorted
        assert result == sorted(result)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_overlap_rejection(self, candidate, existing):
        """Test that overlapping intervals are detected and reservation fails."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) > 0)
        
        # Check if there's any overlap
        has_overlap = any(overlaps(slot, candidate) for slot in existing)
        assume(has_overlap)
        
        success, result = reserve_lane(candidate, existing)
        
        # Should return False and original existing list unchanged
        assert success is False
        assert result == list(existing)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_successful_reservation(self, candidate, existing):
        """Test that non-overlapping intervals are processed successfully."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(overlaps(slot, candidate) for slot in existing)
        assume(no_overlap)
        
        success, result = reserve_lane(candidate, existing)
        
        # Should return True and list with new interval added
        assert success is True
        assert result == sorted(existing + [candidate])

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_existing_slots_preservation(self, candidate, existing):
        """Test that existing slots are preserved when reservation fails."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) > 0)
        
        # Check if there's any overlap
        has_overlap = any(overlaps(slot, candidate) for slot in existing)
        assume(has_overlap)
        
        success, result = reserve_lane(candidate, existing)
        
        # Should return False and original existing list unchanged
        assert success is False
        assert result == list(existing)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_sorted_output(self, candidate, existing):
        """Test that the output is always sorted."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        success, result = reserve_lane(candidate, existing)
        
        # Result should always be sorted regardless of success
        assert result == sorted(result)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_boundary_touch_overlap(self, candidate, existing):
        """Test that touching endpoints are treated as overlapping."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) > 0)
        
        # Create a case where intervals touch at endpoints
        # For example: candidate (1, 3) and existing (3, 5) - they touch at 3
        touching_exists = any(candidate[1] == slot[0] or candidate[0] == slot[1] for slot in existing)
        assume(touching_exists)
        
        success, result = reserve_lane(candidate, existing)
        
        # Should return False because touching endpoints are treated as overlap
        assert success is False
        assert result == list(existing)

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_overlap_detection(self, candidate, existing):
        """Test the overlap detection function directly."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) > 0)
        
        for slot in existing:
            # Test overlap detection logic
            overlap_result = overlaps(slot, candidate)
            
            # Manual overlap check: intervals overlap if not (b[1] <= a[0] or b[0] >= a[1])
            manual_overlap = not (candidate[1] <= slot[0] or candidate[0] >= slot[1])
            
            assert overlap_result == manual_overlap

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_empty_existing_list(self, candidate, existing):
        """Test reservation with empty existing list."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) == 0)
        
        success, result = reserve_lane(candidate, existing)
        
        # Should always succeed with empty list
        assert success is True
        assert result == [candidate]

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_single_existing_interval(self, candidate, existing):
        """Test reservation with single existing interval."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) == 1)
        
        slot = existing[0]
        
        success, result = reserve_lane(candidate, existing)
        
        # Check overlap logic
        has_overlap = overlaps(slot, candidate)
        
        if has_overlap:
            assert success is False
            assert result == list(existing)
        else:
            assert success is True
            assert result == sorted(existing + [candidate])

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_negative_time_values(self, candidate, existing):
        """Test that function handles negative time values correctly."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        success, result = reserve_lane(candidate, existing)
        
        # Verify result properties
        assert isinstance(success, bool)
        assert isinstance(result, list)
        assert all(isinstance(res_interval, tuple) and len(res_interval) == 2 for res_interval in result)
        assert all(isinstance(res_start, int) and isinstance(res_end, int) for res_start, res_end in result)
        assert result == sorted(result)  # Should always be sorted

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_commutative_property(self, candidate, existing):
        """Test that reservation order doesn't affect final result when no overlaps."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Check that there's no overlap
        no_overlap = not any(overlaps(slot, candidate) for slot in existing)
        assume(no_overlap)
        
        success, result = reserve_lane(candidate, existing)
        
        # The result should be the same as if we sorted the combined list
        expected = sorted(existing + [candidate])
        assert success is True
        assert result == expected

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_idempotent_property(self, candidate, existing):
        """Test that reserving the same interval twice fails appropriately."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # First reservation
        success1, result1 = reserve_lane(candidate, existing)
        
        # Second reservation with the result from first reservation
        success2, result2 = reserve_lane(candidate, result1)
        
        # Second reservation should always fail because the interval already exists
        assert success2 is False
        assert result2 == result1

    @given(
        candidate1=tuples(integers(), integers()),
        candidate2=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_multiple_reservations_property(self, candidate1, candidate2, existing):
        """Test that multiple non-overlapping reservations work correctly."""
        start1, end1 = candidate1
        start2, end2 = candidate2
        assume(start1 < end1 and start2 < end2)  # Both intervals valid
        assume(start1 < end1 <= start2 < end2)  # candidate1 ends before candidate2 starts
        
        # Check that neither overlaps with existing
        no_overlap1 = not any(overlaps(slot, candidate1) for slot in existing)
        no_overlap2 = not any(overlaps(slot, candidate2) for slot in existing)
        assume(no_overlap1 and no_overlap2)
        
        # Reserve first interval
        success1, result1 = reserve_lane(candidate1, existing)
        assert success1 is True
        
        # Reserve second interval with updated list
        success2, result2 = reserve_lane(candidate2, result1)
        assert success2 is True
        
        # Final result should contain both intervals
        expected = sorted(existing + [candidate1, candidate2])
        assert result2 == expected

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_edge_case_touching_intervals(self, candidate, existing):
        """Test edge cases with touching intervals."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(len(existing) > 0)
        
        # Test various touching scenarios
        for slot in existing:
            # Case 1: candidate touches existing at start
            if candidate[1] == slot[0]:
                success, result = reserve_lane(candidate, existing)
                assert success is False  # Should fail due to touching
                assert result == list(existing)
            
            # Case 2: candidate touches existing at end  
            if candidate[0] == slot[1]:
                success, result = reserve_lane(candidate, existing)
                assert success is False  # Should fail due to touching
                assert result == list(existing)

    @given(
        candidate=tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_bounded_time_values(self, candidate, existing):
        """Test with bounded time values to ensure reasonable test performance."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        success, result = reserve_lane(candidate, existing)
        
        # Verify all time values in result are within bounds
        assert all(0 <= s <= 1000 and 0 <= e <= 1000 for s, e in result)
        
        # Verify result is sorted
        assert result == sorted(result)
        
        # Verify no modification on overlap
        has_overlap = any(overlaps(slot, candidate) for slot in existing)
        if has_overlap:
            assert success is False
            assert result == list(existing)
        else:
            assert success is True
            assert result == sorted(existing + [candidate])