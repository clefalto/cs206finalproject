"""
Hypothesis tests for schedule_car function semantic properties.

This test file exercises all semantic properties identified in
properties/schedule_car_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, example, strategies as st
from hypothesis.strategies import lists, tuples, integers

# Import the function under test
from dataset.python_programs.schedule_car import schedule_car


class TestScheduleCarSemanticProperties:
    """Test class for schedule_car semantic properties."""

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_empty_window_detection(self, timeline, window):
        """
        Property: empty_window_detection
        Formal: if window[0] >= window[1] then ValueError is raised
        """
        a, b = window
        assume(a >= b)  # This is the condition that triggers the property
        
        with pytest.raises(ValueError, match="empty window"):
            schedule_car(timeline, window)

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_overlap_detection(self, timeline, window):
        """
        Property: overlap_detection
        Formal: if window overlaps with any existing timeline interval then return (False, timeline)
        """
        a, b = window
        
        # Check if there's an overlap with any existing interval
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_overlap:
            success, result_timeline = schedule_car(timeline, window)
            assert success is False
            assert result_timeline == timeline  # Original timeline should be returned unchanged

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_non_overlap_insertion(self, timeline, window):
        """
        Property: non_overlap_insertion
        Formal: if window does not overlap with any existing timeline interval then return (True, sorted(timeline + [window]))
        """
        a, b = window
        
        # Check if there's no overlap with any existing interval
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_overlap:
            success, result_timeline = schedule_car(timeline, window)
            assert success is True
            expected_timeline = sorted(timeline + [window])
            assert result_timeline == expected_timeline

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_timeline_ordering(self, timeline, window):
        """
        Property: timeline_ordering
        Precondition: timeline is a list of (start, end) tuples and window is a (start, end) tuple
        Formal: result is sorted by start time
        """
        assume(window[0] < window[1])  # Valid window
        
        try:
            success, result_timeline = schedule_car(timeline, window)
            
            # If successful, result should be sorted by start time
            if success:
                assert result_timeline == sorted(result_timeline, key=lambda x: x[0])
        except ValueError:
            # Empty window case is expected to raise ValueError
            pass

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_window_inclusion(self, timeline, window):
        """
        Property: window_inclusion
        Precondition: no overlap with existing timeline
        Formal: window is included in result when scheduling succeeds
        """
        a, b = window
        assume(a < b)  # Valid window
        
        # Check if there's no overlap
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_overlap:
            success, result_timeline = schedule_car(timeline, window)
            assert success is True
            assert window in result_timeline

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_timeline_preservation(self, timeline, window):
        """
        Property: timeline_preservation
        Precondition: overlap detected
        Formal: original timeline is returned unchanged when scheduling fails
        """
        a, b = window
        assume(a < b)  # Valid window
        
        # Check if there's an overlap
        has_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_overlap:
            success, result_timeline = schedule_car(timeline, window)
            assert success is False
            assert result_timeline == timeline

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_overlap_detection_correctness(self, timeline, window):
        """
        Property: overlap_detection_correctness
        Precondition: window = (a, b) and timeline contains intervals (s, e)
        Formal: overlap detected iff not (b <= s or a >= e) for some (s, e) in timeline
        """
        a, b = window
        assume(a < b)  # Valid window
        
        # Calculate expected overlap using the formal condition
        expected_overlap = any(not (b <= s or a >= e) for s, e in timeline)
        
        try:
            success, result_timeline = schedule_car(timeline, window)
            
            # If overlap expected, scheduling should fail
            if expected_overlap:
                assert success is False
                assert result_timeline == timeline
            else:
                # If no overlap expected, scheduling should succeed
                assert success is True
                assert window in result_timeline
        except ValueError:
            # This shouldn't happen with valid windows
            assert False, "ValueError raised unexpectedly with valid window"

    @given(window=tuples(integers(), integers()))
    def test_empty_window_validation(self, window):
        """
        Property: empty_window_validation
        Precondition: window = (a, b)
        Formal: ValueError raised when a >= b
        """
        a, b = window
        assume(a >= b)  # This is the condition that should trigger ValueError
        
        with pytest.raises(ValueError, match="empty window"):
            schedule_car([], window)

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_return_type_consistency(self, timeline, window):
        """
        Property: return_type_consistency
        Precondition: valid inputs
        Formal: always returns tuple of (bool, list) where bool indicates success
        """
        a, b = window
        assume(a < b)  # Valid window
        
        try:
            result = schedule_car(timeline, window)
            assert isinstance(result, tuple)
            assert len(result) == 2
            
            success, result_timeline = result
            assert isinstance(success, bool)
            assert isinstance(result_timeline, list)
            
            # All elements in result_timeline should be tuples
            for item in result_timeline:
                assert isinstance(item, tuple)
                assert len(item) == 2
        except ValueError:
            # Empty window case is expected to raise ValueError
            pass

    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_timeline_monotonicity(self, timeline, window):
        """
        Property: timeline_monotonicity
        Precondition: no overlap
        Formal: result maintains sorted order by start time
        """
        a, b = window
        assume(a < b)  # Valid window
        
        # Check if there's no overlap
        no_overlap = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_overlap:
            success, result_timeline = schedule_car(timeline, window)
            assert success is True
            
            # Check that result is sorted by start time
            for i in range(len(result_timeline) - 1):
                assert result_timeline[i][0] <= result_timeline[i + 1][0]


class TestScheduleCarEdgeCases:
    """Test edge cases and additional scenarios."""

    @given(window=tuples(integers(), integers()))
    def test_empty_timeline(self, window):
        """Test scheduling with empty timeline."""
        a, b = window
        assume(a < b)  # Valid window
        
        success, result_timeline = schedule_car([], window)
        assert success is True
        assert result_timeline == [window]

    @given(timeline=lists(tuples(integers(), integers())))
    def test_identical_windows(self, timeline):
        """Test scheduling identical windows."""
        # Create a valid window
        window = (10, 20)
        
        # Remove any intervals that would overlap with our test window
        non_overlapping_timeline = [
            (s, e) for s, e in timeline 
            if e <= 10 or s >= 20
        ]
        
        success, result_timeline = schedule_car(non_overlapping_timeline, window)
        assert success is True
        assert window in result_timeline

    @example(timeline=[(1, 2), (3, 4)], window=(2, 3))
    @given(
        timeline=lists(tuples(integers(), integers())),
        window=tuples(integers(), integers())
    )
    def test_adjacent_intervals(self, timeline, window):
        """Test scheduling with adjacent intervals (should not overlap)."""
        a, b = window
        assume(a < b)  # Valid window
        
        # Filter timeline to only include non-overlapping intervals
        non_overlapping_timeline = [
            (s, e) for s, e in timeline 
            if e <= a or s >= b
        ]
        
        success, result_timeline = schedule_car(non_overlapping_timeline, window)
        assert success is True
        assert window in result_timeline

    @given(
        timeline=lists(tuples(integers(), integers()), max_size=5),
        window=tuples(integers(), integers())
    )
    def test_small_timeline_scenarios(self, timeline, window):
        """Test with small timelines to ensure comprehensive coverage."""
        a, b = window
        assume(a < b)  # Valid window
        
        try:
            success, result_timeline = schedule_car(timeline, window)
            
            if success:
                # Verify window is included
                assert window in result_timeline
                # Verify result is sorted
                assert result_timeline == sorted(result_timeline, key=lambda x: x[0])
            else:
                # Verify timeline is preserved
                assert result_timeline == timeline
        except ValueError:
            # Empty window case
            assert a >= b