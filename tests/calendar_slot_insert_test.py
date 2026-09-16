import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, integers


def calendar_slot_insert(existing, slot):
    """
    Insert a new time slot into a list of existing slots.
    
    Args:
        existing: List of (start, end) tuples representing existing time slots
        slot: A (start, end) tuple representing the new time slot to insert
        
    Returns:
        tuple: (success: bool, updated_slots: list) where success indicates
               if the slot was inserted without overlap, and updated_slots
               is the resulting list of slots (sorted by start time)
               
    Raises:
        ValueError: If start >= end (invalid slot)
    """
    start, end = slot
    
    # Check for invalid slot
    if start >= end:
        raise ValueError("Invalid slot: start must be less than end")
    
    # Check for overlaps with existing slots
    for s, e in existing:
        if not (end <= s or start >= e):
            return False, list(existing)
    
    # Insert the new slot and return sorted result
    new_slots = list(existing)
    new_slots.append(slot)
    new_slots.sort(key=lambda x: x[0])  # Sort by start time
    return True, new_slots


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_invalid_slot_raises_error(existing, start, end):
    """Test that invalid slots (start >= end) raise ValueError"""
    assume(start >= end)
    
    with pytest.raises(ValueError, match="Invalid slot"):
        calendar_slot_insert(existing, (start, end))


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_validity_preservation(existing, start, end):
    """Test that valid slots (start < end) do not raise ValueError"""
    assume(start < end)
    
    # Should not raise an exception
    result = calendar_slot_insert(existing, (start, end))
    assert isinstance(result, tuple)
    assert len(result) == 2


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_overlap_detection(existing, start, end):
    """Test that overlapping slots return (False, original_list)"""
    assume(start < end)
    
    # Create an existing slot that will overlap with the new slot
    if existing:
        # Use an existing slot to create overlap
        s, e = existing[0]
        # Make sure there's overlap: not (end <= s or start >= e)
        assume(not (end <= s or start >= e))
        
        success, result = calendar_slot_insert(existing, (start, end))
        assert not success
        assert result == list(existing)
    else:
        # If no existing slots, we can't test overlap detection
        # This is a limitation of the test strategy
        pass


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_non_overlapping_insertion(existing, start, end):
    """Test that non-overlapping valid slots are inserted correctly"""
    assume(start < end)
    
    # Ensure no overlap with any existing slot
    assume(not any(not (end <= s or start >= e) for s, e in existing))
    
    success, result = calendar_slot_insert(existing, (start, end))
    
    assert success
    expected = sorted(existing + [(start, end)])
    assert result == expected


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_sorted_output(existing, start, end):
    """Test that the output list is always sorted by start time"""
    assume(start < end)
    
    try:
        success, result = calendar_slot_insert(existing, (start, end))
        # Check that result is sorted by start time
        assert all(result[i][0] <= result[i+1][0] for i in range(len(result)-1))
    except ValueError:
        # Invalid slots are expected to raise ValueError
        pass


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_immutability_preservation(existing, start, end):
    """Test that the original existing list is not modified"""
    assume(start < end)
    
    original_existing = list(existing)
    try:
        calendar_slot_insert(existing, (start, end))
        # Original list should be unchanged
        assert existing == original_existing
    except ValueError:
        # Invalid slots are expected to raise ValueError
        assert existing == original_existing


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_overlap_detection_correctness(existing, start, end):
    """Test that overlap detection is correct: returns False iff there's overlap"""
    assume(start < end)
    
    # Check if there's overlap with any existing slot
    has_overlap = any(not (end <= s or start >= e) for s, e in existing)
    
    success, result = calendar_slot_insert(existing, (start, end))
    
    if has_overlap:
        assert not success
        assert result == list(existing)
    else:
        assert success
        expected = sorted(existing + [(start, end)])
        assert result == expected


@given(
    start=integers(),
    end=integers()
)
def test_identity_on_empty(start, end):
    """Test that inserting into empty list returns the slot in a list"""
    assume(start < end)
    
    success, result = calendar_slot_insert([], (start, end))
    
    assert success
    assert result == [(start, end)]


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_monotonicity(existing, start, end):
    """Test that successful insertion increases list length by exactly 1"""
    assume(start < end)
    
    # Ensure no overlap with any existing slot
    assume(not any(not (end <= s or start >= e) for s, e in existing))
    
    success, result = calendar_slot_insert(existing, (start, end))
    
    assert success
    assert len(result) == len(existing) + 1


@given(
    existing=lists(tuples(integers(), integers())),
    start=integers(),
    end=integers()
)
def test_boundary_touching_overlap_bug(existing, start, end):
    """Test that touching endpoints are treated as overlap (boundary bug)"""
    assume(start < end)
    
    # Look for existing slots where touching would occur
    for s, e in existing:
        # Test case: new slot ends where existing starts (end == s)
        if end == s:
            success, result = calendar_slot_insert(existing, (start, end))
            assert not success
            assert result == list(existing)
        
        # Test case: new slot starts where existing ends (start == e)
        if start == e:
            success, result = calendar_slot_insert(existing, (start, end))
            assert not success
            assert result == list(existing)