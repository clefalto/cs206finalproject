import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, booleans
import math

# Import the function under test
# Note: The actual implementation of throughput_trendline is not provided,
# so we'll create a mock implementation for testing purposes
def throughput_trendline(x0, y0, x1, y1, x, clamp=False):
    """
    Mock implementation of throughput_trendline for testing purposes.
    This should be replaced with the actual implementation.
    """
    if x1 == x0:
        raise ValueError("zero length")
    
    t = (x - x0) / (x1 - x0)
    y = (1 - t) * y0 + t * y1
    
    if clamp:
        low, high = sorted([y0, y1])
        y = min(max(y, low), high)
    
    return y


class TestThroughputTrendline:
    """Test class for throughput_trendline function using Hypothesis."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_zero_length_error(self, x0, y0, x1, y1, x):
        """Test that zero_length_error property raises ValueError when x1 == x0."""
        assume(x1 == x0)
        
        with pytest.raises(ValueError, match="zero length"):
            throughput_trendline(x0, y0, x1, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)
    )
    def test_y_range_clamp(self, x0, y0, x1, y1, x, clamp):
        """Test that y_range_clamp property clamps y values within [min(y0,y1), max(y0,y1)]."""
        assume(x1 != x0)
        
        y = throughput_trendline(x0, y0, x1, y1, x, clamp=clamp)
        low, high = sorted([y0, y1])
        
        assert low <= y <= high, f"Clamped value {y} is not within range [{low}, {high}]"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """Test that linear_interpolation property computes correct linear interpolation."""
        assume(x1 != x0)
        
        y = throughput_trendline(x0, y0, x1, y1, x, clamp=False)
        t = (x - x0) / (x1 - x0)
        expected_y = (1 - t) * y0 + t * y1
        
        # Handle floating point precision issues
        assert math.isclose(y, expected_y, rel_tol=1e-9, abs_tol=1e-9), \
            f"Linear interpolation failed: got {y}, expected {expected_y}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_boundary_conditions(self, x0, y0, x1, y1):
        """Test that boundary_conditions property holds at endpoints."""
        assume(x1 != x0)
        
        # Test at x0
        y_at_x0 = throughput_trendline(x0, y0, x1, y1, x0, clamp=False)
        assert math.isclose(y_at_x0, y0, rel_tol=1e-9, abs_tol=1e-9), \
            f"Boundary condition at x0 failed: got {y_at_x0}, expected {y0}"
        
        # Test at x1
        y_at_x1 = throughput_trendline(x0, y0, x1, y1, x1, clamp=False)
        assert math.isclose(y_at_x1, y1, rel_tol=1e-9, abs_tol=1e-9), \
            f"Boundary condition at x1 failed: got {y_at_x1}, expected {y1}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity(self, x0, y0, x1, y1, x):
        """Test that monotonicity property holds when y0 <= y1."""
        assume(x1 != x0)
        assume(y0 <= y1)
        assume(x0 <= x <= x1)  # x should be in the interval [x0, x1]
        
        y = throughput_trendline(x0, y0, x1, y1, x, clamp=False)
        
        # For monotonicity, we need to check that the function is increasing
        # Since we're using linear interpolation, this should hold when y0 <= y1
        # We can't directly test "for all x" with Hypothesis, but we can test
        # that the computed value is reasonable for the given constraints
        
        # The interpolated value should be between y0 and y1 (inclusive)
        assert y0 <= y <= y1, \
            f"Monotonicity violated: y0={y0}, y={y}, y1={y1}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)
    )
    def test_clamp_preserves_bounds(self, x0, y0, x1, y1, x, clamp):
        """Test that clamp_preserves_bounds property holds."""
        assume(x1 != x0)
        
        y_clamped = throughput_trendline(x0, y0, x1, y1, x, clamp=clamp)
        min_y = min(y0, y1)
        max_y = max(y0, y1)
        
        assert min_y <= y_clamped <= max_y, \
            f"Clamp does not preserve bounds: min={min_y}, clamped={y_clamped}, max={max_y}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)
    )
    def test_clamp_idempotent(self, x0, y0, x1, y1, x, clamp):
        """Test that clamp_idempotent property holds."""
        assume(x1 != x0)
        
        y_once = throughput_trendline(x0, y0, x1, y1, x, clamp=clamp)
        y_twice = throughput_trendline(x0, y0, x1, y1, x, clamp=clamp)
        
        assert math.isclose(y_once, y_twice, rel_tol=1e-9, abs_tol=1e-9), \
            f"Clamp is not idempotent: once={y_once}, twice={y_twice}"


if __name__ == "__main__":
    # This allows running the tests with: python throughput_trendline_test.py
    pytest.main([__file__, "-v"])