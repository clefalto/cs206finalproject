"""
Hypothesis-based tests for calibrate_loss function semantic properties.

This test file exercises all semantic properties identified in 
properties/calibrate_loss_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, booleans
import math

# Import the function under test
from dataset.python_programs.calibrate_loss import calibrate_loss


class TestCalibrateLossProperties:
    """Test class for calibrate_loss semantic properties."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_degenerate_segment_error(self, x0, y0, y1, x):
        """
        Test degenerate_segment_error property.
        
        When x1 == x0, the function should raise ValueError.
        """
        with pytest.raises(ValueError, match="degenerate segment"):
            calibrate_loss(x0, y0, x0, y1, x)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)  # Only test when clamp=True
    )
    def test_lower_clamp(self, x0, y0, x1, y1, x, clamp):
        """
        Test lower_clamp property.
        
        If clamp=True and y < lo, then y should be clamped to lo.
        """
        assume(x1 != x0)  # Avoid degenerate case
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        lo = min(y0, y1)
        
        # If the unclamped value would be less than lo, it should be clamped to lo
        t = (x - x0) / (x1 - x0)
        y_unclamped = y0 + t * (y1 - y0)
        
        if y_unclamped < lo:
            assert result == lo
        else:
            assert result >= lo

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)  # Only test when clamp=True
    )
    def test_upper_clamp(self, x0, y0, x1, y1, x, clamp):
        """
        Test upper_clamp property.
        
        If clamp=True and y > hi, then y should be clamped to hi.
        """
        assume(x1 != x0)  # Avoid degenerate case
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        hi = max(y0, y1)
        
        # If the unclamped value would be greater than hi, it should be clamped to hi
        t = (x - x0) / (x1 - x0)
        y_unclamped = y0 + t * (y1 - y0)
        
        if y_unclamped > hi:
            assert result == hi
        else:
            assert result <= hi

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x, clamp):
        """
        Test linear_interpolation property.
        
        When x1 != x0, the function should perform linear interpolation:
        calibrate_loss(x0, y0, x1, y1, x) = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        """
        assume(x1 != x0)  # Precondition: x1 != x0
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        
        # Calculate expected value using the linear interpolation formula
        expected = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        
        # Use math.isclose for floating point comparison
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)  # Only test when clamp=True
    )
    def test_boundary_preservation(self, x0, y0, x1, y1, x, clamp):
        """
        Test boundary_preservation property.
        
        When x1 != x0 and clamp=True, the result should be between min(y0, y1) and max(y0, y1).
        """
        assume(x1 != x0)  # Precondition: x1 != x0
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        lo = min(y0, y1)
        hi = max(y0, y1)
        
        assert lo <= result <= hi

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_endpoint_identity(self, x0, y0, x1, y1, clamp):
        """
        Test endpoint_identity property.
        
        When x1 != x0, calibrate_loss(x0, y0, x1, y1, x0) == y0 and 
        calibrate_loss(x0, y0, x1, y1, x1) == y1.
        """
        assume(x1 != x0)  # Precondition: x1 != x0
        
        # Test at x0
        result_x0 = calibrate_loss(x0, y0, x1, y1, x0, clamp=clamp)
        assert math.isclose(result_x0, y0, rel_tol=1e-9, abs_tol=1e-9)
        
        # Test at x1
        result_x1 = calibrate_loss(x0, y0, x1, y1, x1, clamp=clamp)
        assert math.isclose(result_x1, y1, rel_tol=1e-9, abs_tol=1e-9)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x_a=st.floats(allow_nan=False, allow_infinity=False),
        x_b=st.floats(allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_monotonicity(self, x0, y0, x1, y1, x_a, x_b, clamp):
        """
        Test monotonicity property.
        
        When x1 != x0 and y1 >= y0, if x_a <= x_b then 
        calibrate_loss(x0, y0, x1, y1, x_a) <= calibrate_loss(x0, y0, x1, y1, x_b).
        """
        assume(x1 != x0)  # Precondition: x1 != x0
        assume(y1 >= y0)  # Precondition: y1 >= y0
        assume(x_a <= x_b)  # Precondition: x_a <= x_b
        
        result_a = calibrate_loss(x0, y0, x1, y1, x_a, clamp=clamp)
        result_b = calibrate_loss(x0, y0, x1, y1, x_b, clamp=clamp)
        
        assert result_a <= result_b

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)  # Only test when clamp=True
    )
    def test_clamp_range(self, x0, y0, x1, y1, x, clamp):
        """
        Test clamp_range property.
        
        When x1 != x0 and clamp=True, the result should be in the range [min(y0, y1), max(y0, y1)].
        """
        assume(x1 != x0)  # Precondition: x1 != x0
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        lo = min(y0, y1)
        hi = max(y0, y1)
        
        # The result should be in the closed interval [lo, hi]
        assert lo <= result <= hi


class TestCalibrateLossEdgeCases:
    """Additional edge case tests for calibrate_loss function."""

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=booleans()
    )
    def test_no_clamp_behavior(self, x0, y0, x1, y1, x, clamp):
        """
        Test that when clamp=False, no clamping occurs.
        """
        assume(x1 != x0)  # Avoid degenerate case
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        
        # Calculate the unclamped value
        t = (x - x0) / (x1 - x0)
        expected_unclamped = y0 + t * (y1 - y0)
        
        if not clamp:
            # When clamp=False, result should equal the unclamped value
            assert math.isclose(result, expected_unclamped, rel_tol=1e-9, abs_tol=1e-9)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_degenerate_segment_error_message(self, x0, y0, y1, x):
        """
        Test that the degenerate segment error has the correct message.
        """
        with pytest.raises(ValueError) as exc_info:
            calibrate_loss(x0, y0, x0, y1, x)
        
        assert "degenerate segment" in str(exc_info.value)

    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        clamp=st.just(True)
    )
    def test_clamp_consistency(self, x0, y0, x1, y1, x, clamp):
        """
        Test that clamping produces consistent results within bounds.
        """
        assume(x1 != x0)  # Avoid degenerate case
        
        result = calibrate_loss(x0, y0, x1, y1, x, clamp=clamp)
        lo = min(y0, y1)
        hi = max(y0, y1)
        
        # Result should always be within bounds when clamping is enabled
        assert lo <= result <= hi
        
        # If the unclamped value is already within bounds, result should equal it
        t = (x - x0) / (x1 - x0)
        y_unclamped = y0 + t * (y1 - y0)
        
        if lo <= y_unclamped <= hi:
            assert math.isclose(result, y_unclamped, rel_tol=1e-9, abs_tol=1e-9)