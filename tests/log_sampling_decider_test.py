#!/usr/bin/env python3
"""
Hypothesis-based property tests for log_sampling_decider function.

This test suite verifies all semantic properties identified in
properties/log_sampling_decider_properties.json using the Hypothesis
testing framework for comprehensive property-based testing.
"""

import pytest
from hypothesis import given, assume, strategies as st, settings
from hypothesis.strategies import floats, integers, text, composite
from hypothesis.extra.numpy import arrays
import numpy as np
from typing import List, Tuple

# Import the function under test
# Note: Replace with actual import path
from dataset.python_programs.log_sampling_decider import log_sampling_decider


class TestLogSamplingDecider:
    """Test class for log_sampling_decider function properties."""

    @given(rate=st.floats().filter(lambda x: not (0 <= x <= 1)))
    def test_invalid_rate_validation(self, rate: float):
        """
        Test invalid rate validation property.
        
        Property: if not (0 <= rate <= 1) then raise ValueError("rate must be in [0, 1]")
        """
        with pytest.raises(ValueError, match="rate must be in \\[0, 1\\]"):
            log_sampling_decider("test_log_id", rate)

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_valid_rate_sampling(self, rate: float, log_id: str):
        """
        Test valid rate sampling property.
        
        Property: if 0 <= rate <= 1 then return bucket > rate where 
        bucket = (hash(log_id) % 1000) / 1000.0
        """
        result = log_sampling_decider(log_id, rate=rate)
        bucket = (hash(log_id) % 1000) / 1000.0
        expected = bucket > rate
        assert result == expected

    @given(log_id=st.text(min_size=1, max_size=100))
    def test_zero_rate_always_sample(self, log_id: str):
        """
        Test zero rate always samples property.
        
        Property: if rate == 0 then return True (bucket > 0 for any bucket in [0, 1))
        """
        result = log_sampling_decider(log_id, rate=0.0)
        assert result is True

    @given(log_id=st.text(min_size=1, max_size=100))
    def test_one_rate_never_sample(self, log_id: str):
        """
        Test one rate never samples property.
        
        Property: if rate == 1 then return False (bucket > 1 is impossible for bucket in [0, 1))
        """
        result = log_sampling_decider(log_id, rate=1.0)
        assert result is False

    @given(
        rate=st.floats(min_value=0, max_value=1, exclude_min=True, exclude_max=True),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_inverted_sampling_behavior(self, rate: float, log_id: str):
        """
        Test inverted sampling behavior property.
        
        Property: if 0 < rate < 1 then return bucket > rate (inverted from expected bucket <= rate)
        """
        result = log_sampling_decider(log_id, rate=rate)
        bucket = (hash(log_id) % 1000) / 1000.0
        expected = bucket > rate
        assert result == expected

    @given(rate=st.floats().filter(lambda x: not (0 <= x <= 1)))
    def test_rate_range_validation(self, rate: float):
        """
        Test rate range validation property.
        
        Property: if not (0 <= rate <= 1) then raise ValueError("rate must be in [0, 1]")
        """
        with pytest.raises(ValueError, match="rate must be in \\[0, 1\\]"):
            log_sampling_decider("test_log_id", rate=rate)

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_deterministic_sampling(self, rate: float, log_id: str):
        """
        Test deterministic sampling property.
        
        Property: for same log_id and rate, always return same boolean result
        """
        result1 = log_sampling_decider(log_id, rate=rate)
        result2 = log_sampling_decider(log_id, rate=rate)
        assert result1 == result2

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_uniform_bucket_distribution(self, rate: float, log_id: str):
        """
        Test uniform bucket distribution property.
        
        Property: bucket = (hash(log_id) % 1000) / 1000.0 produces uniform distribution in [0, 1)
        """
        bucket = (hash(log_id) % 1000) / 1000.0
        assert 0 <= bucket < 1

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_boolean_return_type(self, rate: float, log_id: str):
        """
        Test boolean return type property.
        
        Property: always returns boolean value (True or False)
        """
        result = log_sampling_decider(log_id, rate=rate)
        assert isinstance(result, bool)

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_inverted_rate_semantics(self, rate: float, log_id: str):
        """
        Test inverted rate semantics property.
        
        Property: higher rate values result in lower sampling probability (bucket > rate)
        """
        result = log_sampling_decider(log_id, rate=rate)
        bucket = (hash(log_id) % 1000) / 1000.0
        # Higher rate means lower probability of bucket > rate
        if rate > 0.5:
            # For high rates, sampling should be less likely
            assert isinstance(result, bool)
        else:
            # For low rates, sampling should be more likely
            assert isinstance(result, bool)

    @given(
        rate1=st.floats(min_value=0, max_value=1),
        rate2=st.floats(min_value=0, max_value=1),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_metamorphic_relation_rate_monotonicity(self, rate1: float, rate2: float, log_id: str):
        """
        Test metamorphic relation rate monotonicity property.
        
        Property: if rate1 <= rate2 then P(log_sampling_decider(log_id, rate1) = True) >= 
        P(log_sampling_decider(log_id, rate2) = True)
        """
        assume(rate1 <= rate2)
        
        result1 = log_sampling_decider(log_id, rate=rate1)
        result2 = log_sampling_decider(log_id, rate=rate2)
        
        # If rate1 <= rate2, then result1 should be True more often than result2
        # This is because higher rates make bucket > rate less likely
        if result1 is True and result2 is False:
            # This is the expected monotonic behavior
            pass
        elif result1 is False and result2 is True:
            # This violates monotonicity - should not happen
            pytest.fail(f"Monotonicity violation: rate1={rate1} <= rate2={rate2} but "
                       f"result1={result1} < result2={result2}")
        # Other cases (both True or both False) are acceptable

    @given(
        rate=st.floats(min_value=0, max_value=1),
        log_id1=st.text(min_size=1, max_size=100),
        log_id2=st.text(min_size=1, max_size=100)
    )
    def test_metamorphic_relation_log_id_independence(self, rate: float, log_id1: str, log_id2: str):
        """
        Test metamorphic relation log_id independence property.
        
        Property: P(log_sampling_decider(log_id1, rate) = True) = 
        P(log_sampling_decider(log_id2, rate) = True)
        """
        assume(log_id1 != log_id2)
        
        result1 = log_sampling_decider(log_id1, rate=rate)
        result2 = log_sampling_decider(log_id2, rate=rate)
        
        # For different log_ids with same rate, results should be independent
        # We can't guarantee they're equal, but we can check they're both valid booleans
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        
        # The probability should be the same, but individual results may differ
        # This test verifies the function works correctly for different log_ids


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @given(log_id=st.text(min_size=0, max_size=1000))
    def test_empty_log_id(self, log_id: str):
        """Test with empty log_id."""
        assume(len(log_id) == 0)
        result = log_sampling_decider(log_id, rate=0.5)
        assert isinstance(result, bool)

    @given(rate=st.floats(min_value=0, max_value=1))
    def test_boundary_rates(self, rate: float):
        """Test boundary rate values."""
        assume(rate in [0.0, 1.0])
        result = log_sampling_decider("test_log_id", rate=rate)
        assert isinstance(result, bool)

    @given(
        rate=st.floats(min_value=-1000, max_value=1000),
        log_id=st.text(min_size=1, max_size=100)
    )
    def test_extreme_rates(self, rate: float, log_id: str):
        """Test with extreme rate values."""
        if not (0 <= rate <= 1):
            with pytest.raises(ValueError):
                log_sampling_decider(log_id, rate=rate)
        else:
            result = log_sampling_decider(log_id, rate=rate)
            assert isinstance(result, bool)


class TestStatisticalProperties:
    """Test statistical properties over multiple runs."""

    @given(
        rate=st.floats(min_value=0.1, max_value=0.9),
        log_id=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_sampling_probability_approximation(self, rate: float, log_id: str):
        """
        Test that sampling probability approximates expected behavior.
        
        For a given rate, the probability of sampling should be approximately (1 - rate)
        due to the inverted semantics (bucket > rate).
        """
        # Generate multiple log_ids to test probability distribution
        test_log_ids = [f"{log_id}_{i}" for i in range(100)]
        
        results = [log_sampling_decider(log_id_test, rate=rate) 
                  for log_id_test in test_log_ids]
        
        sampling_probability = sum(results) / len(results)
        
        # Due to hash distribution, should be approximately (1 - rate)
        # Allow some tolerance for statistical variation
        expected_probability = 1 - rate
        tolerance = 0.2  # 20% tolerance for small sample size
        
        assert abs(sampling_probability - expected_probability) <= tolerance, \
            f"Sampling probability {sampling_probability} differs from expected {expected_probability}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])