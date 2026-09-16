"""
Tests for inspection_booking function using Hypothesis testing framework.
Tests all semantic properties identified in properties/inspection_booking_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


# Import the function under test
from dataset.python_programs.inspection_booking import inspection_booking


class TestInspectionBooking:
    """Test class for inspection_booking function semantic properties."""

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_invalid_interval_raises_value_error(self, existing, candidate):
        """Test that invalid intervals (start >= end) raise ValueError."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError, match="start must be before end"):
            inspection_booking(existing, candidate)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1),
        candidate=tuples(integers(), integers())
    )
    def test_conflict_detection_returns_false(self, existing, candidate):
        """Test that overlapping intervals return False with existing list."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Find an existing slot that overlaps with candidate
        overlapping_slot = None
        for slot in existing:
            if self._overlaps(slot, candidate):
                overlapping_slot = slot
                break
        
        assume(overlapping_slot is not None)
        
        result, returned_list = inspection_booking(existing, candidate)
        assert result is False
        assert returned_list == list(existing)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_valid_interval_check_no_exception(self, existing, candidate):
        """Test that valid intervals (start < end) don't raise exceptions."""
        assume(candidate[0] < candidate[1])
        
        # This should not raise any exception
        try:
            result, returned_list = inspection_booking(existing, candidate)
            # If we get here, the test passes
            assert True
        except ValueError as e:
            if "start must be before end" in str(e):
                pytest.fail(f"Valid interval {candidate} incorrectly raised ValueError: {e}")
            else:
                # Re-raise if it's a different ValueError
                raise

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_conflict_free_insertion(self, existing, candidate):
        """Test that non-overlapping intervals are inserted and list is sorted."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Ensure candidate doesn't overlap with any existing slot
        for slot in existing:
            assume(not self._overlaps(slot, candidate))
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        expected_list = sorted(existing + [candidate])
        assert returned_list == expected_list

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_sorted_output(self, existing, candidate):
        """Test that merged list is sorted by start time."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Ensure candidate doesn't overlap with any existing slot
        for slot in existing:
            assume(not self._overlaps(slot, candidate))
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        # Check that the list is sorted by start time
        for i in range(len(returned_list) - 1):
            assert returned_list[i][0] <= returned_list[i + 1][0]

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_immutability_preservation(self, existing, candidate):
        """Test that existing list is not modified."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Ensure candidate doesn't overlap with any existing slot
        for slot in existing:
            assume(not self._overlaps(slot, candidate))
        
        # Make a copy to compare against
        original_existing = list(existing)
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        # The original list should be unchanged
        assert existing == original_existing

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1),
        candidate=tuples(integers(), integers())
    )
    def test_boundary_touch_overlap(self, existing, candidate):
        """Test that boundary-touching intervals are considered overlapping."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Create a candidate that touches the boundary of an existing slot
        boundary_slot = None
        for slot in existing:
            # Check if candidate touches slot at start boundary: candidate[1] == slot[0]
            if candidate[1] == slot[0]:
                boundary_slot = slot
                break
            # Check if candidate touches slot at end boundary: candidate[0] == slot[1]
            elif candidate[0] == slot[1]:
                boundary_slot = slot
                break
        
        assume(boundary_slot is not None)
        
        # The overlaps function should return True for boundary-touching intervals
        assert self._overlaps(boundary_slot, candidate) is True
        
        # This should return False (conflict detected)
        result, returned_list = inspection_booking(existing, candidate)
        assert result is False
        assert returned_list == list(existing)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1),
        candidate=tuples(integers(), integers())
    )
    def test_no_duplicate_insertion(self, existing, candidate):
        """Test that identical intervals are not inserted."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Find an existing slot that is identical to candidate
        identical_slot = None
        for slot in existing:
            if slot == candidate:
                identical_slot = slot
                break
        
        assume(identical_slot is not None)
        
        result, returned_list = inspection_booking(existing, candidate)
        assert result is False
        assert returned_list == list(existing)

    def _overlaps(self, a, b):
        """
        Helper method to check if two intervals overlap.
        This replicates the overlaps function from inspection_booking.py.
        """
        return not (b[1] <= a[0] or b[0] >= a[1])


class TestInspectionBookingEdgeCases:
    """Additional edge case tests for inspection_booking function."""

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0, max_size=10),
        candidate=tuples(integers(), integers())
    )
    def test_empty_existing_list(self, existing, candidate):
        """Test behavior with empty existing list."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Ensure no overlaps (trivially true for empty list)
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        assert returned_list == [candidate]

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1, max_size=5),
        candidate=tuples(integers(), integers())
    )
    def test_multiple_overlaps(self, existing, candidate):
        """Test behavior when candidate overlaps with multiple existing slots."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Find multiple overlapping slots
        overlapping_slots = [slot for slot in existing if self._overlaps(slot, candidate)]
        assume(len(overlapping_slots) >= 2)
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is False
        assert returned_list == list(existing)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0, max_size=10),
        candidate=tuples(integers(), integers())
    )
    def test_insertion_at_beginning(self, existing, candidate):
        """Test insertion at the beginning of the sorted list."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Ensure no overlaps and candidate should be inserted at beginning
        for slot in existing:
            assume(not self._overlaps(slot, candidate))
            assume(candidate[0] < slot[0])
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        assert returned_list[0] == candidate
        assert sorted(returned_list) == returned_list

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0, max_size=10),
        candidate=tuples(integers(), integers())
    )
    def test_insertion_at_end(self, existing, candidate):
        """Test insertion at the end of the sorted list."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Ensure no overlaps and candidate should be inserted at end
        for slot in existing:
            assume(not self._overlaps(slot, candidate))
            assume(candidate[0] > slot[0])
        
        result, returned_list = inspection_booking(existing, candidate)
        
        assert result is True
        assert returned_list[-1] == candidate
        assert sorted(returned_list) == returned_list

    def _overlaps(self, a, b):
        """
        Helper method to check if two intervals overlap.
        This replicates the overlaps function from inspection_booking.py.
        """
        return not (b[1] <= a[0] or b[0] >= a[1])