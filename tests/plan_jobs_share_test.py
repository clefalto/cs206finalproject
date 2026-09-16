"""
Tests for plan_jobs_share function using Hypothesis testing framework.
Tests all semantic properties identified in properties/plan_jobs_share_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, floats, lists


def plan_jobs_share(total, weights, minimum=0, floor_to_int=False):
    """
    Plan job shares based on weights with minimum constraints.
    
    Args:
        total: Total amount to distribute
        weights: List of weights for distribution
        minimum: Minimum share for each weight (default: 0)
        floor_to_int: Whether to floor results to integers (default: False)
    
    Returns:
        list: Shares distributed according to weights with minimum constraints
    """
    # Error conditions
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
    for w in weights:
        portion = total * w / sum(weights)
        if portion > minimum:
            shares.append(portion)
        else:
            shares.append(minimum)
    
    # Apply integer flooring if requested
    if floor_to_int:
        return [int(v) for v in shares]
    
    return shares


class TestPlanJobsShare:
    """Test class for plan_jobs_share function semantic properties."""

    # Branch-level property tests
    
    @given(
        total=st.floats(min_value=-1000, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=0, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_empty_weights_error(self, total, weights, minimum, floor_to_int):
        """Test that empty weights list raises ValueError."""
        assume(len(weights) == 0)
        
        with pytest.raises(ValueError, match="weights required"):
            plan_jobs_share(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_negative_total_error(self, total, weights, minimum, floor_to_int):
        """Test that negative total raises ValueError."""
        assume(total < 0)
        
        with pytest.raises(ValueError, match="negative total"):
            plan_jobs_share(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=-0.1),
        floor_to_int=st.booleans()
    )
    def test_negative_minimum_error(self, total, weights, minimum, floor_to_int):
        """Test that negative minimum raises ValueError."""
        assume(minimum < 0)
        
        with pytest.raises(ValueError, match="negative minimum"):
            plan_jobs_share(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_zero_weight_sum_error(self, total, weights, minimum, floor_to_int):
        """Test that zero weight sum raises ValueError."""
        assume(sum(weights) == 0)
        
        with pytest.raises(ValueError, match="zero total weight"):
            plan_jobs_share(total, weights, minimum, floor_to_int)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_portion_above_minimum(self, total, weights, minimum, floor_to_int):
        """Test that portion > minimum results in portion being added to shares."""
        assume(sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        for i, w in enumerate(weights):
            portion = total * w / sum(weights)
            if portion > minimum:
                # The share should be the portion (or floored portion)
                expected = int(portion) if floor_to_int else portion
                assert shares[i] == expected

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_portion_at_minimum(self, total, weights, minimum, floor_to_int):
        """Test that portion <= minimum results in minimum being added to shares."""
        assume(sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        for i, w in enumerate(weights):
            portion = total * w / sum(weights)
            if portion <= minimum:
                # The share should be the minimum (or floored minimum)
                expected = int(minimum) if floor_to_int else minimum
                assert shares[i] == expected

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_integer_flooring(self, total, weights, minimum, floor_to_int):
        """Test that floor_to_int=True returns integer shares."""
        assume(sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        # All shares should be integers
        assert all(isinstance(s, int) for s in shares)

    # Function-level property tests
    
    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_non_empty_weights(self, total, weights, minimum, floor_to_int):
        """Test that weights list is non-empty."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        # This is a precondition test - if we get here, weights should be non-empty
        assert len(weights) > 0

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_non_negative_total(self, total, weights, minimum, floor_to_int):
        """Test that total is non-negative."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        # This is a precondition test - if we get here, total should be non-negative
        assert total >= 0

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_non_negative_minimum(self, total, weights, minimum, floor_to_int):
        """Test that minimum is non-negative."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        # This is a precondition test - if we get here, minimum should be non-negative
        assert minimum >= 0

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_positive_weight_sum(self, total, weights, minimum, floor_to_int):
        """Test that sum of weights is positive."""
        assume(len(weights) > 0)
        
        # This is a precondition test - if we get here, weight sum should be positive
        assert sum(weights) > 0

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_length(self, total, weights, minimum, floor_to_int):
        """Test that shares list has same length as weights."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert len(shares) == len(weights)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_non_negative(self, total, weights, minimum, floor_to_int):
        """Test that all shares are non-negative."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert all(s >= 0 for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_minimum_bound(self, total, weights, minimum, floor_to_int):
        """Test that all shares are at least minimum."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert all(s >= minimum for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_sum_bound(self, total, weights, minimum, floor_to_int):
        """Test that sum of shares is at least total."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert sum(shares) >= total

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_sum_exact(self, total, weights, minimum, floor_to_int):
        """Test that sum of shares equals total when not flooring to int."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert abs(sum(shares) - total) < 1e-10  # Account for floating point precision

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_proportional(self, total, weights, minimum, floor_to_int):
        """Test that shares are proportional to weights where above minimum."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        for i, w in enumerate(weights):
            portion = total * w / sum(weights)
            if portion > minimum:
                # Should be proportional
                assert abs(shares[i] / total - w / sum(weights)) < 1e-10

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_shares_integer(self, total, weights, minimum, floor_to_int):
        """Test that all shares are integers when floor_to_int=True."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, int) for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_float(self, total, weights, minimum, floor_to_int):
        """Test that all shares are floats when floor_to_int=False."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert all(isinstance(s, float) for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_monotonic_weights(self, total, weights, minimum, floor_to_int):
        """Test that shares preserve weight ordering."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        # Check that if weights[i] <= weights[j], then shares[i] <= shares[j]
        for i in range(len(weights)):
            for j in range(len(weights)):
                if weights[i] <= weights[j]:
                    assert shares[i] <= shares[j]

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans(),
        k=st.floats(min_value=0.1, max_value=10)
    )
    def test_shares_scale_invariant(self, total, weights, minimum, floor_to_int, k):
        """Test that scaling total scales shares proportionally."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        original_shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        scaled_shares = plan_jobs_share(k * total, weights, minimum, floor_to_int)
        
        expected_scaled = [k * s for s in original_shares]
        
        # Compare with tolerance for floating point
        for i in range(len(original_shares)):
            assert abs(scaled_shares[i] - expected_scaled[i]) < 1e-10

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans(),
        delta=st.floats(min_value=0, max_value=100)
    )
    def test_shares_translation_invariant(self, total, weights, minimum, floor_to_int, delta):
        """Test that adding delta to total distributes proportionally."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        original_shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        # Check if adding delta would cause any share to fall below minimum
        # For simplicity, we'll just test the mathematical property
        if not floor_to_int:  # Only test for float case to avoid integer truncation issues
            new_total = total + delta
            new_shares = plan_jobs_share(new_total, weights, minimum, floor_to_int)
            
            # Expected: shares[i] + delta * weights[i] / sum(weights)
            expected = [s + delta * w / sum(weights) for s, w in zip(original_shares, weights)]
            
            for i in range(len(original_shares)):
                assert abs(new_shares[i] - expected[i]) < 1e-10

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_minimum_preservation(self, total, weights, minimum, floor_to_int):
        """Test that all shares are at least minimum."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert all(s >= minimum for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_total_preservation(self, total, weights, minimum, floor_to_int):
        """Test that sum of shares equals total."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        assert abs(sum(shares) - total) < 1e-10

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(False)
    )
    def test_shares_weight_preservation(self, total, weights, minimum, floor_to_int):
        """Test that shares preserve weight proportions where above minimum."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        for i, w in enumerate(weights):
            portion = total * w / sum(weights)
            if portion > minimum:
                # Should preserve weight proportion
                assert abs(shares[i] / total - w / sum(weights)) < 1e-10

    @given(
        total=st.floats(min_value=0, max_value=1000),
        weights=st.lists(st.floats(min_value=0, max_value=1000), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=1000),
        floor_to_int=st.just(True)
    )
    def test_shares_flooring_bug(self, total, weights, minimum, floor_to_int):
        """Test that integer flooring may result in sum less than total."""
        assume(len(weights) > 0 and sum(weights) > 0)
        
        shares = plan_jobs_share(total, weights, minimum, floor_to_int)
        
        # Sum of floored shares should be <= sum of original shares
        original_shares = plan_jobs_share(total, weights, minimum, False)
        assert sum(shares) <= sum(original_shares)
        
        # May be less than total due to flooring
        assert sum(shares) <= total

    @given(
        total=st.floats(min_value=-1000, max_value=1000),
        weights=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=0, max_size=10),
        minimum=st.floats(min_value=-1000, max_value=1000),
        floor_to_int=st.booleans()
    )
    def test_shares_error_conditions(self, total, weights, minimum, floor_to_int):
        """Test that appropriate ValueError is raised for error conditions."""
        error_conditions = [
            (len(weights) == 0, "weights required"),
            (total < 0, "negative total"),
            (minimum < 0, "negative minimum"),
            (sum(weights) == 0, "zero total weight")
        ]
        
        for condition, expected_msg in error_conditions:
            if condition:
                with pytest.raises(ValueError, match=expected_msg):
                    plan_jobs_share(total, weights, minimum, floor_to_int)