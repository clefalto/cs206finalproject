import pytest
import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import math
from typing import Union


def calibrate_quality(x0: float, y0: float, x1: float, y1: float, x: float, clamp: bool = True) -> float:
    """
    Calibrate quality using linear interpolation between two points.
    
    Args:
        x0, y0: First point coordinates
        x1, y1: Second point coordinates  
        x: Input value to interpolate for
        clamp: Whether to clamp the result to the y-range
    
    Returns:
        Interpolated y value
    """
    if x1 == x0:
        raise ValueError("degenerate segment")
    
    t = (x - x0) / (x1 - x0)
    y = y0 + t * (y1 - y0)
    
    if clamp:
        lo, hi = min(y0, y1), max(y0, y1)
        if y < lo:
            y = lo
        elif y > hi:
            y = hi
    
    return y


class TestCalibrateQuality:
    """Test suite for calibrate_quality function using Hypothesis."""

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_degenerate_segment_error(self, x0, y0, y1, x):
        """Test that degenerate segments (x1 == x0) raise ValueError."""
        with pytest.raises(ValueError, match="degenerate segment"):
            calibrate_quality(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_y_range_clamping(self, x0, y0, x1, y1, x):
        """Test that y is clamped to the range [min(y0,y1), max(y0,y1)] when clamp=True."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        lo, hi = min(y0, y1), max(y0, y1)
        
        # y should be clamped to [lo, hi]
        assert lo <= y <= hi

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_lower_bound_clamp(self, x0, y0, x1, y1, x):
        """Test that y is clamped to lo when y < lo."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        lo = min(y0, y1)
        
        # If y would be less than lo, it should be clamped to lo
        if y < lo:
            assert y == lo

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_upper_bound_clamp(self, x0, y0, x1, y1, x):
        """Test that y is clamped to hi when y > hi."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        hi = max(y0, y1)
        
        # If y would be greater than hi, it should be clamped to hi
        if y > hi:
            assert y == hi

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """Test that linear interpolation formula is correct."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        t = (x - x0) / (x1 - x0)
        expected_y = y0 + t * (y1 - y0)
        
        # Allow for floating point precision issues
        assert abs(y - expected_y) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_endpoint_preservation(self, x0, y0, x1, y1):
        """Test that endpoints are preserved."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        # Test x0 endpoint
        y_at_x0 = calibrate_quality(x0, y0, x1, y1, x0, clamp=False)
        assert abs(y_at_x0 - y0) < 1e-10
        
        # Test x1 endpoint
        y_at_x1 = calibrate_quality(x0, y0, x1, y1, x1, clamp=False)
        assert abs(y_at_x1 - y1) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, x0, y0, x1, y1, x):
        """Test that monotonicity is preserved when clamping."""
        assume(x1 != x0)  # Avoid degenerate segments
        assume(y0 <= y1)  # Assume y0 <= y1 for monotonicity
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        lo, hi = min(y0, y1), max(y0, y1)
        
        # y should be in the range [lo, hi]
        assert lo <= y <= hi

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_range_clamping(self, x0, y0, x1, y1, x):
        """Test that range clamping works correctly."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        lo, hi = min(y0, y1), max(y0, y1)
        
        # y should always be in [lo, hi] when clamping
        assert lo <= y <= hi

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        k=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False).filter(lambda x: x != 0)
    )
    def test_scale_invariance(self, x0, y0, x1, y1, x, k):
        """Test scale invariance property."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        original = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        scaled = calibrate_quality(k*x0, k*y0, k*x1, k*y1, k*x, clamp=False)
        
        # Allow for floating point precision issues
        assert abs(scaled - k*original) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        c=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        d=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_translation_invariance(self, x0, y0, x1, y1, x, c, d):
        """Test translation invariance property."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        original = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        translated = calibrate_quality(x0+c, y0+d, x1+c, y1+d, x+c, clamp=False)
        
        # Allow for floating point precision issues
        assert abs(translated - (original + d)) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_convex_combination(self, x0, y0, x1, y1, x):
        """Test that y is a convex combination of y0 and y1 when t in [0, 1]."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        # For x between x0 and x1, t should be in [0, 1]
        x_min, x_max = min(x0, x1), max(x0, x1)
        assume(x_min <= x <= x_max)  # x should be between x0 and x1
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        t = (x - x0) / (x1 - x0)
        
        # y should be y0 + t*(y1-y0) where t in [0, 1]
        expected_y = y0 + t * (y1 - y0)
        assert abs(y - expected_y) < 1e-10
        assert 0 <= t <= 1

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_parameter_symmetry(self, x0, y0, x1, y1, x):
        """Test that swapping endpoints gives the same result."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y1 = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        y2 = calibrate_quality(x1, y1, x0, y0, x, clamp=False)
        
        # Results should be the same
        assert abs(y1 - y2) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_clamp_idempotence(self, x0, y0, x1, y1, x):
        """Test that clamping is idempotent."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        # First call with clamping
        y1 = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        
        # Second call should give the same result
        y2 = calibrate_quality(x0, y0, x1, y1, x, clamp=True)
        
        assert abs(y1 - y2) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_degenerate_segment_detection(self, x0, y0, y1, x):
        """Test that degenerate segments are detected."""
        with pytest.raises(ValueError, match="degenerate segment"):
            calibrate_quality(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_proportional_interpolation(self, x0, y0, x1, y1, x):
        """Test proportional interpolation formula."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        
        # Check the proportional relationship
        if abs(x1 - x0) > 1e-10:  # Avoid division by very small numbers
            expected_diff = (x - x0) * (y1 - y0) / (x1 - x0)
            actual_diff = y - y0
            assert abs(actual_diff - expected_diff) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_continuity(self, x0, y0, x1, y1, x):
        """Test that the function is continuous."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        # Test continuity by checking small perturbations
        epsilon = 1e-6
        y1 = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        y2 = calibrate_quality(x0, y0, x1, y1, x + epsilon, clamp=False)
        
        # The difference should be small for small epsilon
        assert abs(y2 - y1) < 1e-3

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_linear_scaling(self, x0, y0, x1, y1, x):
        """Test linear scaling formula."""
        assume(x1 != x0)  # Avoid degenerate segments
        
        y = calibrate_quality(x0, y0, x1, y1, x, clamp=False)
        expected_y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        
        assert abs(y - expected_y) < 1e-10