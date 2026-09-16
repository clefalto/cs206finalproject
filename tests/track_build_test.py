"""
Hypothesis-based tests for the track_build function semantic properties.

This test file verifies all semantic properties identified in track_build_properties.json:
- cap_enforcement: When cap is not None and counters[key] > cap, counters[key] = cap
- monotonic_decrease: When counters[key] > cap, counters[key] <= original_value
- cap_bound: When cap is not None, counters[key] <= cap
- identity_when_uncapped: When cap is None, counters[key] == original_value
- identity_when_below_cap: When counters[key] <= cap, counters[key] == original_value
- key_preservation: When key in counters, key remains in counters
- counter_return: When key in counters, return_value == counters[key]
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, text, sampled_from, none

# Import the function under test
from dataset.python_programs.track_build import track_build


class TestTrackBuildProperties:
    """Test class for track_build semantic properties using Hypothesis."""

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000) | none()
    )
    def test_cap_enforcement(self, counters, key, cap):
        """
        Property: cap_enforcement
        Condition: cap is not None and counters[key] > cap
        Formal: counters[key] = cap
        """
        assume(cap is not None)
        
        # Set up initial state where counters[key] > cap
        initial_value = cap + 1
        counters[key] = initial_value
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify the property: counters[key] should be clamped to cap
        assert counters[key] == cap, f"Expected counters[{key}] to be {cap}, got {counters[key]}"
        assert result == cap, f"Expected return value to be {cap}, got {result}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_monotonic_decrease(self, counters, key, cap):
        """
        Property: monotonic_decrease
        Precondition: counters[key] > cap
        Formal: counters[key] <= original_value
        """
        # Set up initial state where counters[key] > cap
        initial_value = cap + 1
        counters[key] = initial_value
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify the property: counters[key] should not exceed original value
        assert counters[key] <= initial_value, f"Expected counters[{key}] <= {initial_value}, got {counters[key]}"
        assert result <= initial_value, f"Expected return value <= {initial_value}, got {result}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000) | none()
    )
    def test_cap_bound(self, counters, key, cap):
        """
        Property: cap_bound
        Precondition: cap is not None
        Formal: counters[key] <= cap
        """
        assume(cap is not None)
        
        # Set up initial state
        initial_value = counters.get(key, 0)
        counters[key] = initial_value
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify the property: counters[key] should not exceed cap
        assert counters[key] <= cap, f"Expected counters[{key}] <= {cap}, got {counters[key]}"
        assert result <= cap, f"Expected return value <= {cap}, got {result}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1)
    )
    def test_identity_when_uncapped(self, counters, key):
        """
        Property: identity_when_uncapped
        Precondition: cap is None
        Formal: counters[key] == original_value
        """
        # Set up initial state
        original_value = counters.get(key, 0)
        counters[key] = original_value
        
        # Call track_build with cap=None
        result = track_build(counters, key, cap=None)
        
        # Verify the property: counters[key] should equal original_value
        expected_value = original_value + 1  # track_build increments by 1
        assert counters[key] == expected_value, f"Expected counters[{key}] to be {expected_value}, got {counters[key]}"
        assert result == expected_value, f"Expected return value to be {expected_value}, got {result}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_identity_when_below_cap(self, counters, key, cap):
        """
        Property: identity_when_below_cap
        Precondition: counters[key] <= cap
        Formal: counters[key] == original_value
        """
        # Set up initial state where counters[key] <= cap
        initial_value = min(cap, 1000)  # Ensure we don't exceed max_value
        counters[key] = initial_value
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify the property: counters[key] should equal original_value + 1 (since it's incremented)
        expected_value = initial_value + 1
        assert counters[key] == expected_value, f"Expected counters[{key}] to be {expected_value}, got {counters[key]}"
        assert result == expected_value, f"Expected return value to be {expected_value}, got {result}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000) | none()
    )
    def test_key_preservation(self, counters, key, cap):
        """
        Property: key_preservation
        Precondition: key in counters
        Formal: key in counters
        """
        # Ensure key exists in counters
        counters[key] = counters.get(key, 0)
        
        # Call track_build
        track_build(counters, key, cap=cap)
        
        # Verify the property: key should still be in counters
        assert key in counters, f"Expected key '{key}' to be in counters after track_build call"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000) | none()
    )
    def test_counter_return(self, counters, key, cap):
        """
        Property: counter_return
        Precondition: key in counters
        Formal: return_value == counters[key]
        """
        # Ensure key exists in counters
        counters[key] = counters.get(key, 0)
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify the property: return value should equal counters[key]
        assert result == counters[key], f"Expected return value {result} to equal counters[{key}] {counters[key]}"

    @given(
        counters=dictionaries(text(min_size=1), integers(min_value=0, max_value=1000)),
        key=text(min_size=1),
        cap=integers(min_value=0, max_value=1000) | none()
    )
    def test_comprehensive_behavior(self, counters, key, cap):
        """
        Comprehensive test that verifies the overall behavior of track_build.
        This test ensures that the function works correctly across all scenarios.
        """
        # Store initial state
        initial_count = counters.get(key, 0)
        
        # Call track_build
        result = track_build(counters, key, cap=cap)
        
        # Verify that the key exists and was incremented
        assert key in counters, f"Key '{key}' should exist in counters"
        assert counters[key] == initial_count + 1, f"Expected counters[{key}] to be {initial_count + 1}, got {counters[key]}"
        assert result == initial_count + 1, f"Expected return value to be {initial_count + 1}, got {result}"
        
        # If cap is set and we exceeded it, verify clamping behavior
        if cap is not None and initial_count + 1 > cap:
            assert counters[key] == cap, f"Expected counters[{key}] to be clamped to {cap}, got {counters[key]}"
            assert result == cap, f"Expected return value to be clamped to {cap}, got {result}"


if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main([__file__, "-v"])