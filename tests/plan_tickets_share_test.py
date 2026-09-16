"""
Hypothesis-based tests for plan_tickets_share function semantic properties.

This test file exercises all 19 semantic properties identified for the
plan_tickets_share function using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, integers, lists, booleans
import math


def plan_tickets_share(total, weights, minimum, floor_to_int):
    """
    Allocate tickets proportionally based on weights with minimum guarantees.
    
    Args:
        total: Total number of tickets to distribute
        weights: List of weights for proportional allocation
        minimum: Minimum tickets each recipient must receive
        floor_to_int: Whether to floor results to integers
    
    Returns:
        List of ticket allocations
    """
    if len(weights) == 0:
        raise ValueError("weights required")
    if total < 0:
        raise ValueError("negative total")
    if minimum < 0:
        raise ValueError("negative minimum")
    if sum(weights) == 0:
        raise ValueError("zero total weight")
    
    shares = []
    for weight in weights:
        portion = total * weight / sum(weights)
        if portion > minimum:
            shares.append(portion)
        else:
            shares.append(minimum)
    
    if floor_to_int:
        shares = [math.floor(share) for share in shares]
    
    return shares


class TestPlanTicketsShareProperties:
    """Test class for plan_tickets_share semantic properties."""
    
    @given(
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=0, max_size=10),
        total=st.floats(min_value=-1000, max_value=1000),
        minimum=st.floats(min_value=-1000, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_empty_weights_error(self, weights, total, minimum, floor_to_int):
        """Test that empty weights raises ValueError."""
        assume(len(weights) == 0)
        with pytest.raises(ValueError, match="weights required"):
            plan_tickets_share(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=-1000, max_value=-0.1),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_negative_total_error(self, weights, total, minimum, floor_to_int):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="negative total"):
            plan_tickets_share(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=-1000, max_value=-0.1),
        floor_to_int=st.booleans()
    )
    def test_negative_minimum_error(self, weights, total, minimum, floor_to_int):
        """Test that negative minimum raises ValueError."""
        with pytest.raises(ValueError, match="negative minimum"):
            plan_tickets_share(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_zero_weight_sum_error(self, weights, total, minimum, floor_to_int):
        """Test that zero weight sum raises ValueError."""
        assume(sum(weights) == 0)
        with pytest.raises(ValueError, match="zero total weight"):
            plan_tickets_share(total, weights, minimum, floor_to_int)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_proportional_allocation(self, weights, total, minimum, floor_to_int):
        """Test proportional allocation when portion > minimum."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        
        for i, weight in enumerate(weights):
            portion = total * weight / sum(weights)
            if portion > minimum:
                if floor_to_int:
                    assert shares[i] == math.floor(portion)
                else:
                    assert shares[i] == portion
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0.1, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_minimum_enforcement(self, weights, total, minimum, floor_to_int):
        """Test minimum enforcement when portion <= minimum."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        
        for i, weight in enumerate(weights):
            portion = total * weight / sum(weights)
            if portion <= minimum:
                if floor_to_int:
                    assert shares[i] == math.floor(minimum)
                else:
                    assert shares[i] == minimum
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_integer_flooring(self, weights, total, minimum, floor_to_int):
        """Test that floor_to_int produces integer results."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert all(isinstance(share, int) for share in shares)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_float_preservation(self, weights, total, minimum, floor_to_int):
        """Test that non-floor_to_int preserves floats."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert any(isinstance(share, float) for share in shares)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_non_negative_shares(self, weights, total, minimum, floor_to_int):
        """Test that all shares are non-negative."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert all(share >= 0 for share in shares)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_minimum_shares(self, weights, total, minimum, floor_to_int):
        """Test that all shares meet minimum requirement."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert all(share >= minimum for share in shares)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_length(self, weights, total, minimum, floor_to_int):
        """Test that shares list has same length as weights."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert len(shares) == len(weights)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=2, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_proportional_distribution(self, weights, total, minimum, floor_to_int):
        """Test proportional distribution when portions > minimum."""
        assume(sum(weights) > 0)
        assume(all(w >= 0 for w in weights))
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        
        for i in range(len(weights)):
            for j in range(len(weights)):
                if i != j:
                    portion_i = total * weights[i] / sum(weights)
                    portion_j = total * weights[j] / sum(weights)
                    if portion_i > minimum and portion_j > minimum:
                        # Proportional relationship should be maintained
                        ratio_shares = shares[i] / shares[j] if shares[j] != 0 else float('inf')
                        ratio_weights = weights[i] / weights[j] if weights[j] != 0 else float('inf')
                        assert abs(ratio_shares - ratio_weights) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_total_preservation(self, weights, total, minimum, floor_to_int):
        """Test that sum of shares equals total when not flooring."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert abs(sum(shares) - total) < 1e-10
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_total_approximation(self, weights, total, minimum, floor_to_int):
        """Test that sum of shares approximates total when flooring."""
        assume(sum(weights) > 0)
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        assert abs(sum(shares) - total) < len(weights)
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total1=st.floats(min_value=0.1, max_value=1000),
        total2=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_monotonicity(self, weights, total1, total2, minimum, floor_to_int):
        """Test that increasing total increases shares."""
        assume(sum(weights) > 0)
        assume(total1 >= total2)
        shares1 = plan_tickets_share(total1, weights, minimum, floor_to_int)
        shares2 = plan_tickets_share(total2, weights, minimum, floor_to_int)
        
        for i in range(len(weights)):
            assert shares1[i] >= shares2[i]
    
    @given(
        weights1=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        weights2=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_weight_monotonicity(self, weights1, weights2, total, minimum, floor_to_int):
        """Test that increasing weight increases share."""
        assume(len(weights1) == len(weights2))
        assume(sum(weights1) > 0 and sum(weights2) > 0)
        
        # Find indices where weights1[i] >= weights2[i]
        valid_indices = [i for i in range(len(weights1)) if weights1[i] >= weights2[i]]
        assume(len(valid_indices) > 0)
        
        shares1 = plan_tickets_share(total, weights1, minimum, floor_to_int)
        shares2 = plan_tickets_share(total, weights2, minimum, floor_to_int)
        
        for i in valid_indices:
            assert shares1[i] >= shares2[i]
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0, max_value=1000),
        k=st.floats(min_value=0.1, max_value=100),
        floor_to_int=st.booleans()
    )
    def test_scale_invariance(self, weights, total, minimum, k, floor_to_int):
        """Test that scaling weights doesn't change results."""
        assume(sum(weights) > 0)
        assume(k > 0)
        
        shares1 = plan_tickets_share(total, weights, minimum, floor_to_int)
        scaled_weights = [w * k for w in weights]
        shares2 = plan_tickets_share(total, scaled_weights, minimum, floor_to_int)
        
        assert shares1 == shares2
    
    @given(
        weights=st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1, max_size=10),
        total=st.floats(min_value=0.1, max_value=1000),
        minimum=st.floats(min_value=0.1, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_minimum_dominance(self, weights, total, minimum, floor_to_int):
        """Test that when minimum dominates, all shares equal minimum."""
        assume(sum(weights) > 0)
        assume(minimum * len(weights) >= total)
        
        shares = plan_tickets_share(total, weights, minimum, floor_to_int)
        
        for share in shares:
            if floor_to_int:
                assert share == math.floor(minimum)
            else:
                assert share == minimum
    
    @given(
        weights=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=0, max_size=10),
        total=st.floats(min_value=-1000, max_value=1000),
        minimum=st.floats(min_value=-1000, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_error_conditions(self, weights, total, minimum, floor_to_int):
        """Test that all error conditions raise ValueError."""
        should_raise = (
            len(weights) == 0 or 
            total < 0 or 
            minimum < 0 or 
            sum(weights) == 0
        )
        
        if should_raise:
            with pytest.raises(ValueError):
                plan_tickets_share(total, weights, minimum, floor_to_int)
        else:
            # If no error condition, function should work
            assume(sum(weights) > 0)
            shares = plan_tickets_share(total, weights, minimum, floor_to_int)
            assert len(shares) == len(weights)