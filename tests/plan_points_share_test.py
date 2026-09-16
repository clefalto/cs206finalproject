"""
Comprehensive Hypothesis-based tests for plan_points_share function.

This test suite exercises all semantic properties identified in 
properties/plan_points_share_properties.json using property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import floats, integers, lists, one_of
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.plan_points_share import plan_points_share


class TestPlanPointsShare:
    """Test class for plan_points_share function using Hypothesis."""

    # ============================================================================
    # Error Condition Tests (Branch Properties)
    # ============================================================================

    @given(
        total=st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_negative_total_error(self, total, weights, minimum):
        """Test that negative total raises ValueError with appropriate message."""
        with pytest.raises(ValueError, match="total < 0"):
            plan_points_share(total, weights, minimum=minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=-100, max_value=-0.1, allow_nan=False, allow_infinity=False)
    )
    def test_negative_minimum_error(self, total, weights, minimum):
        """Test that negative minimum raises ValueError with appropriate message."""
        with pytest.raises(ValueError, match="minimum < 0"):
            plan_points_share(total, weights, minimum=minimum)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.one_of(
            st.lists(st.floats(min_value=0, max_value=0), min_size=1, max_size=10),  # All zeros
            st.lists(st.floats(min_value=0, max_value=100), min_size=0, max_size=0)  # Empty list
        ),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_weights_error(self, total, weights, minimum):
        """Test that invalid weights (empty or sum to zero) raise ValueError."""
        with pytest.raises(ValueError, match="invalid weights"):
            plan_points_share(total, weights, minimum=minimum)

    # ============================================================================
    # Function-Level Properties
    # ============================================================================

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_total(self, total, weights, minimum):
        """Test that total is non-negative (precondition)."""
        assume(total >= 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        # This is a precondition test - the function should accept non-negative totals
        assert isinstance(shares, list)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_non_negative_minimum(self, total, weights, minimum):
        """Test that minimum is non-negative (precondition)."""
        assume(minimum >= 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        # This is a precondition test - the function should accept non-negative minimum
        assert isinstance(shares, list)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_valid_weights(self, total, weights, minimum):
        """Test that weights are valid (non-empty and sum > 0)."""
        assume(len(weights) > 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        # This is a precondition test - the function should accept valid weights
        assert isinstance(shares, list)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_length(self, total, weights, minimum):
        """Test that shares length equals weights length."""
        assume(len(weights) > 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert len(shares) == len(weights)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_non_negative(self, total, weights, minimum):
        """Test that all shares are non-negative."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert all(s >= 0 for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_minimum_bound(self, total, weights, minimum):
        """Test that all shares are at least minimum."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert all(s >= minimum for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_sum_bound(self, total, weights, minimum):
        """Test that sum of shares is at least total."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert sum(shares) >= total

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_integer(self, total, weights, minimum):
        """Test that all shares are integers."""
        shares = plan_points_share(total, weights, minimum=minimum)
        assert all(isinstance(s, int) for s in shares)

    @given(
        total=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shares_proportional(self, total, weights, minimum):
        """Test that shares are proportional when no share is clamped to minimum."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        
        shares = plan_points_share(total, weights, minimum=minimum)
        weight_sum = sum(weights)
        
        # Check proportionality for shares that are not clamped to minimum
        for i, (share, weight) in enumerate(zip(shares, weights)):
            expected_raw = (weight / weight_sum) * total
            if share > minimum:  # Not clamped
                # Allow for small floating point differences due to integer conversion
                expected_share = int(expected_raw)
                assert share == expected_share, f"Share {i} not proportional: got {share}, expected {expected_share}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_monotonic_weights(self, total, weights, minimum):
        """Test that shares preserve weight ordering."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        
        # Check that if weights[i] <= weights[j], then shares[i] <= shares[j]
        for i in range(len(weights)):
            for j in range(len(weights)):
                if weights[i] <= weights[j]:
                    assert shares[i] <= shares[j], f"Monotonicity violated: weight[{i}]={weights[i]} <= weight[{j}]={weights[j]} but share[{i}]={shares[i]} > share[{j}]={shares[j]}"

    @given(
        total=st.floats(min_value=1, max_value=100, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=2, max_size=5),
        minimum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
        k=st.floats(min_value=1.1, max_value=10, allow_nan=False, allow_infinity=False)
    )
    def test_shares_scale_invariant(self, total, weights, minimum, k):
        """Test that scaling total by k scales shares proportionally."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0 and k > 0)
        
        original_shares = plan_points_share(total, weights, minimum=minimum)
        scaled_shares = plan_points_share(k * total, weights, minimum=minimum)
        
        # Check that scaled shares are approximately k times original shares
        for orig, scaled in zip(original_shares, scaled_shares):
            expected_scaled = int(k * orig)
            # Allow for small differences due to integer conversion and minimum clamping
            assert abs(scaled - expected_scaled) <= 1, f"Scale invariance violated: {orig} -> {scaled}, expected ~{expected_scaled}"

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_minimum_preservation(self, total, weights, minimum):
        """Test that all shares are at least minimum (redundant with test_shares_minimum_bound but explicit)."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert all(s >= minimum for s in shares)

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_shares_flooring_bug(self, total, weights, minimum):
        """Test the flooring bug: sum of shares <= total due to integer conversion."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert sum(shares) <= total, f"Flooring bug not present: sum={sum(shares)} > total={total}"

    @given(
        total=st.one_of(
            st.floats(min_value=-1000, max_value=-0.1, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
        ),
        weights=st.one_of(
            st.lists(st.floats(min_value=0, max_value=0), min_size=1, max_size=10),  # All zeros
            st.lists(st.floats(min_value=0, max_value=100), min_size=0, max_size=0),  # Empty list
            st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10)  # Valid weights
        ),
        minimum=st.one_of(
            st.floats(min_value=-100, max_value=-0.1, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
        )
    )
    def test_shares_error_conditions(self, total, weights, minimum):
        """Test that appropriate ValueError is raised for error conditions."""
        should_raise = (total < 0) or (minimum < 0) or (not weights or sum(weights) == 0)
        
        if should_raise:
            with pytest.raises(ValueError):
                plan_points_share(total, weights, minimum=minimum)
        else:
            # If no error should be raised, the function should work
            shares = plan_points_share(total, weights, minimum=minimum)
            assert isinstance(shares, list)

    @given(
        total=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shares_weight_sum_preservation(self, total, weights, minimum):
        """Test that sum of shares equals total when no share is clamped to minimum."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        
        shares = plan_points_share(total, weights, minimum=minimum)
        weight_sum = sum(weights)
        
        # Check if any share is clamped to minimum
        has_clamped = any(share == minimum for share in shares)
        
        if not has_clamped:
            # If no shares are clamped, sum should equal total
            assert sum(shares) == total, f"Sum preservation failed: sum={sum(shares)} != total={total}"

    @given(
        total=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=2, max_size=10),
        minimum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    def test_shares_weight_proportionality(self, total, weights, minimum):
        """Test that shares[i] / total == weights[i] / sum(weights) when no share is clamped."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        
        shares = plan_points_share(total, weights, minimum=minimum)
        weight_sum = sum(weights)
        
        # Check if any share is clamped to minimum
        has_clamped = any(share == minimum for share in shares)
        
        if not has_clamped:
            # If no shares are clamped, proportionality should hold
            for i, (share, weight) in enumerate(zip(shares, weights)):
                expected_ratio = weight / weight_sum
                actual_ratio = share / total
                # Allow for small floating point differences due to integer conversion
                assert abs(actual_ratio - expected_ratio) < 0.01, f"Proportionality failed for index {i}: {actual_ratio} != {expected_ratio}"


class TestPlanPointsShareEdgeCases:
    """Additional edge case tests for plan_points_share function."""

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=1),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_single_weight(self, total, weights, minimum):
        """Test behavior with single weight."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert len(shares) == 1
        assert shares[0] >= minimum

    @given(
        total=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=100), min_size=10, max_size=100),
        minimum=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_many_weights(self, total, weights, minimum):
        """Test behavior with many weights."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        shares = plan_points_share(total, weights, minimum=minimum)
        assert len(shares) == len(weights)
        assert all(s >= minimum for s in shares)

    @example(total=0.0, weights=[1.0], minimum=0.0)
    @example(total=100.0, weights=[1.0, 1.0], minimum=50.0)
    @example(total=1.0, weights=[0.5, 0.5], minimum=1.0)
    @given(
        total=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        weights=st.lists(st.floats(min_value=0.1, max_value=10), min_size=1, max_size=5),
        minimum=st.floats(min_value=0, max_value=50, allow_nan=False, allow_infinity=False)
    )
    def test_specific_edge_cases(self, total, weights, minimum):
        """Test specific edge cases that might reveal bugs."""
        assume(total >= 0 and minimum >= 0 and sum(weights) > 0)
        
        shares = plan_points_share(total, weights, minimum=minimum)
        
        # Basic sanity checks
        assert len(shares) == len(weights)
        assert all(isinstance(s, int) for s in shares)
        assert all(s >= minimum for s in shares)
        assert sum(shares) >= total
        assert sum(shares) <= total  # Due to flooring bug


if __name__ == "__main__":
    # Run the tests if executed directly
    pytest.main([__file__, "-v"])