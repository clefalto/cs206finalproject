import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import lists, tuples, integers
import math


def overlaps(a, b):
    """Check if two intervals overlap (including boundary touching)."""
    return a[0] <= b[1] and b[0] <= a[1]


def reserve_band(existing, candidate):
    """
    Reserve a time band in the existing schedule.
    
    Args:
        existing: List of (start, end) tuples representing existing reservations
        candidate: (start, end) tuple representing the new reservation
        
    Returns:
        (success, updated_list) where success is bool and updated_list is sorted
    """
    # Validate candidate interval
    if candidate[0] >= candidate[1]:
        raise ValueError("Invalid interval: start must be less than end")
    
    # Check for overlaps with existing reservations
    for slot in existing:
        if overlaps(slot, candidate):
            return (False, existing.copy())
    
    # No overlaps, add the new reservation
    result = existing.copy()
    result.append(candidate)
    result.sort(key=lambda x: x[0])  # Sort by start time
    return (True, result)


class TestReserveBand:
    """Test suite for reserve_band function using Hypothesis."""

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_invalid_interval_rejection(self, candidate, existing):
        """Test that invalid intervals (start >= end) raise ValueError."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError, match="Invalid interval"):
            reserve_band(existing, candidate)

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_overlap_prevention(self, existing, candidate):
        """Test that overlapping reservations return (False, original_existing)."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Create a scenario where there's an overlap
        if existing:
            # Find an existing slot and create overlap
            slot = existing[0]
            # Make candidate overlap with this slot
            candidate = (slot[0], slot[1] + 1)  # Overlaps by touching boundary
        
        result = reserve_band(existing, candidate)
        
        # Should return False and original list (copied)
        assert result[0] is False
        assert result[1] == existing
        assert result[1] is not existing  # Should be a copy

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_successful_reservation(self, existing, candidate):
        """Test successful reservation when no overlaps and valid interval."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Ensure no overlaps
        assume(not any(overlaps(slot, candidate) for slot in existing))
        
        result = reserve_band(existing, candidate)
        
        # Should return True and sorted list with new candidate
        assert result[0] is True
        expected = existing.copy()
        expected.append(candidate)
        expected.sort(key=lambda x: x[0])
        assert result[1] == expected

    @given(
        candidate=tuples(integers(), integers()),
        existing=lists(tuples(integers(), integers()))
    )
    def test_interval_validation(self, candidate, existing):
        """Test that candidate[0] < candidate[1] must hold for success."""
        assume(candidate[0] >= candidate[1])
        
        with pytest.raises(ValueError):
            reserve_band(existing, candidate)

    @given(
        a=tuples(integers(), integers()),
        b=tuples(integers(), integers())
    )
    def test_overlap_detection(self, a, b):
        """Test that overlaps function correctly detects interval overlaps."""
        assume(a[0] < a[1] and b[0] < b[1])  # Valid intervals
        
        # Test overlap detection logic
        expected_overlap = a[0] <= b[1] and b[0] <= a[1]
        actual_overlap = overlaps(a, b)
        
        assert actual_overlap == expected_overlap

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_sorted_output(self, existing, candidate):
        """Test that successful reservation returns sorted list by start time."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(not any(overlaps(slot, candidate) for slot in existing))
        
        result = reserve_band(existing, candidate)
        
        if result[0]:  # If reservation succeeded
            # Check that result is sorted by start time
            sorted_result = sorted(result[1], key=lambda x: x[0])
            assert result[1] == sorted_result

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_immutability_on_failure(self, existing, candidate):
        """Test that original list is not modified on failure."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        # Create overlap to ensure failure
        if existing:
            # Make candidate overlap with first existing slot
            slot = existing[0]
            candidate = (slot[0], slot[1] + 1)
        
        original_existing = existing.copy()
        result = reserve_band(existing, candidate)
        
        # Should return copy of original on failure
        assert result[1] == original_existing
        assert result[1] is not existing

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_monotonicity(self, existing, candidate):
        """Test that sorted order is maintained after successful reservation."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(not any(overlaps(slot, candidate) for slot in existing))
        
        # Sort existing list first
        existing_sorted = sorted(existing, key=lambda x: x[0])
        
        result = reserve_band(existing_sorted, candidate)
        
        if result[0]:  # If reservation succeeded
            # Result should still be sorted
            assert result[1] == sorted(result[1], key=lambda x: x[0])

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_boundary_touch_overlap(self, existing, candidate):
        """Test that intervals touching at boundaries are considered overlapping."""
        assume(candidate[0] < candidate[1])  # Valid interval
        
        if existing:
            # Create boundary touch scenario
            slot = existing[0]
            # Make candidate touch at boundary
            candidate = (slot[1], slot[1] + 1)  # Touches at slot[1]
        
        result = reserve_band(existing, candidate)
        
        # Should detect overlap due to boundary touching
        if existing and candidate[0] == existing[0][1]:  # Boundary touch case
            assert result[0] is False

    @given(
        existing=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    def test_idempotence(self, existing, candidate):
        """Test that reserve_band is idempotent when successful."""
        assume(candidate[0] < candidate[1])  # Valid interval
        assume(not any(overlaps(slot, candidate) for slot in existing))
        
        # Sort existing and ensure no internal overlaps
        existing_sorted = sorted(existing, key=lambda x: x[0])
        
        # First reservation
        result1 = reserve_band(existing_sorted, candidate)
        
        if result1[0]:  # If first reservation succeeded
            # Second reservation with the result
            result2 = reserve_band(result1[1], candidate)
            
            # Should get same result
            assert result2[0] is True
            assert result2[1] == result1[1]

    @given(
        existing=lists(tuples(integers(), integers()), max_size=5),
        candidate=tuples(integers(), integers())
    )
    @pytest.mark.parametrize("damping", [0.0, 0.5, 1.0])
    def test_edge_cases(self, existing, candidate, damping):
        """Test various edge cases and boundary conditions."""
        # Test empty existing list
        if not existing:
            assume(candidate[0] < candidate[1])
            result = reserve_band([], candidate)
            assert result[0] is True
            assert result[1] == [candidate]
        
        # Test single element existing list
        if len(existing) == 1:
            assume(candidate[0] < candidate[1])
            # Test both overlap and non-overlap cases
            slot = existing[0]
            if candidate[1] <= slot[0] or candidate[0] >= slot[1]:
                # No overlap
                result = reserve_band(existing, candidate)
                assert result[0] is True
            else:
                # Overlap
                result = reserve_band(existing, candidate)
                assert result[0] is False
                assert result[1] == existing