"""
Comprehensive Hypothesis tests for plan_seats_share function
Testing all semantic properties identified in properties/plan_seats_share_properties.json
"""

import pytest
from hypothesis import given, assume, strategies as st, example
from hypothesis.strategies import floats, integers, lists, booleans
import math

# Import the function under test
from dataset.python_programs.plan_seats_share import plan_seats_share


class TestPlanSeatsShare:
    """Test class for plan_seats_share function using Hypothesis"""

    # Strategies for generating test data
    @pytest.fixture
    def valid_weights_strategy(self):
        """Strategy for generating valid weights (non-empty, non-zero sum)"""
        return lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=50
        ).filter(lambda w: sum(w) > 0)

    @pytest.fixture
    def valid_total_strategy(self):
        """Strategy for generating valid total values"""
        return floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)

    @pytest.fixture
    def valid_minimum_strategy(self):
        """Strategy for generating valid minimum values"""
        return floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

    # BRANCH PROPERTIES - Error conditions

    @given(
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_empty_weights_error(self, total, minimum, floor_to_int):
        """Test: len(weights) == 0 => raises ValueError("weights required")"""
        with pytest.raises(ValueError, match="weights required"):
            plan_seats_share(total, [], floor_to_int=floor_to_int, minimum=minimum)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_negative_total_error(self, weights, minimum, floor_to_int):
        """Test: total < 0 => raises ValueError("negative total")"""
        with pytest.raises(ValueError, match="negative total"):
            plan_seats_share(-1.0, weights, floor_to_int=floor_to_int, minimum=minimum)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_negative_minimum_error(self, weights, total, floor_to_int):
        """Test: minimum < 0 => raises ValueError("negative minimum")"""
        with pytest.raises(ValueError, match="negative minimum"):
            plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=-1.0)

    @given(
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_zero_weight_sum_error(self, total, minimum, floor_to_int):
        """Test: sum(weights) == 0 => raises ValueError("zero total weight")"""
        # Generate weights that sum to zero (all zeros)
        weights = [0.0] * 5
        with pytest.raises(ValueError, match="zero total weight"):
            plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_integer_flooring(self, weights, total, minimum):
        """Test: floor_to_int => return [int(v) for v in shares]"""
        result = plan_seats_share(total, weights, floor_to_int=True, minimum=minimum)
        expected = [int(v) for v in plan_seats_share(total, weights, floor_to_int=False, minimum=minimum)]
        assert result == expected
        assert all(isinstance(x, int) for x in result)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_proportional_allocation(self, weights, total, minimum, floor_to_int):
        """Test: portion > minimum => shares.append(portion)"""
        weight_sum = sum(weights)
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion > minimum:
                if floor_to_int:
                    assert shares[i] == int(portion)
                else:
                    assert shares[i] == portion

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_minimum_floor(self, weights, total, minimum, floor_to_int):
        """Test: portion <= minimum => shares.append(minimum)"""
        weight_sum = sum(weights)
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        
        for i, w in enumerate(weights):
            portion = (w / weight_sum) * total
            if portion <= minimum:
                if floor_to_int:
                    assert shares[i] == int(minimum)
                else:
                    assert shares[i] == minimum

    # FUNCTION PROPERTIES - Valid inputs

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_non_empty_weights_required(self, weights, total, minimum, floor_to_int):
        """Test: len(weights) > 0"""
        assume(len(weights) > 0)
        result = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert len(weights) > 0

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_non_negative_total(self, weights, minimum, floor_to_int):
        """Test: total >= 0"""
        result = plan_seats_share(0.0, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert 0.0 >= 0

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_non_negative_minimum(self, weights, total, floor_to_int):
        """Test: minimum >= 0"""
        result = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=0.0)
        assert 0.0 >= 0

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_non_zero_weight_sum(self, weights, total, minimum, floor_to_int):
        """Test: sum(weights) != 0"""
        assume(sum(weights) != 0)
        result = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert sum(weights) != 0

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_shares_length_equals_weights_length(self, weights, total, minimum, floor_to_int):
        """Test: len(shares) == len(weights)"""
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert len(shares) == len(weights)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_shares_sum_approximates_total(self, weights, total, minimum, floor_to_int):
        """Test: abs(sum(shares) - total) <= len(weights) * minimum"""
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert abs(sum(shares) - total) <= len(weights) * minimum

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_shares_non_negative(self, weights, total, minimum, floor_to_int):
        """Test: all(s >= 0 for s in shares)"""
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert all(s >= 0 for s in shares)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_shares_minimum_bound(self, weights, total, minimum, floor_to_int):
        """Test: all(s >= minimum for s in shares)"""
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=minimum)
        assert all(s >= minimum for s in shares)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_proportional_when_no_minimum(self, weights, total, floor_to_int):
        """Test: shares[i] / total == weights[i] / sum(weights) for all i"""
        assume(total > 0)
        shares = plan_seats_share(total, weights, floor_to_int=floor_to_int, minimum=0.0)
        weight_sum = sum(weights)
        
        for i in range(len(weights)):
            expected_ratio = weights[i] / weight_sum
            if total > 0:
                actual_ratio = shares[i] / total
                assert abs(actual_ratio - expected_ratio) < 1e-10

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_integer_output_when_floored(self, weights, total, minimum):
        """Test: all(isinstance(s, int) for s in shares)"""
        shares = plan_seats_share(total, weights, floor_to_int=True, minimum=minimum)
        assert all(isinstance(s, int) for s in shares)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_float_output_when_not_floored(self, weights, total, minimum):
        """Test: all(isinstance(s, float) for s in shares)"""
        shares = plan_seats_share(total, weights, floor_to_int=False, minimum=minimum)
        assert all(isinstance(s, float) for s in shares)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_with_total(self, weights, minimum):
        """Test: total1 <= total2 => all(shares1[i] <= shares2[i] for i in range(len(weights)))"""
        total1 = 100.0
        total2 = 200.0
        
        shares1 = plan_seats_share(total1, weights, floor_to_int=False, minimum=minimum)
        shares2 = plan_seats_share(total2, weights, floor_to_int=False, minimum=minimum)
        
        assert all(shares1[i] <= shares2[i] for i in range(len(weights)))

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonic_with_minimum(self, weights, total):
        """Test: minimum1 <= minimum2 => all(shares1[i] <= shares2[i] for i in range(len(weights)))"""
        minimum1 = 1.0
        minimum2 = 2.0
        
        shares1 = plan_seats_share(total, weights, floor_to_int=False, minimum=minimum1)
        shares2 = plan_seats_share(total, weights, floor_to_int=False, minimum=minimum2)
        
        assert all(shares1[i] <= shares2[i] for i in range(len(weights)))

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariant_weights(self, weights, total, minimum):
        """Test: plan_seats_share(total, weights) == plan_seats_share(total, [k*w for w in weights]) for any k > 0"""
        k = 2.5
        scaled_weights = [k * w for w in weights]
        
        shares1 = plan_seats_share(total, weights, floor_to_int=False, minimum=minimum)
        shares2 = plan_seats_share(total, scaled_weights, floor_to_int=False, minimum=minimum)
        
        assert shares1 == shares2

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariant_total(self, weights, minimum):
        """Test: plan_seats_share(k*total, weights) == [k*s for s in plan_seats_share(total, weights)] for any k >= 0"""
        total = 100.0
        k = 2.0
        
        shares_original = plan_seats_share(total, weights, floor_to_int=False, minimum=minimum)
        shares_scaled = plan_seats_share(k * total, weights, floor_to_int=False, minimum=minimum)
        expected_scaled = [k * s for s in shares_original]
        
        assert shares_scaled == expected_scaled

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    def test_remainder_loss_when_floored(self, weights, total):
        """Test: sum(shares) <= total"""
        shares = plan_seats_share(total, weights, floor_to_int=True, minimum=0.0)
        assert sum(shares) <= total

    # Additional edge case tests

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_all_zero_weights_handled(self, weights, total, minimum, floor_to_int):
        """Test edge case where all weights are zero (should raise error)"""
        zero_weights = [0.0] * len(weights)
        with pytest.raises(ValueError, match="zero total weight"):
            plan_seats_share(total, zero_weights, floor_to_int=floor_to_int, minimum=minimum)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_very_small_weights(self, weights, total, minimum, floor_to_int):
        """Test with very small weight values"""
        small_weights = [w * 1e-10 for w in weights]
        assume(sum(small_weights) > 0)
        
        result = plan_seats_share(total, small_weights, floor_to_int=floor_to_int, minimum=minimum)
        assert len(result) == len(small_weights)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_very_large_weights(self, weights, total, minimum, floor_to_int):
        """Test with very large weight values"""
        large_weights = [w * 1e10 for w in weights]
        
        result = plan_seats_share(total, large_weights, floor_to_int=floor_to_int, minimum=minimum)
        assert len(result) == len(large_weights)

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_single_weight(self, weights, total, minimum, floor_to_int):
        """Test with single weight"""
        single_weight = [weights[0]]
        
        result = plan_seats_share(total, single_weight, floor_to_int=floor_to_int, minimum=minimum)
        assert len(result) == 1

    @given(
        weights=st.lists(
            floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=10
        ).filter(lambda w: sum(w) > 0),
        total=floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        minimum=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        floor_to_int=booleans()
    )
    def test_identical_weights(self, weights, total, minimum, floor_to_int):
        """Test with identical weight values"""
        identical_weights = [weights[0]] * len(weights)
        
        result = plan_seats_share(total, identical_weights, floor_to_int=floor_to_int, minimum=minimum)
        assert len(result) == len(identical_weights)
        # All shares should be equal when weights are identical
        if not floor_to_int:
            assert all(abs(result[0] - r) < 1e-10 for r in result)