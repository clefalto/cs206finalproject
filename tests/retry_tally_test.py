"""
Hypothesis-based property tests for retry_tally function.

This test suite exercises all semantic properties identified in 
properties/retry_tally_properties.json using the Hypothesis 
testing framework to generate comprehensive test cases.
"""

import pytest
from hypothesis import given, assume, strategies as st, example
from typing import Dict, Optional, Any


# Import the function under test
# Note: The actual function implementation should be imported here
# from your_module import retry_tally

def retry_tally(counters: Dict[Any, int], key: Any, cap: Optional[int] = None) -> int:
    """
    Increment a counter in a dictionary with optional capping.
    
    Args:
        counters: Dictionary to store counters
        key: Key to increment
        cap: Optional maximum value for the counter
    
    Returns:
        The new counter value
    
    Raises:
        TypeError: If counters is not a dictionary
    """
    if not isinstance(counters, dict):
        raise TypeError("counters must be a dictionary")
    
    # Initialize counter if key doesn't exist
    if key not in counters:
        counters[key] = 0
    
    # Increment the counter
    counters[key] += 1
    
    # Apply cap if specified and counter exceeds it
    if cap is not None and counters[key] > cap:
        counters[key] = cap
    
    return counters[key]


class TestRetryTallyProperties:
    """Test class for retry_tally semantic properties."""
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=0, max_value=1000)
    )
    @example(counters={"test": 5}, key="test", cap=3)
    @example(counters={"a": 10, "b": 20}, key="a", cap=5)
    def test_cap_clamp(self, counters, key, cap):
        """
        Property: cap_clamp
        Condition: cap is not None and counters[key] > cap
        Formal: counters[key] = cap
        """
        assume(cap is not None)
        
        # Set up the condition where counter will exceed cap after increment
        if key in counters:
            assume(counters[key] >= cap)
        else:
            # If key doesn't exist, it will be initialized to 0, then incremented to 1
            # So we need cap to be 0 for the condition to trigger
            assume(cap == 0)
        
        # Store original value for comparison
        original_value = counters.get(key, 0)
        
        result = retry_tally(counters, key, cap=cap)
        
        # After incrementing and capping, the value should equal cap
        assert result == cap, f"Expected {cap}, got {result} for key={key}, original={original_value}, cap={cap}"
        assert counters[key] == cap, f"Dictionary value should be {cap}, got {counters[key]}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1)
    )
    @example(counters={"test": 5}, key="test")
    @example(counters={"a": 0, "b": 100}, key="a")
    def test_incremental_count(self, counters, key):
        """
        Property: incremental_count
        Precondition: counters is a dictionary and key is a valid key
        Formal: retry_tally(counters, key) == previous_count + 1
        """
        # Store the previous count
        previous_count = counters.get(key, 0)
        
        result = retry_tally(counters, key)
        
        # The result should be exactly one more than the previous count
        expected = previous_count + 1
        assert result == expected, f"Expected {expected}, got {result} for key={key}, previous={previous_count}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1)
    )
    @example(counters={"existing": 5}, key="new_key")
    @example(counters={}, key="first_key")
    def test_key_initialization(self, counters, key):
        """
        Property: key_initialization
        Precondition: key not in counters
        Formal: retry_tally(counters, key) == 1
        """
        assume(key not in counters)
        
        result = retry_tally(counters, key)
        
        # When key doesn't exist, it should be initialized to 1
        assert result == 1, f"Expected 1, got {result} for new key={key}"
        assert counters[key] == 1, f"Dictionary should have key={key} with value 1, got {counters[key]}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    @example(counters={"test": 5}, key="test", cap=None)
    @example(counters={"test": 2}, key="test", cap=10)
    def test_monotonic_increase(self, counters, key, cap):
        """
        Property: monotonic_increase
        Precondition: counters[key] exists and cap is None or counters[key] < cap
        Formal: retry_tally(counters, key) > previous_count
        """
        # Initialize key if it doesn't exist
        if key not in counters:
            counters[key] = 0
        
        previous_count = counters[key]
        
        # Only test when the condition is met
        assume(cap is None or previous_count < cap)
        
        result = retry_tally(counters, key, cap=cap)
        
        # The result should be greater than the previous count
        assert result > previous_count, f"Expected increase from {previous_count}, got {result} for key={key}, cap={cap}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=0, max_value=1000)
    )
    @example(counters={"test": 5}, key="test", cap=10)
    @example(counters={"test": 15}, key="test", cap=10)
    def test_cap_bounded(self, counters, key, cap):
        """
        Property: cap_bounded
        Precondition: cap is not None
        Formal: retry_tally(counters, key, cap=cap) <= cap
        """
        assume(cap is not None)
        
        result = retry_tally(counters, key, cap=cap)
        
        # The result should never exceed the cap
        assert result <= cap, f"Expected result <= {cap}, got {result} for key={key}, cap={cap}"
        assert counters[key] <= cap, f"Dictionary value should be <= {cap}, got {counters[key]}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    @example(counters={"test": 5}, key="test", cap=None)
    @example(counters={"test": 3}, key="test", cap=10)
    def test_dictionary_mutation(self, counters, key, cap):
        """
        Property: dictionary_mutation
        Precondition: counters is mutable dictionary
        Formal: counters[key] is updated in-place
        """
        # Store reference to original dictionary
        original_id = id(counters)
        
        # Store original value
        original_value = counters.get(key, 0)
        
        result = retry_tally(counters, key, cap=cap)
        
        # Dictionary should be the same object (in-place mutation)
        assert id(counters) == original_id, "Dictionary should be mutated in-place"
        
        # Dictionary should contain the updated value
        assert key in counters, f"Key {key} should exist in dictionary"
        assert counters[key] == result, f"Dictionary value should equal return value: {result}, got {counters[key]}"
        
        # Value should have increased (unless capped at original value)
        if cap is None or original_value < cap:
            assert counters[key] > original_value, f"Value should increase from {original_value}, got {counters[key]}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    @example(counters={"test": 5}, key="test", cap=None)
    @example(counters={"test": 8}, key="test", cap=5)
    def test_return_value_consistency(self, counters, key, cap):
        """
        Property: return_value_consistency
        Precondition: counters[key] is accessible
        Formal: return value == counters[key]
        """
        # Ensure key exists in dictionary for accessibility
        if key not in counters:
            counters[key] = 0
        
        result = retry_tally(counters, key, cap=cap)
        
        # Return value should equal the dictionary value
        assert result == counters[key], f"Return value {result} should equal dictionary value {counters[key]}"
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    @example(counters={"test": 0}, key="test", cap=None)
    @example(counters={"test": 5}, key="test", cap=10)
    def test_non_negative_count(self, counters, key, cap):
        """
        Property: non_negative_count
        Precondition: counters[key] >= 0
        Formal: retry_tally(counters, key) >= 0
        """
        # Initialize key if it doesn't exist (starting at 0 which is non-negative)
        if key not in counters:
            counters[key] = 0
        
        # Ensure precondition: existing value is non-negative
        assume(counters[key] >= 0)
        
        result = retry_tally(counters, key, cap=cap)
        
        # Result should always be non-negative
        assert result >= 0, f"Expected non-negative result, got {result} for key={key}, cap={cap}"
        assert counters[key] >= 0, f"Dictionary value should be non-negative, got {counters[key]}"


class TestRetryTallyEdgeCases:
    """Additional edge case tests for retry_tally."""
    
    @given(
        counters=st.dictionaries(st.integers(), st.integers(min_value=0, max_value=100)),
        key=st.integers(),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=100))
    )
    def test_integer_keys(self, counters, key, cap):
        """Test with integer keys."""
        result = retry_tally(counters, key, cap=cap)
        
        assert isinstance(result, int)
        assert result == counters[key]
        if cap is not None:
            assert result <= cap
    
    @given(
        counters=st.dictionaries(st.text(), st.integers(min_value=0, max_value=10)),
        key=st.text(),
        cap=st.integers(min_value=0, max_value=20)
    )
    def test_string_keys(self, counters, key, cap):
        """Test with string keys."""
        result = retry_tally(counters, key, cap=cap)
        
        assert isinstance(result, int)
        assert result == counters[key]
        assert result <= cap
    
    def test_type_error_for_non_dict(self):
        """Test that TypeError is raised for non-dictionary counters."""
        with pytest.raises(TypeError, match="counters must be a dictionary"):
            retry_tally("not_a_dict", "key")
        
        with pytest.raises(TypeError, match="counters must be a dictionary"):
            retry_tally([1, 2, 3], "key")
        
        with pytest.raises(TypeError, match="counters must be a dictionary"):
            retry_tally(None, "key")
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=100)),
        key=st.text(min_size=1)
    )
    def test_multiple_calls_consistency(self, counters, key):
        """Test that multiple calls maintain consistency."""
        # First call
        result1 = retry_tally(counters, key)
        expected1 = counters.get(key, 0) + 1
        assert result1 == expected1
        
        # Second call
        result2 = retry_tally(counters, key)
        expected2 = result1 + 1
        assert result2 == expected2
        
        # Dictionary should reflect the final value
        assert counters[key] == result2
    
    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0, max_value=100)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=1, max_value=10)
    )
    def test_capping_behavior(self, counters, key, cap):
        """Test detailed capping behavior."""
        # Set up so that after a few increments, we'll hit the cap
        if key in counters:
            counters[key] = max(0, cap - 2)  # Start close to cap
        
        # Increment until we hit the cap
        for i in range(5):  # Try multiple increments
            result = retry_tally(counters, key, cap=cap)
            
            # Should never exceed cap
            assert result <= cap
            
            # Should stop increasing once cap is reached
            if result == cap:
                # Additional calls should keep it at cap
                for _ in range(3):
                    assert retry_tally(counters, key, cap=cap) == cap
                break


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])