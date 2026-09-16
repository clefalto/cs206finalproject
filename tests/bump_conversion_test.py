"""
Hypothesis-based tests for the bump_conversion function semantic properties.
Tests all properties defined in properties/bump_conversion_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, dictionaries, none, one_of

# Import the function under test
from dataset.python_programs.bump_conversion import bump_conversion


class TestBumpConversionProperties:
    """Test class for bump_conversion semantic properties."""

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0, max_value=1000), none())
    )
    def test_monotonic_increase(self, counters, key, cap):
        """
        Property: monotonic_increase
        Precondition: counters[key] is not None
        Formal: updated >= counters[key]
        """
        assume(key in counters)
        
        initial_value = counters[key]
        result = bump_conversion(counters, key, cap=cap)
        
        # The updated value should be >= the initial value
        assert result >= initial_value, f"Updated value {result} should be >= initial value {initial_value}"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_cap_respected(self, counters, key, cap):
        """
        Property: cap_respected
        Precondition: cap is not None
        Formal: updated <= cap
        """
        result = bump_conversion(counters, key, cap=cap)
        
        # The updated value should not exceed the cap
        assert result <= cap, f"Updated value {result} should be <= cap {cap}"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_key_preservation(self, counters, key, cap):
        """
        Property: key_preservation
        Precondition: counters[key] is not None
        Formal: updated >= 0
        """
        assume(key in counters)
        
        result = bump_conversion(counters, key, cap=cap)
        
        # The updated value should be non-negative
        assert result >= 0, f"Updated value {result} should be >= 0"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_non_negative_output(self, counters, key, cap):
        """
        Property: non_negative_output
        Precondition: counters[key] is not None
        Formal: updated >= 0
        """
        assume(key in counters)
        
        result = bump_conversion(counters, key, cap=cap)
        
        # The updated value should be non-negative
        assert result >= 0, f"Updated value {result} should be >= 0"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_cap_applied(self, counters, key, cap):
        """
        Property: cap_applied
        Condition: cap is not None
        Formal: updated = min(updated, cap)
        """
        # Get the value that would be set without cap logic
        current = counters.get(key, 0)
        updated_without_cap = current + 1
        
        result = bump_conversion(counters, key, cap=cap)
        
        # The result should be min(updated_without_cap, cap)
        expected = min(updated_without_cap, cap)
        assert result == expected, f"Updated value {result} should equal min({updated_without_cap}, {cap}) = {expected}"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_cap_enforced(self, counters, key, cap):
        """
        Property: cap_enforced
        Condition: cap is not None and updated > cap
        Formal: updated = cap
        """
        # Only test cases where the increment would exceed the cap
        current = counters.get(key, 0)
        assume(current + 1 > cap)
        
        result = bump_conversion(counters, key, cap=cap)
        
        # When the increment would exceed the cap, the result should equal the cap
        assert result == cap, f"Updated value {result} should equal cap {cap} when increment would exceed cap"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=none()
    )
    def test_no_cap_behavior(self, counters, key, cap):
        """
        Additional test: When cap is None, function should behave like normal increment.
        """
        current = counters.get(key, 0)
        result = bump_conversion(counters, key, cap=cap)
        
        # Without cap, result should be current + 1
        expected = current + 1
        assert result == expected, f"Updated value {result} should equal {current} + 1 = {expected}"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_counters_dict_updated(self, counters, key, cap):
        """
        Additional test: Verify that the counters dictionary is actually updated.
        """
        initial_value = counters.get(key, 0)
        result = bump_conversion(counters, key, cap=cap)
        
        # The dictionary should be updated with the new value
        assert counters[key] == result, f"Counters dict should be updated with result {result}"
        
        # The result should match what's in the dictionary
        assert result == counters[key], f"Returned result {result} should match dict value {counters[key]}"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=integers(min_value=0, max_value=1000)
    )
    def test_multiple_calls_with_cap(self, counters, key, cap):
        """
        Additional test: Multiple calls should respect the cap consistently.
        """
        # Make multiple calls and verify cap is respected each time
        for _ in range(5):
            result = bump_conversion(counters, key, cap=cap)
            assert result <= cap, f"Result {result} should not exceed cap {cap} on multiple calls"
            
            # If we've hit the cap, subsequent calls should return the cap
            if result == cap:
                next_result = bump_conversion(counters, key, cap=cap)
                assert next_result == cap, f"Once cap {cap} is reached, subsequent calls should return {cap}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])