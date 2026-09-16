"""
Hypothesis tests for schedule_training function semantic properties.

This test file exercises all semantic properties identified in
properties/schedule_training_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers

# Import the function under test
from dataset.python_programs.schedule_training import schedule_training


class TestScheduleTrainingSemanticProperties:
    """Test class for schedule_training semantic properties."""

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_invalid_interval_detection(self, existing, interval):
        """
        Property: invalid_interval_detection
        Formal: if start >= end then ValueError is raised
        """
        start, end = interval
        assume(start >= end)  # This is the condition that triggers the property
        
        with pytest.raises(ValueError, match="start must be before end"):
            schedule_training(existing, interval)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_valid_interval_processing(self, existing, interval):
        """
        Property: valid_interval_processing
        Formal: if start < end then proceed to overlap checking
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Should not raise ValueError for valid intervals
        try:
            result = schedule_training(existing, interval)
            # If we get here, the function didn't raise an exception for valid interval
            assert isinstance(result, tuple)
            assert len(result) == 2
        except ValueError as e:
            if "start must be before end" in str(e):
                pytest.fail(f"Valid interval {interval} incorrectly rejected")

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_overlap_detection(self, existing, interval):
        """
        Property: overlap_detection
        Formal: if intervals overlap then return False, existing
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Check if there's an overlap with any existing interval
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        if has_overlap:
            success, result_existing = schedule_training(existing, interval)
            assert success is False
            assert result_existing == existing  # Original list should be returned unchanged

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_no_overlap_confirmation(self, existing, interval):
        """
        Property: no_overlap_confirmation
        Formal: if intervals don't overlap then continue checking other intervals
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Check if there's no overlap with any existing interval
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        
        if no_overlap:
            success, result_existing = schedule_training(existing, interval)
            assert success is True
            assert interval in result_existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_interval_validation(self, existing, interval):
        """
        Property: interval_validation
        Precondition: interval is a tuple/list with two elements
        Formal: start and end must be comparable and start < end
        """
        start, end = interval
        
        # Test invalid intervals (start >= end)
        assume(start >= end)
        
        with pytest.raises(ValueError, match="start must be before end"):
            schedule_training(existing, interval)

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_overlap_detection_function(self, existing, interval):
        """
        Property: overlap_detection
        Precondition: existing contains valid intervals
        Formal: if any existing interval overlaps with new interval then return False
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Check if there's an overlap
        has_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        if has_overlap:
            success, result_existing = schedule_training(existing, interval)
            assert success is False
            assert result_existing == existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_sorted_output(self, existing, interval):
        """
        Property: sorted_output
        Precondition: existing is a list of intervals
        Formal: updated list is sorted by start time
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Check if there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        
        if no_overlap:
            success, result_existing = schedule_training(existing, interval)
            assert success is True
            
            # Check that result is sorted by start time
            for i in range(len(result_existing) - 1):
                assert result_existing[i][0] <= result_existing[i + 1][0]

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_interval_addition(self, existing, interval):
        """
        Property: interval_addition
        Precondition: no overlap detected
        Formal: if no overlap then interval is added to existing list
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Check if there's no overlap
        no_overlap = not any(not (end <= s or start >= e) for s, e in existing)
        
        if no_overlap:
            success, result_existing = schedule_training(existing, interval)
            assert success is True
            assert interval in result_existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_immutability_preservation(self, existing, interval):
        """
        Property: immutability_preservation
        Precondition: existing is a list
        Formal: original existing list is not modified
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        original_existing = list(existing)  # Make a copy to compare
        
        try:
            success, result_existing = schedule_training(existing, interval)
            
            # The original list should not be modified
            assert existing == original_existing
        except ValueError:
            # Empty interval case - original list should still not be modified
            assert existing == original_existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_return_format(self, existing, interval):
        """
        Property: return_format
        Precondition: function executes successfully
        Formal: returns tuple (bool, list) where bool indicates success and list is updated intervals
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        try:
            result = schedule_training(existing, interval)
            assert isinstance(result, tuple)
            assert len(result) == 2
            
            success, result_existing = result
            assert isinstance(success, bool)
            assert isinstance(result_existing, list)
            
            # All elements in result_existing should be tuples
            for item in result_existing:
                assert isinstance(item, tuple)
                assert len(item) == 2
        except ValueError:
            # Empty interval case is expected to raise ValueError
            pass

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_touching_endpoint_overlap(self, existing, interval):
        """
        Property: touching_endpoint_overlap
        Precondition: intervals share endpoints
        Formal: intervals that touch at endpoints are treated as overlapping (bug noted in code)
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Create a slot that touches at the boundary
        boundary_slot = (end, end + 1)  # Touches at end
        existing_with_boundary = existing + [boundary_slot]
        
        result = schedule_training(existing_with_boundary, interval)
        assert result == (False, list(existing_with_boundary))

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_empty_existing_handling(self, existing, interval):
        """
        Property: empty_existing_handling
        Precondition: existing is empty list
        Formal: if existing is empty then new interval is always added
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        assume(len(existing) == 0)  # Empty existing list
        
        success, result_existing = schedule_training(existing, interval)
        assert success is True
        assert result_existing == [interval]


class TestScheduleTrainingEdgeCases:
    """Test edge cases and additional scenarios."""

    @given(interval=tuples(integers(), integers()))
    def test_empty_existing_timeline(self, interval):
        """Test scheduling with empty existing list."""
        start, end = interval
        assume(start < end)  # Valid interval
        
        success, result_existing = schedule_training([], interval)
        assert success is True
        assert result_existing == [interval]

    @given(existing=lists(tuples(integers(), integers())))
    def test_identical_intervals(self, existing):
        """Test scheduling identical intervals."""
        # Create a valid interval
        interval = (10, 20)
        
        # Remove any intervals that would overlap with our test interval
        non_overlapping_existing = [
            (s, e) for s, e in existing 
            if e <= 10 or s >= 20
        ]
        
        success, result_existing = schedule_training(non_overlapping_existing, interval)
        assert success is True
        assert interval in result_existing

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_adjacent_intervals(self, existing, interval):
        """Test scheduling with adjacent intervals (should not overlap)."""
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Filter existing to only include non-overlapping intervals
        non_overlapping_existing = [
            (s, e) for s, e in existing 
            if e <= start or s >= end
        ]
        
        success, result_existing = schedule_training(non_overlapping_existing, interval)
        assert success is True
        assert interval in result_existing

    @given(
        existing=lists(tuples(integers(), integers()), max_size=5),
        interval=tuples(integers(), integers())
    )
    def test_small_existing_scenarios(self, existing, interval):
        """Test with small existing lists to ensure comprehensive coverage."""
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        try:
            success, result_existing = schedule_training(existing, interval)
            
            if success:
                # Verify interval is included
                assert interval in result_existing
                # Verify result is sorted
                assert result_existing == sorted(result_existing, key=lambda x: x[0])
            else:
                # Verify existing is preserved
                assert result_existing == existing
        except ValueError:
            # Empty interval case
            assert start >= end

    @given(
        existing=lists(tuples(integers(), integers())),
        interval=tuples(integers(), integers())
    )
    def test_overlap_detection_correctness(self, existing, interval):
        """
        Property: overlap_detection_correctness
        Precondition: interval = (start, end) and existing contains intervals (s, e)
        Formal: overlap detected iff not (end <= s or start >= e) for some (s, e) in existing
        """
        start, end = interval
        assume(start < end)  # Valid interval precondition
        
        # Calculate expected overlap using the formal condition
        expected_overlap = any(not (end <= s or start >= e) for s, e in existing)
        
        try:
            success, result_existing = schedule_training(existing, interval)
            
            # If overlap expected, scheduling should fail
            if expected_overlap:
                assert success is False
                assert result_existing == existing
            else:
                # If no overlap expected, scheduling should succeed
                assert success is True
                assert interval in result_existing
        except ValueError:
            # This shouldn't happen with valid intervals
            assert False, "ValueError raised unexpectedly with valid interval"