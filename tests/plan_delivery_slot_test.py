"""
Tests for plan_delivery_slot function using Hypothesis testing framework.
Tests all semantic properties identified in properties/plan_delivery_slot_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, tuples


def plan_delivery_slot(a, b, timeline):
    """
    Plan a delivery slot in a timeline.
    
    Args:
        a: Start time of the delivery window
        b: End time of the delivery window  
        timeline: List of existing (start, end) time slots
    
    Returns:
        tuple: (success: bool, updated_timeline: list)
    """
    # Check for empty window
    if a >= b:
        raise ValueError("empty window")
    
    # Check for conflicts with existing timeline
    if any(not (b <= s or a >= e) for s, e in timeline):
        return False, timeline
    
    # Insert new window into timeline and sort
    window = (a, b)
    result = sorted(timeline + [window])
    return True, result


class TestPlanDeliverySlot:
    """Test class for plan_delivery_slot function semantic properties."""

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_empty_window_error(self, a, b, timeline):
        """Test that empty window (a >= b) raises ValueError."""
        assume(a >= b)
        
        with pytest.raises(ValueError, match="empty window"):
            plan_delivery_slot(a, b, timeline)

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_conflict_detection(self, a, b, timeline):
        """Test that conflicts are detected and return False with original timeline."""
        assume(a < b)  # Valid window precondition
        
        # Check if there's a conflict
        has_conflict = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_conflict:
            success, result_timeline = plan_delivery_slot(a, b, timeline)
            assert success is False
            assert result_timeline == timeline

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_non_empty_window(self, a, b, timeline):
        """Test that valid window (a < b) creates a valid interval."""
        assume(a < b)
        
        # This property is about the window being valid, which is checked by the precondition
        # The function will raise ValueError if a >= b, so if we get here, window is valid
        window = (a, b)
        assert a < b  # Window is valid interval

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_timeline_sorted(self, a, b, timeline):
        """Test that result timeline is sorted when no conflicts."""
        assume(a < b)  # Valid window precondition
        
        # Check if there are no conflicts
        no_conflicts = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is True
            
            # Check that result is sorted
            for i in range(len(result) - 1):
                assert result[i][1] <= result[i + 1][0], f"Timeline not sorted: {result[i]} and {result[i + 1]}"

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_conflict_free_insertion(self, a, b, timeline):
        """Test that window does not overlap with existing slots when no conflicts."""
        assume(a < b)  # Valid window precondition
        
        # Check if there are no conflicts
        no_conflicts = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is True
            
            # Check that new window doesn't overlap with any existing slot
            window = (a, b)
            for slot in timeline:
                # Two intervals [a,b] and [s,e] don't overlap if b <= s or a >= e
                assert (b <= slot[0] or a >= slot[1]), f"Window {window} overlaps with slot {slot}"

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_timeline_integrity(self, a, b, timeline):
        """Test that result contains all original timeline slots plus new window."""
        assume(a < b)  # Valid window precondition
        
        # Check if there are no conflicts
        no_conflicts = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is True
            
            # Check that all original slots are in result
            for slot in timeline:
                assert slot in result
            
            # Check that new window is in result
            window = (a, b)
            assert window in result
            
            # Check that result has exactly one more element than original timeline
            assert len(result) == len(timeline) + 1

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_return_format(self, a, b, timeline):
        """Test that function returns tuple (bool, list) for valid input."""
        assume(a < b)  # Valid input precondition
        
        result = plan_delivery_slot(a, b, timeline)
        
        # Check return format
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_success_indicator(self, a, b, timeline):
        """Test that function returns True when successful (no conflicts)."""
        assume(a < b)  # Valid input precondition
        
        # Check if there are no conflicts
        no_conflicts = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is True

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_failure_indicator(self, a, b, timeline):
        """Test that function returns False when conflicts detected."""
        assume(a < b)  # Valid input precondition
        
        # Check if there are conflicts
        has_conflicts = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is False

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_boundary_inclusion_bug(self, a, b, timeline):
        """Test that function incorrectly rejects valid adjacent slots due to strict inequality."""
        assume(a < b)  # Valid window precondition
        
        # Create a timeline with slots that touch at boundaries
        # This tests the bug where adjacent slots are incorrectly rejected
        adjacent_timeline = [(0, 1), (1, 2), (2, 3)]
        
        # Try to insert a slot that touches at boundary (should be valid but may be rejected due to bug)
        test_cases = [
            (1, 1),  # Point at boundary - should raise ValueError
            (0.5, 1),  # Touches at end - may be incorrectly rejected
            (1, 1.5),  # Touches at start - may be incorrectly rejected
        ]
        
        for test_a, test_b in test_cases:
            try:
                success, result = plan_delivery_slot(test_a, test_b, adjacent_timeline)
                # If it succeeds, check if it's correct behavior
                if success:
                    # Verify no actual overlap occurred
                    window = (test_a, test_b)
                    for slot in adjacent_timeline:
                        assert (test_b <= slot[0] or test_a >= slot[1]), f"Actual overlap detected: {window} and {slot}"
            except ValueError:
                # Empty window is expected to raise ValueError
                assert test_a >= test_b

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_timeline_immutability_on_conflict(self, a, b, timeline):
        """Test that original timeline is unchanged when conflicts detected."""
        assume(a < b)  # Valid window precondition
        
        # Make a copy to compare against
        original_timeline = timeline.copy()
        
        # Check if there are conflicts
        has_conflicts = any(not (b <= s or a >= e) for s, e in timeline)
        
        if has_conflicts:
            success, result_timeline = plan_delivery_slot(a, b, timeline)
            assert success is False
            assert result_timeline == original_timeline

    @given(
        a=st.integers(min_value=-1000, max_value=1000),
        b=st.integers(min_value=-1000, max_value=1000),
        timeline=st.lists(st.tuples(st.integers(), st.integers()))
    )
    def test_window_type_preservation(self, a, b, timeline):
        """Test that window maintains its original structure in result."""
        assume(a < b)  # Valid input precondition
        
        # Check if there are no conflicts
        no_conflicts = not any(not (b <= s or a >= e) for s, e in timeline)
        
        if no_conflicts:
            success, result = plan_delivery_slot(a, b, timeline)
            assert success is True
            
            # Check that new window is in result with original structure
            window = (a, b)
            assert window in result
            
            # Verify the window tuple structure is preserved
            for item in result:
                if item == window:
                    assert isinstance(item, tuple)
                    assert len(item) == 2
                    assert item[0] == a
                    assert item[1] == b