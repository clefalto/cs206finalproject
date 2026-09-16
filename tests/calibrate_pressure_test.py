"""
Hypothesis tests for calibrate_pressure function semantic properties.

This test file exercises all semantic properties identified in
properties/calibrate_pressure_properties.json using the Hypothesis
testing framework for property-based testing.
"""

import pytest
import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import math

# Import the function under test
from dataset.python_programs.calibrate_pressure import calibrate_pressure


class TestCalibratePressureProperties:
    """Test class for calibrate_pressure semantic properties."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_zero_length_error(self, x0, y0, y1, x):
        """
        Test zero_length_error property:
        calibrate_pressure(x0, y0, x0, y1, x) raises ValueError('zero length')
        """
        with pytest.raises(ValueError, match="zero length"):
            calibrate_pressure(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_output_clamped_to_y_range(self, x0, y0, x1, y1, x):
        """
        Test output_clamped_to_y_range property:
        if clamp: min(y0, y1) <= y <= max(y0, y1)
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=True)
        low, high = sorted([y0, y1])
        
        assert low <= result <= high, f"Result {result} not in range [{low}, {high}]"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_interpolation_at_x0(self, x0, y0, x1, y1):
        """
        Test interpolation_at_x0 property:
        calibrate_pressure(x0, y0, x1, y1, x0) == y0
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x0)
        assert result == y0, f"Expected {y0}, got {result}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_interpolation_at_x1(self, x0, y0, x1, y1):
        """
        Test interpolation_at_x1 property:
        calibrate_pressure(x0, y0, x1, y1, x1) == y1
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x1)
        assert result == y1, f"Expected {y1}, got {result}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation_between_bounds(self, x0, y0, x1, y1, x):
        """
        Test linear_interpolation_between_bounds property:
        y is linear interpolation between y0 and y1
        """
        assume(x1 != x0)  # Avoid zero length error
        assume(x0 < x < x1)  # Test specifically for x0 < x < x1 case
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        
        # Calculate expected linear interpolation
        t = (x - x0) / (x1 - x0)
        expected = (1 - t) * y0 + t * y1
        
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """
        Test linear_interpolation property:
        y = (1 - t) * y0 + t * y1 where t = (x - x0) / (x1 - x0)
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        
        # Calculate expected linear interpolation
        t = (x - x0) / (x1 - x0)
        expected = (1 - t) * y0 + t * y1
        
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_boundary_preservation(self, x0, y0, x1, y1):
        """
        Test boundary_preservation property:
        calibrate_pressure(x0, y0, x1, y1, x0) == y0 and calibrate_pressure(x0, y0, x1, y1, x1) == y1
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result_x0 = calibrate_pressure(x0, y0, x1, y1, x0, clamp=False)
        result_x1 = calibrate_pressure(x0, y0, x1, y1, x1, clamp=False)
        
        assert result_x0 == y0, f"Expected {y0} at x0, got {result_x0}"
        assert result_x1 == y1, f"Expected {y1} at x1, got {result_x1}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x_a=st.floats(allow_nan=False, allow_infinity=False),
        x_b=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, x0, y0, x1, y1, x_a, x_b):
        """
        Test monotonicity_preservation property:
        if x_a <= x_b then calibrate_pressure(x0, y0, x1, y1, x_a) <= calibrate_pressure(x0, y0, x1, y1, x_b)
        """
        assume(x1 != x0)  # Avoid zero length error
        assume(y0 <= y1)  # Precondition: y0 <= y1
        assume(x_a <= x_b)  # Precondition: x_a <= x_b
        
        result_a = calibrate_pressure(x0, y0, x1, y1, x_a, clamp=False)
        result_b = calibrate_pressure(x0, y0, x1, y1, x_b, clamp=False)
        
        assert result_a <= result_b, f"Monotonicity violated: {result_a} > {result_b} for x_a={x_a} <= x_b={x_b}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_zero_length_detection(self, x0, y0, y1, x):
        """
        Test zero_length_detection property:
        raises ValueError('zero length')
        """
        with pytest.raises(ValueError, match="zero length"):
            calibrate_pressure(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_output_range(self, x0, y0, x1, y1, x):
        """
        Test clamp_output_range property:
        min(y0, y1) <= calibrate_pressure(x0, y0, x1, y1, x, clamp=True) <= max(y0, y1)
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=True)
        low, high = sorted([y0, y1])
        
        assert low <= result <= high, f"Result {result} not in range [{low}, {high}]"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_parameter_symmetry(self, x0, y0, x1, y1, x):
        """
        Test parameter_symmetry property:
        calibrate_pressure(x0, y0, x1, y1, x) == calibrate_pressure(x1, y1, x0, y0, x)
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result1 = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        result2 = calibrate_pressure(x1, y1, x0, y0, x, clamp=False)
        
        assert abs(result1 - result2) < 1e-10, f"Symmetry violated: {result1} != {result2}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        k=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False).filter(lambda x: x != 0)
    )
    def test_scale_invariance(self, x0, y0, x1, y1, x, k):
        """
        Test scale_invariance property:
        calibrate_pressure(k*x0, k*y0, k*x1, k*y1, k*x) == k*calibrate_pressure(x0, y0, x1, y1, x)
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result1 = calibrate_pressure(k * x0, k * y0, k * x1, k * y1, k * x, clamp=False)
        result2 = k * calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        
        assert abs(result1 - result2) < 1e-6, f"Scale invariance violated: {result1} != {result2}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        a=st.floats(allow_nan=False, allow_infinity=False),
        b=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_translation_invariance(self, x0, y0, x1, y1, x, a, b):
        """
        Test translation_invariance property:
        calibrate_pressure(x0+a, y0+b, x1+a, y1+b, x+a) == calibrate_pressure(x0, y0, x1, y1, x) + b
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result1 = calibrate_pressure(x0 + a, y0 + b, x1 + a, y1 + b, x + a, clamp=False)
        result2 = calibrate_pressure(x0, y0, x1, y1, x, clamp=False) + b
        
        assert abs(result1 - result2) < 1e-10, f"Translation invariance violated: {result1} != {result2}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_convex_combination(self, x0, y0, x1, y1, x):
        """
        Test convex_combination property:
        y is convex combination of y0 and y1 (t in [0,1])
        """
        assume(x1 != x0)  # Avoid zero length error
        assume(x0 <= x <= x1)  # Precondition: x0 <= x <= x1
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        
        # Calculate t parameter
        t = (x - x0) / (x1 - x0)
        
        # Check that t is in [0, 1]
        assert 0 <= t <= 1, f"t parameter {t} not in [0, 1]"
        
        # Check that result is convex combination
        expected = (1 - t) * y0 + t * y1
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_bug(self, x0, y0, x1, y1, x):
        """
        Test clamp_bug property:
        output clamped to [min(y0,y1), max(y0,y1)] regardless of x bounds
        """
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=True)
        low, high = sorted([y0, y1])
        
        # This test verifies the bug: output is clamped to y-range regardless of x bounds
        assert low <= result <= high, f"Result {result} not in range [{low}, {high}]"
        
        # Additional check: even when x is outside [x0, x1], clamping still uses y-range
        if x < min(x0, x1) or x > max(x0, x1):
            # Without clamping, result would be outside [y0, y1] for extrapolation
            # But with clamping, it's forced into [min(y0,y1), max(y0,y1)]
            unclamped_result = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
            if unclamped_result < low or unclamped_result > high:
                assert result == low or result == high, f"Clamping bug: {result} should be at boundary"


# Additional edge case tests
class TestCalibratePressureEdgeCases:
    """Additional tests for edge cases and boundary conditions."""

    @example(x0=0.0, y0=0.0, x1=1.0, y1=1.0, x=0.5)
    @example(x0=-1.0, y0=-1.0, x1=1.0, y1=1.0, x=0.0)
    @given(
        x0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y0=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_interpolation_accuracy(self, x0, y0, x1, y1, x):
        """Test interpolation accuracy with specific examples and random values."""
        assume(x1 != x0)  # Avoid zero length error
        
        result = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        
        # Calculate expected result using the exact formula
        t = (x - x0) / (x1 - x0)
        expected = (1 - t) * y0 + t * y1
        
        # Use relative tolerance for floating point comparison
        if expected == 0:
            assert abs(result) < 1e-10, f"Expected 0, got {result}"
        else:
            relative_error = abs(result - expected) / abs(expected)
            assert relative_error < 1e-9, f"Relative error too large: {relative_error}"

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_no_clamp_vs_clamp_difference(self, x0, y0, x1, y1, x):
        """Test that clamp=True and clamp=False can produce different results."""
        assume(x1 != x0)  # Avoid zero length error
        
        unclamped = calibrate_pressure(x0, y0, x1, y1, x, clamp=False)
        clamped = calibrate_pressure(x0, y0, x1, y1, x, clamp=True)
        
        low, high = sorted([y0, y1])
        
        # Clamped result should always be in range
        assert low <= clamped <= high
        
        # If unclamped result is outside range, clamped should be different
        if unclamped < low or unclamped > high:
            assert clamped != unclamped, f"Clamping should have changed result: {clamped}"
        else:
            # If unclamped is already in range, results should be the same
            assert abs(clamped - unclamped) < 1e-10, f"Results should be equal when in range: {clamped} != {unclamped}"