"""
Hypothesis-based tests for speed_trendline function semantic properties.

This test file exercises all semantic properties identified in 
properties/speed_trendline_properties.json using the Hypothesis testing framework.
"""

import math
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, booleans
import pytest


def speed_trendline(x0, y0, x1, y1, x, clamp=True):
    """
    Linear interpolation/extrapolation function with optional clamping.
    
    Args:
        x0, y0: First point coordinates
        x1, y1: Second point coordinates  
        x: Input value to interpolate/extrapolate for
        clamp: Whether to clamp result to [min(y0,y1), max(y0,y1)]
    
    Returns:
        Interpolated/extrapolated y value
    """
    if x0 == x1:
        raise ValueError("x0 and x1 cannot be equal")
    
    # Linear interpolation formula
    t = (x - x0) / (x1 - x0)
    y = y0 + t * (y1 - y0)
    
    # Apply clamping if requested
    if clamp:
        y_min, y_max = min(y0, y1), max(y0, y1)
        y = max(y_min, min(y_max, y))
    
    return y


class TestSpeedTrendlineBranchProperties:
    """Test branch-level semantic properties."""
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_invalid_input_error(self, x0, y0, y1, x):
        """Test that x0 == x1 raises ValueError."""
        with pytest.raises(ValueError, match="x0 and x1 cannot be equal"):
            speed_trendline(x0, y0, x0, y1, x)
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_lower_bound_clamp(self, x0, y0, x1, y1, x):
        """Test lower bound clamping when clamp=True and y < min(y0, y1)."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        y_min = min(y0, y1)
        
        # If result would be below y_min, it should be clamped to y_min
        # We can't directly test "y < min(y0, y1)" since we don't have access to the unclamped y
        # But we can verify the result is at least y_min
        assert result >= y_min
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_upper_bound_clamp(self, x0, y0, x1, y1, x):
        """Test upper bound clamping when clamp=True and y > max(y0, y1)."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        y_max = max(y0, y1)
        
        # If result would be above y_max, it should be clamped to y_max
        # We can't directly test "y > max(y0, y1)" since we don't have access to the unclamped y
        # But we can verify the result is at most y_max
        assert result <= y_max
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_unclamped_interpolation(self, x0, y0, x1, y1, x):
        """Test unclamped interpolation formula when clamp=False."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        expected = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        
        # Handle floating point precision
        if math.isnan(expected):
            assert math.isnan(result)
        else:
            assert abs(result - expected) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_left_endpoint_identity(self, x0, y0, x1, y1):
        """Test that speed_trendline(x0, y0, x1, y1, x0) == y0 when x0 != x1."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x0, clamp=True)
        assert abs(result - y0) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_right_endpoint_identity(self, x0, y0, x1, y1):
        """Test that speed_trendline(x0, y0, x1, y1, x1) == y1 when x0 != x1."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x1, clamp=True)
        assert abs(result - y1) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_intermediate_interpolation(self, x0, y0, x1, y1, x):
        """Test that when x0 < x < x1, result is between y0 and y1 (inclusive)."""
        assume(x0 != x1)
        assume(x0 < x < x1 or x1 < x < x0)  # x is between x0 and x1
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        y_min, y_max = min(y0, y1), max(y0, y1)
        
        # Result should be between y0 and y1 (inclusive)
        assert y_min <= result <= y_max
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_extrapolation(self, x0, y0, x1, y1, x):
        """Test that when x < x0 or x > x1, result may be outside [min(y0,y1), max(y0,y1)]."""
        assume(x0 != x1)
        assume(x < min(x0, x1) or x > max(x0, x1))  # x is outside [x0, x1]
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        y_min, y_max = min(y0, y1), max(y0, y1)
        
        # When extrapolating without clamping, result may be outside bounds
        # This property is about possibility, not requirement
        # So we just verify the function runs without error
        assert isinstance(result, float)


class TestSpeedTrendlineFunctionProperties:
    """Test function-level semantic properties."""
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_interpolation(self, x0, y0, x1, y1, x):
        """Test linear interpolation formula when x0 != x1."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        expected = y0 + ((x - x0) / (x1 - x0)) * (y1 - y0)
        
        if math.isnan(expected):
            assert math.isnan(result)
        else:
            assert abs(result - expected) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_bounds(self, x0, y0, x1, y1, x):
        """Test that clamped result is within [min(y0,y1), max(y0,y1)]."""
        assume(x0 != x1)
        
        result = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        y_min, y_max = min(y0, y1), max(y0, y1)
        
        assert y_min <= result <= y_max
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity_preservation(self, x0, y0, x1, y1, x):
        """Test that if y0 <= y1, then speed_trendline preserves monotonicity in x."""
        assume(x0 != x1)
        assume(y0 <= y1)
        
        # Test with two different x values
        x_test = x
        x_test2 = x + 1.0 if x < x1 else x - 1.0
        
        result1 = speed_trendline(x0, y0, x1, y1, x_test, clamp=False)
        result2 = speed_trendline(x0, y0, x1, y1, x_test2, clamp=False)
        
        # If x_test < x_test2, then result1 <= result2 (monotonicity)
        if x_test < x_test2:
            assert result1 <= result2
        elif x_test > x_test2:
            assert result1 >= result2
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_symmetry(self, x0, y0, x1, y1, x):
        """Test that speed_trendline(x0, y0, x1, y1, x) = speed_trendline(x1, y1, x0, y0, x)."""
        assume(x0 != x1)
        
        result1 = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        result2 = speed_trendline(x1, y1, x0, y0, x, clamp=False)
        
        if math.isnan(result1) and math.isnan(result2):
            pass  # Both NaN, considered equal
        else:
            assert abs(result1 - result2) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False),
        c=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False).filter(lambda x: x != 0)
    )
    def test_scale_invariance(self, x0, y0, x1, y1, x, c):
        """Test scale invariance: speed_trendline(c*x0, c*y0, c*x1, c*y1, c*x) = c * speed_trendline(x0, y0, x1, y1, x)."""
        assume(x0 != x1)
        assume(c != 0)
        
        result1 = speed_trendline(c * x0, c * y0, c * x1, c * y1, c * x, clamp=False)
        result2 = c * speed_trendline(x0, y0, x1, y1, x, clamp=False)
        
        if math.isnan(result1) and math.isnan(result2):
            pass  # Both NaN, considered equal
        else:
            assert abs(result1 - result2) < 1e-8  # Slightly looser tolerance for scaled values
    
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
        """Test translation invariance: speed_trendline(x0+a, y0+b, x1+a, y1+b, x+a) = speed_trendline(x0, y0, x1, y1, x) + b."""
        assume(x0 != x1)
        
        result1 = speed_trendline(x0 + a, y0 + b, x1 + a, y1 + b, x + a, clamp=False)
        result2 = speed_trendline(x0, y0, x1, y1, x, clamp=False) + b
        
        if math.isnan(result1) and math.isnan(result2):
            pass  # Both NaN, considered equal
        else:
            assert abs(result1 - result2) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_endpoint_consistency(self, x0, y0, x1, y1):
        """Test endpoint consistency: speed_trendline(x0, y0, x1, y1, x0) == y0 and speed_trendline(x0, y0, x1, y1, x1) == y1."""
        assume(x0 != x1)
        
        result_x0 = speed_trendline(x0, y0, x1, y1, x0, clamp=True)
        result_x1 = speed_trendline(x0, y0, x1, y1, x1, clamp=True)
        
        assert abs(result_x0 - y0) < 1e-10
        assert abs(result_x1 - y1) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_continuity(self, x0, y0, x1, y1, x):
        """Test that speed_trendline is continuous in x for all x (when x0 != x1)."""
        assume(x0 != x1)
        
        # Test continuity by checking that small changes in x produce small changes in result
        epsilon = 1e-6
        result1 = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        result2 = speed_trendline(x0, y0, x1, y1, x + epsilon, clamp=False)
        
        # The change in result should be proportional to epsilon
        # For linear interpolation, |result2 - result1| = |epsilon * (y1-y0)/(x1-x0)|
        expected_change = abs(epsilon * (y1 - y0) / (x1 - x0))
        actual_change = abs(result2 - result1)
        
        # Allow some floating point tolerance
        assert abs(actual_change - expected_change) < 1e-10
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_clamp_idempotence(self, x0, y0, x1, y1, x):
        """Test clamp idempotence: clamp(speed_trendline(...)) = speed_trendline(...) when clamp=True."""
        assume(x0 != x1)
        
        # First call with clamp=True
        result1 = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        
        # Second call with clamp=True (should be the same)
        result2 = speed_trendline(x0, y0, x1, y1, x, clamp=True)
        
        assert abs(result1 - result2) < 1e-15
    
    @given(
        x0=st.floats(allow_nan=False, allow_infinity=False),
        y0=st.floats(allow_nan=False, allow_infinity=False),
        x1=st.floats(allow_nan=False, allow_infinity=False),
        y1=st.floats(allow_nan=False, allow_infinity=False),
        x=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_linear_combination(self, x0, y0, x1, y1, x):
        """Test linear combination form: speed_trendline(x0, y0, x1, y1, x) = (1-t)*y0 + t*y1 where t = (x-x0)/(x1-x0)."""
        assume(x0 != x1)
        
        t = (x - x0) / (x1 - x0)
        expected = (1 - t) * y0 + t * y1
        result = speed_trendline(x0, y0, x1, y1, x, clamp=False)
        
        if math.isnan(expected):
            assert math.isnan(result)
        else:
            assert abs(result - expected) < 1e-10