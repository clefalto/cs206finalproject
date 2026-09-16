import pytest
import hypothesis.strategies as st
from hypothesis import given, assume, example
import math

def model_confidence_clamp(x0, y0, x1, y1, x, clamp=True):
    """
    Linear interpolation with optional clamping.
    
    Args:
        x0, y0: First point
        x1, y1: Second point  
        x: Input value to interpolate at
        clamp: Whether to clamp output to [min(y0,y1), max(y0,y1)]
    
    Returns:
        Interpolated value y
    """
    if x0 == x1:
        raise ValueError("degenerate segment")
    
    # Linear interpolation
    y = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
    
    # Optional clamping
    if clamp:
        y = min(max(y, min(y0, y1)), max(y0, y1))
    
    return y


class TestModelConfidenceClamp:
    """Test suite for model_confidence_clamp function using Hypothesis."""

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_degenerate_segment_error(self, x0, y0, x1, y1, x):
        """Test that degenerate segments (x0 == x1) raise ValueError."""
        assume(x0 == x1)
        with pytest.raises(ValueError, match="degenerate segment"):
            model_confidence_clamp(x0, y0, x1, y1, x)

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_output_clamping(self, x0, y0, x1, y1, x):
        """Test that clamping works correctly when enabled."""
        assume(x0 != x1)
        
        # Test with clamping enabled (default)
        y_clamped = model_confidence_clamp(x0, y0, x1, y1, x, clamp=True)
        
        # Calculate expected clamped value
        y_unclamped = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        expected_clamped = min(max(y_unclamped, min(y0, y1)), max(y0, y1))
        
        # Allow for floating point precision issues
        assert abs(y_clamped - expected_clamped) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """Test that linear interpolation formula is correct."""
        assume(x0 != x1)
        
        y = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        expected = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        
        # Allow for floating point precision issues
        assert abs(y - expected) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_boundary_preservation(self, x0, y0, x1, y1, x):
        """Test that clamped output stays within y0-y1 bounds."""
        assume(x0 != x1)
        
        y = model_confidence_clamp(x0, y0, x1, y1, x, clamp=True)
        lower_bound = min(y0, y1)
        upper_bound = max(y0, y1)
        
        assert lower_bound <= y <= upper_bound

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_endpoint_identity(self, x0, y0, x1, y1):
        """Test that endpoints map to themselves."""
        assume(x0 != x1)
        
        # Test x0 maps to y0
        y_at_x0 = model_confidence_clamp(x0, y0, x1, y1, x0, clamp=False)
        assert abs(y_at_x0 - y0) < 1e-10
        
        # Test x1 maps to y1
        y_at_x1 = model_confidence_clamp(x0, y0, x1, y1, x1, clamp=False)
        assert abs(y_at_x1 - y1) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x_a=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x_b=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity(self, x0, y0, x1, y1, x_a, x_b):
        """Test that function is monotonic when y0 <= y1."""
        assume(x0 != x1)
        assume(y0 <= y1)
        assume(x0 <= x_a <= x1)
        assume(x0 <= x_b <= x1)
        assume(x_a <= x_b)
        
        y_a = model_confidence_clamp(x0, y0, x1, y1, x_a, clamp=False)
        y_b = model_confidence_clamp(x0, y0, x1, y1, x_b, clamp=False)
        
        assert y_a <= y_b

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        a=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        b=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_affine_invariance(self, x0, y0, x1, y1, x, a, b):
        """Test that function is invariant under affine transformations."""
        assume(x0 != x1)
        assume(a != 0)  # Avoid degenerate affine transformation
        
        def f(z):
            return a * z + b
        
        # Apply affine transformation to y values
        y0_transformed = f(y0)
        y1_transformed = f(y1)
        
        # Interpolate with transformed values
        y_transformed = model_confidence_clamp(x0, y0_transformed, x1, y1_transformed, x, clamp=False)
        
        # Interpolate with original values, then transform
        y_original = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        y_expected = f(y_original)
        
        assert abs(y_transformed - y_expected) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        c=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, x0, y0, x1, y1, x, c):
        """Test that function is invariant under uniform scaling."""
        assume(x0 != x1)
        assume(c != 0)
        
        # Scale all coordinates
        y_scaled = model_confidence_clamp(c * x0, c * y0, c * x1, c * y1, c * x, clamp=False)
        
        # Scale the result of original interpolation
        y_original = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        y_expected = c * y_original
        
        assert abs(y_scaled - y_expected) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        dx=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        dy=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_translation_invariance(self, x0, y0, x1, y1, x, dx, dy):
        """Test that function is invariant under translation."""
        assume(x0 != x1)
        
        # Translate all coordinates
        y_translated = model_confidence_clamp(x0 + dx, y0 + dy, x1 + dx, y1 + dy, x + dx, clamp=False)
        
        # Translate the result of original interpolation
        y_original = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        y_expected = y_original + dy
        
        assert abs(y_translated - y_expected) < 1e-10

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_convex_combination(self, x0, y0, x1, y1, x):
        """Test that interpolation produces convex combinations when x is between x0 and x1."""
        assume(x0 != x1)
        assume(x0 <= x <= x1)
        
        y = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        
        # Calculate the interpolation parameter t
        t = (x - x0) / (x1 - x0)
        
        # Check that y is a convex combination: y = (1-t)*y0 + t*y1
        expected = (1 - t) * y0 + t * y1
        
        assert abs(y - expected) < 1e-10
        assert 0 <= t <= 1

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_error_on_degenerate(self, x0, y0, x1, y1, x):
        """Test that degenerate segments always raise ValueError."""
        assume(x0 == x1)
        with pytest.raises(ValueError, match="degenerate segment"):
            model_confidence_clamp(x0, y0, x1, y1, x)

    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_clamp_idempotence(self, x0, y0, x1, y1, x):
        """Test that clamping is idempotent when output is already in bounds."""
        assume(x0 != x1)
        
        # Calculate the unclamped result
        y_unclamped = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        lower_bound = min(y0, y1)
        upper_bound = max(y0, y1)
        
        # Only test when the unclamped result is already in bounds
        assume(lower_bound <= y_unclamped <= upper_bound)
        
        # Compare clamped vs unclamped results
        y_clamped = model_confidence_clamp(x0, y0, x1, y1, x, clamp=True)
        y_unclamped_direct = model_confidence_clamp(x0, y0, x1, y1, x, clamp=False)
        
        assert abs(y_clamped - y_unclamped_direct) < 1e-10