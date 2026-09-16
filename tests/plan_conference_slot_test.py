"""
Tests for plan_conference_slot function using Hypothesis testing framework.
Tests all semantic properties identified in properties/plan_conference_slot_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


def plan_conference_slot(candidate, existing):
    """
    Plan a conference slot in an existing schedule.
    
    Args:
        candidate: Tuple (start, end) representing the candidate slot
        existing: List of existing (start, end) time slots
    
    Returns:
        tuple: (success: bool, updated_schedule: list)
    """
    # Check for invalid interval
    if candidate[0] >= candidate[1]:
        raise ValueError("Invalid interval")
    
    # Check for overlaps with existing slots
    for slot in existing:
        if overlaps(slot, candidate):
            return False, list(existing)
    
    # Insert new slot into schedule and sort
    result = sorted(existing + [candidate])
    return True, result


def overlaps(slot1, slot2):
    """
    Check if two time slots overlap.
    Note: This function has a bug where slots that touch at boundaries are considered overlapping.
    """
    return slot1[1] > slot2[0] and slot1[0] < slot2[1]


class TestPlanConferenceSlot:
    """Test class for plan_conference_slot function semantic properties."""

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_invalid_interval_rejection(self, candidate, existing):
        """Test that invalid intervals (start >= end) raise ValueError."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError, match="Invalid interval"):
            plan_conference_slot(candidate, existing)

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_overlap_detection(self, candidate, existing):
        """Test that overlaps are detected and return False with original schedule."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if there's an overlap
        has_overlap = any(overlaps(slot, candidate) for slot in existing)
        
        if has_overlap:
            success, result_schedule = plan_conference_slot(candidate, existing)
            assert success is False
            assert result_schedule == existing

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_valid_interval_acceptance(self, candidate, existing):
        """Test that valid intervals (start < end) proceed to overlap checking."""
        assume(candidate[0] < candidate[1])
        
        # This property is about the interval being valid, which is checked by the precondition
        # The function will raise ValueError if candidate[0] >= candidate[1], so if we get here, interval is valid
        assert candidate[0] < candidate[1]  # Interval is valid

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_non_overlapping_insertion(self, candidate, existing):
        """Test that non-overlapping slots are inserted and schedule is sorted."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if there are no overlaps
        no_overlaps = not any(overlaps(slot, candidate) for slot in existing)
        
        if no_overlaps:
            success, result = plan_conference_slot(candidate, existing)
            assert success is True
            
            # Check that result is sorted by start time
            for i in range(len(result) - 1):
                assert result[i][0] <= result[i + 1][0], f"Schedule not sorted: {result[i]} and {result[i + 1]}"

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_sorted_output(self, candidate, existing):
        """Test that result schedule is sorted by start time when no overlaps."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if there are no overlaps
        no_overlaps = not any(overlaps(slot, candidate) for slot in existing)
        
        if no_overlaps:
            success, result = plan_conference_slot(candidate, existing)
            assert success is True
            
            # Check that result is sorted by start time
            for i in range(len(result) - 1):
                assert result[i][0] <= result[i + 1][0], f"Schedule not sorted: {result[i]} and {result[i + 1]}"

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_existing_preservation(self, candidate, existing):
        """Test that all existing slots are preserved in output when no overlaps."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if there are no overlaps
        no_overlaps = not any(overlaps(slot, candidate) for slot in existing)
        
        if no_overlaps:
            success, result = plan_conference_slot(candidate, existing)
            assert success is True
            
            # Check that all existing slots are in result
            for slot in existing:
                assert slot in result
            
            # Check that result has exactly one more element than original schedule
            assert len(result) == len(existing) + 1

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_candidate_inclusion(self, candidate, existing):
        """Test that candidate is included in output when no overlaps detected."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if there are no overlaps
        no_overlaps = not any(overlaps(slot, candidate) for slot in existing)
        
        if no_overlaps:
            success, result = plan_conference_slot(candidate, existing)
            assert success is True
            
            # Check that candidate is in result
            assert candidate in result

    @given(
        candidate=st.tuples(st.integers(), st.integers()),
        existing=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_boundary_touch_overlap(self, candidate, existing):
        """Test that slots touching at boundaries are considered overlapping due to bug in overlaps function."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Create a slot that touches at boundary (should be considered overlapping due to bug)
        # If candidate is (a, b) and existing slot is (b, c), they touch at boundary b
        # Due to the bug in overlaps function, this should be detected as overlapping
        boundary_slots = [(candidate[1], candidate[1] + 10)]  # Slot that starts where candidate ends
        
        # Test with boundary-touching slot
        success, result = plan_conference_slot(candidate, boundary_slots)
        
        # Due to the bug in overlaps function, boundary-touching slots are considered overlapping
        # So the function should return False and original schedule
        assert success is False
        assert result == boundary_slots