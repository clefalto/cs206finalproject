import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, tuples, floats, integers

# Import the function under test
from dataset.python_programs.time_range_filter import time_range_filter


class TestTimeRangeFilter:
    """Test suite for time_range_filter function using Hypothesis."""

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_invalid_range_error(self, points, start, end):
        """Test that ValueError is raised when start >= end."""
        assume(start >= end)
        
        with pytest.raises(ValueError, match="invalid range"):
            time_range_filter(points, start, end)

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_inclusive_range_filter(self, points, start, end):
        """Test that the function returns points within [start, end] range."""
        assume(start < end)
        
        result = time_range_filter(points, start, end)
        expected = [p for p in points if start <= p[0] <= end]
        
        assert result == expected

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_order_preservation(self, points, start, end):
        """Test that the function preserves the order of points."""
        assume(start < end)
        
        result = time_range_filter(points, start, end)
        
        # Check that the order is preserved by comparing indices
        if result:
            original_indices = [points.index(p) for p in result]
            assert original_indices == sorted(original_indices)

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_subset_property(self, points, start, end):
        """Test that all returned points are from the original input."""
        assume(start < end)
        
        result = time_range_filter(points, start, end)
        
        # All points in result should be in the original points list
        for point in result:
            assert point in points

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_boundary_inclusion(self, points, start, end):
        """Test that all returned points satisfy start <= timestamp <= end."""
        assume(start < end)
        
        result = time_range_filter(points, start, end)
        
        # All points should be within the boundary
        for timestamp, value in result:
            assert start <= timestamp <= end

    @given(
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_empty_input_identity(self, start, end):
        """Test that filtering an empty list returns an empty list."""
        assume(start < end)
        
        result = time_range_filter([], start, end)
        
        assert result == []

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_no_out_of_range_points(self, points, start, end):
        """Test that no points outside the range are included."""
        assume(start < end)
        
        result = time_range_filter(points, start, end)
        
        # No points should be outside the range
        for timestamp, value in result:
            assert not (timestamp < start or timestamp > end)

    @given(
        points=lists(tuples(floats(allow_nan=False, allow_infinity=False), floats())),
        start=floats(allow_nan=False, allow_infinity=False),
        end=floats(allow_nan=False, allow_infinity=False)
    )
    def test_idempotence(self, points, start, end):
        """Test that applying the filter twice gives the same result."""
        assume(start < end)
        
        first_result = time_range_filter(points, start, end)
        second_result = time_range_filter(first_result, start, end)
        
        assert first_result == second_result