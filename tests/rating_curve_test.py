"""
Hypothesis tests for the rating_curve function semantic properties.

This test file exercises all semantic properties identified in 
properties/rating_curve_properties.json using the Hypothesis testing framework.
"""

import math
from hypothesis import given, assume, strategies as st
import pytest

# Import the function under test
from dataset.python_programs.rating_curve import rating_curve


class TestRatingCurveProperties:
    """Test class for rating_curve semantic properties."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_zero_length_error(self, x0, y0, y1, x):
        """
        Test zero_length_error property: rating_curve(x0, y0, x0, y1, x) raises ValueError
        """
        with pytest.raises(ValueError, match="zero length"):
            rating_curve(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_y_range_clamping(self, x0, y0, x1, y1, x):
        """
        Test y_range_clamping property: clamp implies min(y0, y1) <= y <= max(y0, y1)
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Test with clamp=True (default)
        y = rating_curve(x0, y0, x1, y1, x, clamp=True)
        low, high = sorted([y0, y1])
        assert low <= y <= high, f"Clamped value {y} not in range [{low}, {high}]"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """
        Test linear_interpolation property: y = (1 - t) * y0 + t * y1 where t = (x - x0) / (x1 - x0)
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Calculate expected value using the formal definition
        t = (x - x0) / (x1 - x0)
        expected_y = (1 - t) * y0 + t * y1
        
        # Get actual result
        actual_y = rating_curve(x0, y0, x1, y1, x, clamp=False)
        
        # Use math.isclose for floating point comparison
        assert math.isclose(actual_y, expected_y, rel_tol=1e-9, abs_tol=1e-9), \
            f"Linear interpolation failed: expected {expected_y}, got {actual_y}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_endpoint_interpolation(self, x0, y0, x1, y1):
        """
        Test endpoint_interpolation property: rating_curve(x0, y0, x1, y1, x0) == y0 
        and rating_curve(x0, y0, x1, y1, x1) == y1
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Test interpolation at x0
        y_at_x0 = rating_curve(x0, y0, x1, y1, x0, clamp=False)
        assert math.isclose(y_at_x0, y0, rel_tol=1e-9, abs_tol=1e-9), \
            f"Endpoint interpolation at x0 failed: expected {y0}, got {y_at_x0}"
        
        # Test interpolation at x1
        y_at_x1 = rating_curve(x0, y0, x1, y1, x1, clamp=False)
        assert math.isclose(y_at_x1, y1, rel_tol=1e-9, abs_tol=1e-9), \
            f"Endpoint interpolation at x1 failed: expected {y1}, got {y_at_x1}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        x_prime=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_scaling(self, x0, y0, x1, y1, x, x_prime):
        """
        Test linear_scaling property: rating_curve(x0, y0, x1, y1, x) is linear in x
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Test linearity: f(ax + b) = a*f(x) + b*f(1) - b*f(0) + f(0)
        # For simplicity, test that the function is affine (linear + constant)
        y_x = rating_curve(x0, y0, x1, y1, x, clamp=False)
        y_x_prime = rating_curve(x0, y0, x1, y1, x_prime, clamp=False)
        
        # For a linear function, the slope between any two points should be constant
        if x != x_prime:
            slope = (y_x_prime - y_x) / (x_prime - x)
            # The slope should be constant regardless of which points we choose
            # We can't easily test this with just two points, so we verify the mathematical
            # definition holds by checking it matches the expected linear interpolation
            t = (x - x0) / (x1 - x0)
            expected_y = (1 - t) * y0 + t * y1
            assert math.isclose(y_x, expected_y, rel_tol=1e-9, abs_tol=1e-9)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_parameter_symmetry(self, x0, y0, x1, y1, x):
        """
        Test parameter_symmetry property: rating_curve(x0, y0, x1, y1, x) == rating_curve(x1, y1, x0, y0, x)
        """
        assume(x1 != x0)  # Avoid zero length case
        
        y1 = rating_curve(x0, y0, x1, y1, x, clamp=False)
        y2 = rating_curve(x1, y1, x0, y0, x, clamp=False)
        
        assert math.isclose(y1, y2, rel_tol=1e-9, abs_tol=1e-9), \
            f"Parameter symmetry failed: rating_curve({x0}, {y0}, {x1}, {y1}, {x}) = {y1}, " \
            f"rating_curve({x1}, {y1}, {x0}, {y0}, {x}) = {y2}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_zero_length_detection(self, x0, y0, y1, x):
        """
        Test zero_length_detection property: raises ValueError("zero length")
        """
        with pytest.raises(ValueError, match="zero length"):
            rating_curve(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_idempotence(self, x0, y0, x1, y1, x):
        """
        Test clamp_idempotence property: clamp implies rating_curve(x0, y0, x1, y1, x) == clamp(rating_curve(x0, y0, x1, y1, x))
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Get the clamped result
        clamped_y = rating_curve(x0, y0, x1, y1, x, clamp=True)
        
        # Apply clamping again (simulate re-clamping)
        low, high = sorted([y0, y1])
        re_clamped_y = min(max(clamped_y, low), high)
        
        assert math.isclose(clamped_y, re_clamped_y, rel_tol=1e-9, abs_tol=1e-9), \
            f"Clamp idempotence failed: {clamped_y} != {re_clamped_y}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        x_prime=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, x0, y0, x1, y1, x, x_prime):
        """
        Test monotonicity_preservation property: x <= x' implies rating_curve(x0, y0, x1, y1, x) <= rating_curve(x0, y0, x1, y1, x')
        """
        assume(x1 != x0)  # Avoid zero length case
        assume(y0 <= y1)  # Precondition for monotonicity
        assume(x <= x_prime)  # Precondition x <= x'
        
        y = rating_curve(x0, y0, x1, y1, x, clamp=False)
        y_prime = rating_curve(x0, y0, x1, y1, x_prime, clamp=False)
        
        assert y <= y_prime, \
            f"Monotonicity preservation failed: x={x} <= x'={x_prime} but y={y} > y'={y_prime}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        a=st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100),
        b=st.floats(allow_nan=False, allow_infinity=False, min_value=-100, max_value=100)
    )
    def test_affine_invariance(self, x0, y0, x1, y1, x, a, b):
        """
        Test affine_invariance property: rating_curve(x0, a*y0 + b, x1, a*y1 + b, x) == a * rating_curve(x0, y0, x1, y1, x) + b
        """
        assume(x1 != x0)  # Avoid zero length case
        assume(a != 0)  # Avoid degenerate cases
        
        # Calculate left side: rating_curve with transformed y values
        left_side = rating_curve(x0, a*y0 + b, x1, a*y1 + b, x, clamp=False)
        
        # Calculate right side: transform the result
        original_y = rating_curve(x0, y0, x1, y1, x, clamp=False)
        right_side = a * original_y + b
        
        assert math.isclose(left_side, right_side, rel_tol=1e-6, abs_tol=1e-6), \
            f"Affine invariance failed: left={left_side}, right={right_side}"


class TestRatingCurveEdgeCases:
    """Test edge cases and additional properties not covered in the main semantic properties."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_vs_no_clamp_difference(self, x0, y0, x1, y1, x):
        """
        Test that clamping can produce different results from non-clamping when extrapolation occurs.
        """
        assume(x1 != x0)  # Avoid zero length case
        
        clamped_y = rating_curve(x0, y0, x1, y1, x, clamp=True)
        unclamped_y = rating_curve(x0, y0, x1, y1, x, clamp=False)
        
        # When x is outside [x0, x1], clamping should constrain the result
        if x < min(x0, x1) or x > max(x0, x1):
            low, high = sorted([y0, y1])
            assert low <= clamped_y <= high, \
                f"Clamped value {clamped_y} not in range [{low}, {high}] for extrapolation"
        
        # When x is between x0 and x1, both should give the same result
        if min(x0, x1) <= x <= max(x0, x1):
            assert math.isclose(clamped_y, unclamped_y, rel_tol=1e-9, abs_tol=1e-9), \
                f"Clamped and unclamped should be equal for interpolation: {clamped_y} != {unclamped_y}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_default_clamp_behavior(self, x0, y0, x1, y1, x):
        """
        Test that the default clamp=True behavior works as expected.
        """
        assume(x1 != x0)  # Avoid zero length case
        
        # Default behavior should be the same as explicitly setting clamp=True
        default_y = rating_curve(x0, y0, x1, y1, x)
        explicit_clamp_y = rating_curve(x0, y0, x1, y1, x, clamp=True)
        
        assert math.isclose(default_y, explicit_clamp_y, rel_tol=1e-9, abs_tol=1e-9), \
            f"Default clamp behavior differs from explicit clamp=True: {default_y} != {explicit_clamp_y}"


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])