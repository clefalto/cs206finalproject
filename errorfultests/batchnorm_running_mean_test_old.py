"""
Hypothesis-based tests for batchnorm_running_mean function semantic properties.
Tests all 13 semantic properties identified in batchnorm_running_mean_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats

# Import the function under test
from dataset.python_programs.batchnorm_running_mean import batchnorm_running_mean


class TestBatchNormRunningMeanProperties:
    """Test class for batchnorm_running_mean semantic properties."""

    @given(momentum=floats(allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_invalid_momentum_error(self, momentum, current_mean, batch_mean):
        """Test branch property: not (0 <= momentum <= 1) raises ValueError("momentum must be in [0, 1]")."""
        assume(not (0 <= momentum <= 1))
        with pytest.raises(ValueError, match="momentum must be in \\[0, 1\\]"):
            batchnorm_running_mean(momentum, current_mean, batch_mean)

    @given(momentum=floats(allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_momentum_range_validation(self, momentum, current_mean, batch_mean):
        """Test function property: if not (0 <= momentum <= 1) then raise ValueError("momentum must be in [0, 1]")."""
        assume(momentum < 0 or momentum > 1)
        with pytest.raises(ValueError, match="momentum must be in \\[0, 1\\]"):
            batchnorm_running_mean(momentum, current_mean, batch_mean)

    @given(momentum=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_weighted_average_update(self, momentum, current_mean, batch_mean):
        """Test function property: result = (1 - momentum) * current_mean + momentum * batch_mean."""
        assume(0 <= momentum <= 1)
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        expected = (1 - momentum) * current_mean + momentum * batch_mean
        
        # Account for floating point precision
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(momentum=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_convex_combination(self, momentum, current_mean, batch_mean):
        """Test function property: result is a convex combination of current_mean and batch_mean."""
        assume(0 <= momentum <= 1)
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        
        # A convex combination means result = alpha * current_mean + (1-alpha) * batch_mean
        # where 0 <= alpha <= 1. In this case, alpha = (1-momentum)
        alpha = 1 - momentum
        
        # Check that result is between the two values (inclusive)
        min_val = min(current_mean, batch_mean)
        max_val = max(current_mean, batch_mean)
        
        assert min_val <= result <= max_val, f"Result {result} is not between {min_val} and {max_val}"

    @given(momentum=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_momentum_weight_swap_bug(self, momentum, current_mean, batch_mean):
        """Test function property: weights are swapped: (1-momentum) applied to current_mean, momentum applied to batch_mean."""
        assume(0 <= momentum <= 1)
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        expected = (1 - momentum) * current_mean + momentum * batch_mean
        
        # This test verifies the specific weight assignment pattern
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(momentum=floats(min_value=0.5000000001, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_aggressive_update_behavior(self, momentum, current_mean, batch_mean):
        """Test function property: batch_mean receives higher weight than current_mean, making updates more aggressive."""
        assume(0 <= momentum <= 1 and momentum > 0.5)
        assume(current_mean != batch_mean)  # Avoid division by zero in comparison
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        
        # When momentum > 0.5, batch_mean weight (momentum) > current_mean weight (1-momentum)
        batch_weight = momentum
        current_weight = 1 - momentum
        
        assert batch_weight > current_weight, f"Batch weight {batch_weight} should be greater than current weight {current_weight}"
        
        # The result should be closer to batch_mean than to current_mean
        distance_to_batch = abs(result - batch_mean)
        distance_to_current = abs(result - current_mean)
        
        assert distance_to_batch < distance_to_current, f"Result {result} should be closer to batch_mean {batch_mean} than to current_mean {current_mean}"

    @given(momentum=floats(min_value=0, max_value=0.4999999999, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_conservative_update_behavior(self, momentum, current_mean, batch_mean):
        """Test function property: current_mean receives higher weight than batch_mean, making updates more conservative."""
        assume(0 <= momentum <= 1 and momentum < 0.5)
        assume(current_mean != batch_mean)  # Avoid division by zero in comparison
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        
        # When momentum < 0.5, current_mean weight (1-momentum) > batch_mean weight (momentum)
        batch_weight = momentum
        current_weight = 1 - momentum
        
        assert current_weight > batch_weight, f"Current weight {current_weight} should be greater than batch weight {batch_weight}"
        
        # The result should be closer to current_mean than to batch_mean
        distance_to_batch = abs(result - batch_mean)
        distance_to_current = abs(result - current_mean)
        
        assert distance_to_current < distance_to_batch, f"Result {result} should be closer to current_mean {current_mean} than to batch_mean {batch_mean}"

    @given(current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_equal_weight_update(self, current_mean, batch_mean):
        """Test function property: result = 0.5 * current_mean + 0.5 * batch_mean."""
        momentum = 0.5
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        expected = 0.5 * current_mean + 0.5 * batch_mean
        
        # Account for floating point precision
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_current_mean_preservation(self, current_mean, batch_mean):
        """Test function property: result = current_mean."""
        momentum = 0
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        expected = current_mean
        
        # Account for floating point precision
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_batch_mean_preservation(self, current_mean, batch_mean):
        """Test function property: result = batch_mean."""
        momentum = 1
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        expected = batch_mean
        
        # Account for floating point precision
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"

    @given(momentum=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_linear_interpolation(self, momentum, current_mean, batch_mean):
        """Test function property: result lies on the line segment between current_mean and batch_mean."""
        assume(0 <= momentum <= 1)
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        
        # For linear interpolation, result should be between the two endpoints
        min_val = min(current_mean, batch_mean)
        max_val = max(current_mean, batch_mean)
        
        assert min_val <= result <= max_val, f"Result {result} is not between {min_val} and {max_val}"

    @given(momentum1=floats(min_value=0, max_value=0.9999999999, allow_nan=False, allow_infinity=False), 
           momentum2=floats(min_value=0.0000000001, max_value=1, allow_nan=False, allow_infinity=False),
           current_mean=floats(allow_nan=False, allow_infinity=False), 
           batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_momentum_monotonicity(self, momentum1, momentum2, current_mean, batch_mean):
        """Test function property: result_with_momentum1 is closer to current_mean than result_with_momentum2."""
        assume(0 <= momentum1 < momentum2 <= 1)
        assume(current_mean != batch_mean)  # Avoid division by zero in comparison
        
        result1 = batchnorm_running_mean(momentum1, current_mean, batch_mean)
        result2 = batchnorm_running_mean(momentum2, current_mean, batch_mean)
        
        # When momentum increases, the result should move away from current_mean
        distance1 = abs(result1 - current_mean)
        distance2 = abs(result2 - current_mean)
        
        assert distance1 < distance2, f"Result with momentum {momentum1} should be closer to current_mean than result with momentum {momentum2}"

    @given(momentum=floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False), current_mean=floats(allow_nan=False, allow_infinity=False), batch_mean=floats(allow_nan=False, allow_infinity=False))
    def test_numerical_stability(self, momentum, current_mean, batch_mean):
        """Test function property: result is finite when 0 <= momentum <= 1."""
        assume(0 <= momentum <= 1)
        assume(current_mean != float('inf') and current_mean != float('-inf'))
        assume(batch_mean != float('inf') and batch_mean != float('-inf'))
        
        result = batchnorm_running_mean(momentum, current_mean, batch_mean)
        
        # Check that result is finite
        assert result != float('inf'), f"Result should not be infinity"
        assert result != float('-inf'), f"Result should not be negative infinity"
        assert result == result, f"Result should not be NaN"  # NaN check


if __name__ == "__main__":
    pytest.main([__file__, "-v"])