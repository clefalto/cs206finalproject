"""
Hypothesis tests for plan_desk_slot function semantic properties.
Tests all properties defined in properties/plan_desk_slot_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers


def plan_desk_slot(existing, interval):
    """
    Schedule a desk interval without overlaps.
    existing: sorted list of (start, end)
    interval: (start, end)
    """
    start, end = interval
    if start >= end:
        raise ValueError("invalid interval")

    for s, e in existing:
        # BUG: touching endpoints treated as overlap.
        if not (end <= s or start >= e):
            return False, existing

    updated = existing + [interval]
    updated.sort()
    return True, updated


class TestPlanDeskSlotProperties:
    """Test class for plan_desk_slot semantic properties using Hypothesis."""

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_invalid_interval_error_branch(self, start, end, existing):
        """Test branch property: invalid_interval_error - if start >= end then ValueError is raised"""
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            plan_desk_slot(existing, (start, end))

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_overlap_detection_branch(self, start, end, existing):
        """Test branch property: overlap_detection - if intervals overlap then return False, existing"""
        assume(start < end)  # Valid interval
        
        # Find an existing interval that overlaps with (start, end)
        overlapping_found = False
        for s, e in existing:
            if not (end <= s or start >= e):  # Overlap condition
                overlapping_found = True
                break
        
        if overlapping_found:
            result, returned_existing = plan_desk_slot(existing, (start, end))
            assert result is False
            assert returned_existing == existing  # Should return original list unchanged

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_valid_interval_check_function(self, start, end, existing):
        """Test function property: valid_interval_check - if start >= end then ValueError is raised"""
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid interval"):
            plan_desk_slot(existing, (start, end))

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_overlap_detection_function(self, start, end, existing):
        """Test function property: overlap_detection - if any existing interval overlaps with new interval then return False, existing"""
        assume(start < end)  # Valid interval
        
        # Check if any existing interval overlaps
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        result, returned_existing = plan_desk_slot(existing, (start, end))
        
        if has_overlap:
            assert result is False
            assert returned_existing == existing
        else:
            assert result is True

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_interval_insertion_function(self, start, end, existing):
        """Test function property: interval_insertion - if no overlap then return True, updated where updated contains new interval"""
        assume(start < end)  # Valid interval
        
        # Ensure no overlap with existing intervals
        assume(all(end <= s or start >= e for s, e in existing))
        
        result, updated = plan_desk_slot(existing, (start, end))
        
        assert result is True
        assert (start, end) in updated
        assert len(updated) == len(existing) + 1

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_list_sorting_function(self, start, end, existing):
        """Test function property: list_sorting - updated list is sorted after insertion"""
        assume(start < end)  # Valid interval
        
        # Ensure no overlap with existing intervals
        assume(all(end <= s or start >= e for s, e in existing))
        
        result, updated = plan_desk_slot(existing, (start, end))
        
        if result is True:
            # Check that the list is sorted
            assert updated == sorted(updated)

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_non_destructive_existing_function(self, start, end, existing):
        """Test function property: non_destructive_existing - existing list remains unchanged when overlap detected"""
        assume(start < end)  # Valid interval
        
        # Ensure there's an overlap
        assume(any(not (end <= s or start >= e) for s, e in existing))
        
        original_existing = existing.copy()
        result, returned_existing = plan_desk_slot(existing, (start, end))
        
        assert result is False
        assert returned_existing == original_existing
        assert existing == original_existing  # Original list should be unchanged

    @given(
        start=integers(min_value=0, max_value=1000),
        end=integers(min_value=0, max_value=1000),
        existing=lists(tuples(integers(min_value=0, max_value=1000), integers(min_value=0, max_value=1000)))
    )
    def test_return_format_function(self, start, end, existing):
        """Test function property: return_format - always returns tuple (bool, list) where bool indicates success"""
        assume(start < end)  # Valid interval
        
        result = plan_desk_slot(existing, (start, end))
        
        # Should always return a tuple
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        # First element should be boolean
        assert isinstance(result[0], bool)
        
        # Second element should be list
        assert isinstance(result[1], list)
        
        # All elements in the list should be tuples of two integers
        for item in result[1]:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert all(isinstance(x, int) for x in item)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])