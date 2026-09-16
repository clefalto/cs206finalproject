"""
Tests for schedule_call function using Hypothesis testing framework.
Tests all semantic properties identified in properties/schedule_call_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import lists, tuples, integers


class TestScheduleCall:
    """Test class for schedule_call function semantic properties."""

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_invalid_interval_rejection(self, existing, candidate):
        """Test that invalid intervals (start >= end) raise ValueError."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError, match="start must be before end"):
            schedule_call(existing, candidate)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1),
        candidate=tuples(integers(), integers())
    )
    def test_overlap_rejection(self, existing, candidate):
        """Test that overlapping intervals return False and original list."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Find an existing slot that overlaps with candidate
        overlapping_slot = None
        for slot in existing:
            if overlaps(slot, candidate):
                overlapping_slot = slot
                break
        
        assume(overlapping_slot is not None)  # Ensure we have an overlap
        
        result = schedule_call(existing, candidate)
        assert result == (False, list(existing))

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_valid_interval_requirement(self, existing, candidate):
        """Test that valid intervals (start < end) don't raise ValueError."""
        assume(candidate[0] < candidate[1])
        
        # Should not raise ValueError for valid intervals
        try:
            result = schedule_call(existing, candidate)
            # If we get here, the function didn't raise an exception
            assert True
        except ValueError as e:
            if "start must be before end" in str(e):
                pytest.fail(f"Valid interval {candidate} incorrectly rejected")

    @given(
        existing=lists(tuples(integers(), integers()), min_size=1),
        candidate=tuples(integers(), integers())
    )
    def test_overlap_detection(self, existing, candidate):
        """Test that overlapping intervals are detected and return False."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Check if any slot in existing overlaps with candidate
        has_overlap = any(overlaps(slot, candidate) for slot in existing)
        
        if has_overlap:
            result = schedule_call(existing, candidate)
            assert result == (False, list(existing))

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_successful_merge(self, existing, candidate):
        """Test that non-overlapping intervals are successfully merged."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        assume(not any(overlaps(slot, candidate) for slot in existing))  # No overlap precondition
        
        result = schedule_call(existing, candidate)
        expected_merged = sorted(existing + [candidate])
        
        assert result == (True, expected_merged)

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_sorted_output(self, existing, candidate):
        """Test that successful merge returns sorted list."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        assume(not any(overlaps(slot, candidate) for slot in existing))  # No overlap precondition
        
        result = schedule_call(existing, candidate)
        success, merged = result
        
        assert success == True
        # Check that merged is sorted
        for i in range(len(merged) - 1):
            assert merged[i][0] <= merged[i + 1][0]

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_no_modification_on_failure(self, existing, candidate):
        """Test that original list is not modified on failure."""
        assume(candidate[0] >= candidate[1] or any(overlaps(slot, candidate) for slot in existing))
        
        original_existing = list(existing)  # Make a copy
        result = schedule_call(existing, candidate)
        
        assert result == (False, original_existing)
        # Verify the original list wasn't modified
        assert existing == original_existing

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_boundary_touch_overlap_bug(self, existing, candidate):
        """Test that boundary-touching intervals are considered overlapping."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        
        # Create a slot that touches at the boundary
        boundary_slot = (candidate[1], candidate[1] + 1)  # Touches at end
        existing_with_boundary = existing + [boundary_slot]
        
        result = schedule_call(existing_with_boundary, candidate)
        assert result == (False, list(existing_with_boundary))

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_monotonicity(self, existing, candidate):
        """Test that if existing is sorted, merged result is also sorted."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        assume(not any(overlaps(slot, candidate) for slot in existing))  # No overlap precondition
        
        # Sort existing to ensure it's sorted
        sorted_existing = sorted(existing)
        
        result = schedule_call(sorted_existing, candidate)
        success, merged = result
        
        assert success == True
        # Check that merged is sorted
        for i in range(len(merged) - 1):
            assert merged[i][0] <= merged[i + 1][0]

    @given(
        existing=lists(tuples(integers(), integers()), min_size=0),
        candidate=tuples(integers(), integers())
    )
    def test_idempotence(self, existing, candidate):
        """Test that schedule_call is idempotent with respect to existing list order."""
        assume(candidate[0] < candidate[1])  # Valid interval precondition
        assume(not any(overlaps(slot, candidate) for slot in existing))  # No overlap precondition
        
        # Test with original order
        result1 = schedule_call(existing, candidate)
        
        # Test with sorted order
        sorted_existing = sorted(existing)
        result2 = schedule_call(sorted_existing, candidate)
        
        # Both should succeed and produce the same sorted result
        assert result1[0] == True
        assert result2[0] == True
        assert sorted(result1[1]) == sorted(result2[1])


def overlaps(a, b):
    """Helper function to check if two intervals overlap."""
    return a[0] < b[1] and b[0] < a[1]