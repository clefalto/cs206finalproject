import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import lists, tuples, integers
import sys
import os

# Add the parent directory to the path to import the function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset.python_programs import reservation_overlap_check


class TestReservationOverlapCheck:
    """Test suite for reservation_overlap_check function using Hypothesis."""

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_invalid_reservation_detection(self, reservations, candidate):
        """Test that ValueError is raised when c_start >= c_end."""
        c_start, c_end = candidate
        assume(c_start >= c_end)  # Precondition for this property
        
        with pytest.raises(ValueError, match="Invalid reservation"):
            reservation_overlap_check(reservations, candidate)

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_boundary_touch_overlap_detection(self, reservations, candidate):
        """Test that overlap is detected when candidate touches boundary of existing reservation."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        # Find a reservation that the candidate touches at boundary
        for start, end in reservations:
            assume(start < end)  # Valid existing reservation
            if c_end == start or c_start == end:
                # Candidate touches boundary, should detect overlap
                result = reservation_overlap_check(reservations, candidate)
                assert result is True, f"Expected overlap detected for boundary touch: {candidate} with {reservations}"
                return
        
        # If no boundary touch found, test should pass without assertion
        # This is handled by the assume statements above

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_valid_reservation_validation(self, reservations, candidate):
        """Test that no ValueError is raised when c_start < c_end."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Precondition for this property
        
        # Should not raise ValueError for valid reservation
        try:
            result = reservation_overlap_check(reservations, candidate)
            # Result should be boolean (True or False)
            assert isinstance(result, bool)
        except ValueError:
            pytest.fail("ValueError raised for valid reservation")

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_no_overlap_return(self, reservations, candidate):
        """Test that False is returned when no reservations overlap with candidate."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        # Filter out invalid reservations and check if any overlap
        valid_reservations = [(start, end) for start, end in reservations if start < end]
        
        # Check if no overlap exists
        no_overlap = all(
            c_end <= start or c_start >= end 
            for start, end in valid_reservations
        )
        
        if no_overlap:
            result = reservation_overlap_check(valid_reservations, candidate)
            assert result is False, f"Expected no overlap for {candidate} with {valid_reservations}"

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_overlap_detection(self, reservations, candidate):
        """Test that True is returned when at least one reservation overlaps with candidate."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        # Filter out invalid reservations
        valid_reservations = [(start, end) for start, end in reservations if start < end]
        
        # Check if overlap exists
        has_overlap = any(
            not (c_end <= start or c_start >= end)
            for start, end in valid_reservations
        )
        
        if has_overlap:
            result = reservation_overlap_check(valid_reservations, candidate)
            assert result is True, f"Expected overlap detected for {candidate} with {valid_reservations}"

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=1000)
    def test_boundary_touch_considered_overlap(self, reservations, candidate):
        """Test that boundary touch is considered overlap."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        # Filter out invalid reservations
        valid_reservations = [(start, end) for start, end in reservations if start < end]
        
        # Check if candidate touches boundary of any existing reservation
        touches_boundary = any(
            c_end == start or c_start == end
            for start, end in valid_reservations
        )
        
        if touches_boundary:
            result = reservation_overlap_check(valid_reservations, candidate)
            assert result is True, f"Expected boundary touch to be considered overlap for {candidate} with {valid_reservations}"

    @given(
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=100)
    def test_empty_reservations_no_overlap(self, candidate):
        """Test that False is returned when reservations list is empty."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        result = reservation_overlap_check([], candidate)
        assert result is False, f"Expected no overlap for empty reservations with candidate {candidate}"

    @given(
        reservations=lists(tuples(integers(), integers())),
        candidate=tuples(integers(), integers())
    )
    @settings(max_examples=500)
    def test_deterministic_behavior(self, reservations, candidate):
        """Test that function returns same result for identical inputs."""
        c_start, c_end = candidate
        assume(c_start < c_end)  # Valid reservation
        
        # Filter out invalid reservations
        valid_reservations = [(start, end) for start, end in reservations if start < end]
        
        # Call function twice with same inputs
        result1 = reservation_overlap_check(valid_reservations, candidate)
        result2 = reservation_overlap_check(valid_reservations, candidate)
        
        assert result1 == result2, f"Function not deterministic: {result1} != {result2}"
        assert isinstance(result1, bool), f"Result should be boolean, got {type(result1)}"
        assert isinstance(result2, bool), f"Result should be boolean, got {type(result2)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])