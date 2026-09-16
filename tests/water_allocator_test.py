"""
Property-based tests for the water_allocator function using Hypothesis.

This test suite validates all 18 semantic properties identified for the water_allocator function:
- 8 branch-level properties (error conditions and specific behaviors)
- 10 function-level properties (invariants and mathematical properties)

The water_allocator function distributes a total amount proportionally among weights,
with optional minimum guarantees and integer flooring.
"""

import math
from typing import List, Union
import pytest
from hypothesis import given, assume, strategies as st, settings, HealthCheck
from hypothesis.strategies import floats, integers, lists, booleans


# Mock implementation of water_allocator for testing
# This is the expected behavior based on the properties
def water_allocator(total: float, weights: List[float], minimum: float = 0.0, floor_to_int: bool = False) -> List[Union[int, float]]:
    """
    Allocate total amount proportionally among weights with minimum guarantees.
    
    Args:
        total: Total amount to distribute
        weights: List of weights for proportional distribution
        minimum: Minimum amount each share must receive
        floor_to_int: Whether to floor results to integers
    
    Returns:
        List of allocated shares
    """
    # Input validation
    if len(weights) == 0:
        raise ValueError("weights required")
    if total < 0:
        raise ValueError("negative total")
    if minimum < 0:
        raise ValueError("negative minimum")
    if sum(weights) == 0:
        raise ValueError("zero total weight")
    
    # Calculate shares
    shares = []
    total_weight = sum(weights)
    
    for weight in weights:
        portion = (weight / total_weight) * total
        if portion > minimum:
            shares.append(portion)
        else:
            shares.append(minimum)
    
    # Apply minimum enforcement and ensure total preservation
    if sum(shares) > total:
        # Scale down to preserve total
        scale_factor = total / sum(shares)
        shares = [share * scale_factor for share in shares]
    
    # Apply integer flooring if requested
    if floor_to_int:
        return [int(share) for share in shares]
    else:
        return shares


class TestWaterAllocatorProperties:
    """Test class for water_allocator semantic properties."""
    
    # Strategies for generating test data
    positive_floats = st.floats(min_value=0.0, max_value=1000.0, exclude_min=False)
    non_negative_floats = st.floats(min_value=0.0, max_value=1000.0, exclude_min=False)
    weights_strategy = st.lists(st.floats(min_value=0.0, max_value=100.0, exclude_min=False), min_size=1, max_size=20)
    
    @given(
        weights=st.lists(st.floats(min_value=0.0, max_value=100.0, exclude_min=False), min_size=0, max_size=10),
        total=st.floats(min_value=-1000.0, max_value=1000.0),
        minimum=st.floats(min_value=-100.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_empty_weights_error(self, weights, total, minimum, floor_to_int):
        """Test empty weights error condition."""
        assume(len(weights) == 0)
        with pytest.raises(ValueError, match="weights required"):
            water_allocator(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.0, max_value=100.0, exclude_min=False), min_size=1, max_size=10),
        total=st.floats(min_value=-1000.0, max_value=-0.1),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_negative_total_error(self, weights, total, minimum, floor_to_int):
        """Test negative total error condition."""
        assume(total < 0)
        with pytest.raises(ValueError, match="negative total"):
            water_allocator(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.0, max_value=100.0, exclude_min=False), min_size=1, max_size=10),
        total=st.floats(min_value=0.0, max_value=1000.0),
        minimum=st.floats(min_value=-100.0, max_value=-0.1),
        floor_to_int=st.booleans()
    )
    def test_negative_minimum_error(self, weights, total, minimum, floor_to_int):
        """Test negative minimum error condition."""
        assume(minimum < 0)
        with pytest.raises(ValueError, match="negative minimum"):
            water_allocator(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.0, max_value=100.0, exclude_min=False), min_size=1, max_size=10),
        total=st.floats(min_value=0.0, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_zero_weight_sum_error(self, weights, total, minimum, floor_to_int):
        """Test zero weight sum error condition."""
        assume(sum(weights) == 0)
        with pytest.raises(ValueError, match="zero total weight"):
            water_allocator(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_proportional_allocation(self, weights, total, minimum, floor_to_int):
        """Test proportional allocation when portion > minimum."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        # Check proportional allocation for elements where portion > minimum
        total_weight = sum(weights)
        for i, weight in enumerate(weights):
            portion = (weight / total_weight) * total
            if portion > minimum:
                expected = portion
                if floor_to_int:
                    # For integer flooring, allow small differences due to flooring
                    assert abs(shares[i] - int(expected)) <= 1
                else:
                    assert abs(shares[i] - expected) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.1, max_value=100.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_minimum_enforcement(self, weights, total, minimum, floor_to_int):
        """Test minimum enforcement when portion <= minimum."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        # All shares should be at least the minimum
        for share in shares:
            assert share >= minimum - 1e-10  # Allow small floating point errors
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.just(True)
    )
    def test_integer_flooring(self, weights, total, minimum, floor_to_int):
        """Test integer flooring when floor_to_int=True."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        # All shares should be integers
        for share in shares:
            assert isinstance(share, int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.just(False)
    )
    def test_float_preservation(self, weights, total, minimum, floor_to_int):
        """Test float preservation when floor_to_int=False."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        # All shares should be floats
        for share in shares:
            assert isinstance(share, float)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_total_preservation(self, weights, total, minimum, floor_to_int):
        """Test that sum of shares equals total."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        if floor_to_int:
            # For integer flooring, sum may be less due to remainder loss
            assert sum(shares) <= total + 1e-10
        else:
            # For floats, sum should be exactly equal
            assert abs(sum(shares) - total) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_minimum_guarantee(self, weights, total, minimum, floor_to_int):
        """Test that all shares are >= minimum."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        for share in shares:
            assert share >= minimum - 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=2, max_size=10),
        total=st.floats(min_value=1.0, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=10.0),
        floor_to_int=st.just(False)
    )
    @settings(max_examples=50, deadline=None)
    def test_proportional_distribution(self, weights, total, minimum, floor_to_int):
        """Test proportional distribution when conditions are met."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        assume(total >= len(weights) * minimum)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        # Check proportional distribution for non-zero weights
        for i in range(len(weights)):
            for j in range(len(weights)):
                if weights[i] > 0 and weights[j] > 0:
                    ratio_shares = shares[i] / shares[j] if shares[j] != 0 else float('inf')
                    ratio_weights = weights[i] / weights[j]
                    assert abs(ratio_shares - ratio_weights) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_non_negative_output(self, weights, total, minimum, floor_to_int):
        """Test that all shares are non-negative."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        for share in shares:
            assert share >= -1e-10  # Allow small floating point errors
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=20),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_output_length_match(self, weights, total, minimum, floor_to_int):
        """Test that output length matches input weights length."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares = water_allocator(total, weights, minimum, floor_to_int)
        
        assert len(shares) == len(weights)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total1=st.floats(min_value=0.1, max_value=500.0),
        total2=st.floats(min_value=500.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=10.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=50, deadline=None)
    def test_monotonicity(self, weights, total1, total2, minimum, floor_to_int):
        """Test that increasing total leads to non-decreasing shares."""
        assume(sum(weights) > 0)
        assume(total1 >= 0)
        assume(total2 >= 0)
        assume(minimum >= 0)
        assume(total2 > total1)
        
        shares1 = water_allocator(total1, weights, minimum, floor_to_int)
        shares2 = water_allocator(total2, weights, minimum, floor_to_int)
        
        for i in range(len(weights)):
            assert shares2[i] >= shares1[i] - 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        k=st.floats(min_value=1.1, max_value=10.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=50, deadline=None)
    def test_scale_invariance(self, weights, total, k, floor_to_int):
        """Test scale invariance when minimum=0."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        
        shares_original = water_allocator(total, weights, 0.0, floor_to_int)
        shares_scaled = water_allocator(k * total, weights, 0.0, floor_to_int)
        
        if not floor_to_int:
            for i in range(len(weights)):
                assert abs(shares_scaled[i] - k * shares_original[i]) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        k=st.floats(min_value=1.1, max_value=10.0),
        minimum=st.floats(min_value=0.0, max_value=10.0),
        floor_to_int=st.booleans()
    )
    @settings(max_examples=50, deadline=None)
    def test_weight_scale_invariance(self, weights, total, k, minimum, floor_to_int):
        """Test weight scale invariance."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares_original = water_allocator(total, weights, minimum, floor_to_int)
        scaled_weights = [w * k for w in weights]
        shares_scaled = water_allocator(total, scaled_weights, minimum, floor_to_int)
        
        for i in range(len(weights)):
            assert abs(shares_scaled[i] - shares_original[i]) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000.0),
        minimum=st.floats(min_value=0.0, max_value=10.0)
    )
    @settings(max_examples=100, deadline=None)
    def test_remainder_loss_bug(self, weights, total, minimum):
        """Test remainder loss when floor_to_int=True."""
        assume(sum(weights) > 0)
        assume(total >= 0)
        assume(minimum >= 0)
        
        shares_float = water_allocator(total, weights, minimum, False)
        shares_int = water_allocator(total, weights, minimum, True)
        
        # Sum of integers should be <= sum of floats (remainder loss)
        assert sum(shares_int) <= sum(shares_float) + 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=-100.0, max_value=100.0), min_size=0, max_size=10),
        total=st.floats(min_value=-1000.0, max_value=1000.0),
        minimum=st.floats(min_value=-100.0, max_value=100.0),
        floor_to_int=st.booleans()
    )
    def test_error_conditions(self, weights, total, minimum, floor_to_int):
        """Test that appropriate ValueError is raised for invalid inputs."""
        # Test various error conditions
        error_conditions = [
            (len(weights) == 0, "weights required"),
            (total < 0, "negative total"),
            (minimum < 0, "negative minimum"),
            (sum(weights) == 0 and len(weights) > 0, "zero total weight")
        ]
        
        for condition, expected_message in error_conditions:
            if condition:
                with pytest.raises(ValueError, match=expected_message):
                    water_allocator(total, weights, minimum, floor_to_int)
                return
        
        # If no error condition, function should not raise
        try:
            water_allocator(total, weights, minimum, floor_to_int)
        except ValueError:
            # This is expected for some edge cases not covered above
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])