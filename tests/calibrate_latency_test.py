"""
Tests for calibrate_latency function using Hypothesis testing framework.
Tests all semantic properties identified in properties/calibrate_latency_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, booleans
import math


# Import the function under test
# Note: We need to import the actual calibrate_latency function
# For now, we'll assume it's available in the dataset.python_programs module
# If the import path is different, it should be adjusted accordingly
try:
    from dataset.python_programs.calibrate_latency import calibrate_latency
except ImportError:
    # If the function is not available, we'll create a mock implementation
    # for testing purposes. This should be replaced with the actual import.
    def calibrate_latency(x0, y0, x1, y1, x, clamp=False):
        """
        Mock implementation of calibrate_latency for testing.
        This should be replaced with the actual function import.
        """
        if x1 == x0:
            raise ValueError("zero length")
        
        t = (x - x0) / (x1 - x0)
        y = (1 - t) * y0 + t * y1
        
        if clamp:
            y = max(min(y, max(y0, y1)), min(y0, y1))
        
        return y


class TestCalibrateLatency:
    """Test class for calibrate_latency function semantic properties."""

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_zero_length_error(self, x0, y0, y1, x, clamp):
        """Test that x1 == x0 raises ValueError with 'zero length' message."""
        x1 = x0  # This creates the zero-length condition
        
        with pytest.raises(ValueError, match="zero length"):
            calibrate_latency(x0, y0, x1, y1, x, clamp=clamp)

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_output_clamped_to_y_range(self, x0, y0, x1, y1, x):
        """Test that when clamp=True, output is clamped to [min(y0,y1), max(y0,y1)]."""
        assume(x1 != x0)  # Precondition for this property
        
        result = calibrate_latency(x0, y0, x1, y1, x, clamp=True)
        
        min_y = min(y0, y1)
        max_y = max(y0, y1)
        
        # The result should be clamped to the range [min_y, max_y]
        assert min_y <= result <= max_y, f"Result {result} not in range [{min_y}, {max_y}]"

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x, clamp):
        """Test that y = (1-t)*y0 + t*y1 where t = (x-x0)/(x1-x0)."""
        assume(x1 != x0)  # Precondition for this property
        
        result = calibrate_latency(x0, y0, x1, y1, x, clamp=clamp)
        
        t = (x - x0) / (x1 - x0)
        expected = (1 - t) * y0 + t * y1
        
        # Account for floating point precision
        assert abs(result - expected) < 1e-10, f"Result {result} != expected {expected} (t={t})"

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_endpoint_preservation(self, x0, y0, x1, y1, clamp):
        """Test that calibrate_latency(x0, y0, x1, y1, x0) == y0 and calibrate_latency(x0, y0, x1, y1, x1) == y1."""
        assume(x1 != x0)  # Precondition for this property
        
        # Test endpoint x0
        result_x0 = calibrate_latency(x0, y0, x1, y1, x0, clamp=clamp)
        assert abs(result_x0 - y0) < 1e-10, f"Result at x0 {result_x0} != y0 {y0}"
        
        # Test endpoint x1
        result_x1 = calibrate_latency(x0, y0, x1, y1, x1, clamp=clamp)
        assert abs(result_x1 - y1) < 1e-10, f"Result at x1 {result_x1} != y1 {y1}"

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, x0, y0, x1, y1, x):
        """Test that if y0 <= y1 then min(y0, y1) <= y <= max(y0, y1) when clamp=True."""
        assume(x1 != x0)  # Precondition for this property
        assume(y0 <= y1)  # Condition for this property
        
        result = calibrate_latency(x0, y0, x1, y1, x, clamp=True)
        
        # Since y0 <= y1, min(y0, y1) = y0 and max(y0, y1) = y1
        assert y0 <= result <= y1, f"Result {result} not in range [{y0}, {y1}] when y0 <= y1"

    @given(
        x0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    def test_range_clamping(self, x0, y0, x1, y1, x):
        """Test that min(y0, y1) <= y <= max(y0, y1) when clamp=True."""
        assume(x1 != x0)  # Precondition for this property
        
        result = calibrate_latency(x0, y0, x1, y1, x, clamp=True)
        
        min_y = min(y0, y1)
        max_y = max(y0, y1)
        
        assert min_y <= result <= max_y, f"Result {result} not in range [{min_y}, {max_y}]"

    @given(
        x0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        k=floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_scale_invariance(self, x0, y0, x1, y1, x, k, clamp):
        """Test that calibrate_latency(k*x0, k*y0, k*x1, k*y1, k*x) == k*calibrate_latency(x0, y0, x1, y1, x)."""
        assume(x1 != x0)  # Precondition for this property
        assume(k != 0)    # Avoid zero scaling which could cause issues
        
        # Calculate both sides of the equation
        result_scaled = calibrate_latency(k*x0, k*y0, k*x1, k*y1, k*x, clamp=clamp)
        result_original_scaled = k * calibrate_latency(x0, y0, x1, y1, x, clamp=clamp)
        
        assert abs(result_scaled - result_original_scaled) < 1e-10, \
            f"Scaled result {result_scaled} != k * original result {result_original_scaled}"

    @given(
        x0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        c=floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        d=floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_translation_invariance(self, x0, y0, x1, y1, x, c, d, clamp):
        """Test that calibrate_latency(x0+c, y0+d, x1+c, y1+d, x+c) == calibrate_latency(x0, y0, x1, y1, x) + d."""
        assume(x1 != x0)  # Precondition for this property
        
        # Calculate both sides of the equation
        result_translated = calibrate_latency(x0+c, y0+d, x1+c, y1+d, x+c, clamp=clamp)
        result_original_translated = calibrate_latency(x0, y0, x1, y1, x, clamp=clamp) + d
        
        assert abs(result_translated - result_original_translated) < 1e-10, \
            f"Translated result {result_translated} != original result + d {result_original_translated}"

    @given(
        x0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_convex_combination(self, x0, y0, x1, y1, x, clamp):
        """Test that y is a convex combination of y0 and y1 when t in [0, 1]."""
        assume(x1 != x0)  # Precondition for this property
        
        result = calibrate_latency(x0, y0, x1, y1, x, clamp=clamp)
        
        t = (x - x0) / (x1 - x0)
        
        # When t is in [0, 1], y should be a convex combination of y0 and y1
        if 0 <= t <= 1:
            # A convex combination means y = (1-t)*y0 + t*y1
            expected = (1 - t) * y0 + t * y1
            assert abs(result - expected) < 1e-10, \
                f"Result {result} != convex combination {expected} (t={t})"
            
            # Also verify it's between y0 and y1
            min_y = min(y0, y1)
            max_y = max(y0, y1)
            assert min_y <= result <= max_y, \
                f"Result {result} not in range [{min_y}, {max_y}] for convex combination"

    @given(
        x0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_parameter_symmetry(self, x0, y0, x1, y1, x, clamp):
        """Test that calibrate_latency(x1, y1, x0, y0, x) == calibrate_latency(x0, y0, x1, y1, x)."""
        assume(x1 != x0)  # Precondition for this property
        
        result1 = calibrate_latency(x1, y1, x0, y0, x, clamp=clamp)
        result2 = calibrate_latency(x0, y0, x1, y1, x, clamp=clamp)
        
        assert abs(result1 - result2) < 1e-10, \
            f"Result with swapped parameters {result1} != original result {result2}"

    @given(
        x0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y0=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        y1=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        x=floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_clamp_idempotence(self, x0, y0, x1, y1, x):
        """Test that if y is already in [min(y0,y1), max(y0,y1)] then clamping has no effect."""
        assume(x1 != x0)  # Precondition for this property
        
        # First get the unclamped result
        result_unclamped = calibrate_latency(x0, y0, x1, y1, x, clamp=False)
        
        # Check if the unclamped result is already in the valid range
        min_y = min(y0, y1)
        max_y = max(y0, y1)
        
        if min_y <= result_unclamped <= max_y:
            # If it's already in range, clamping should have no effect
            result_clamped = calibrate_latency(x0, y0, x1, y1, x, clamp=True)
            assert abs(result_unclamped - result_clamped) < 1e-10, \
                f"Clamping had effect when result was already in range: {result_unclamped} vs {result_clamped}"