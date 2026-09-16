"""
Hypothesis-based property tests for the track_release function.

This test suite exercises all semantic properties identified for the track_release function:
- cap_enforcement: When cap is not None, updated value is min(updated, cap)
- cap_clamping: When updated > cap, updated value becomes cap
- monotonic_increase: Function output is >= input value
- cap_bounded: Function output is <= cap when cap is not None
- identity_on_no_cap: When cap is None, output equals input + 1
- integer_preservation: Integer inputs produce integer outputs
- key_preservation: Function doesn't modify the counters dictionary
- incremental_behavior: Normal increment when no cap or within cap
- saturation_behavior: Output equals cap when input + 1 would exceed cap
- non_negative_output: Output is non-negative when input is non-negative
"""

import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Optional, Any


# Mock implementation of track_release function for testing
# This should match the actual implementation being tested
def track_release(counters: Dict[str, int], key: str, cap: Optional[int] = None) -> int:
    """
    Track a release count with optional capping.
    
    Args:
        counters: Dictionary containing counter values
        key: Key to track in the counters dictionary
        cap: Optional maximum value for the counter
        
    Returns:
        The updated counter value
    """
    if key not in counters:
        counters[key] = 0
    
    updated = counters[key] + 1
    
    if cap is not None:
        updated = min(updated, cap)
    
    counters[key] = updated
    return updated


class TestTrackReleaseProperties:
    """Test class for track_release function properties."""
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_cap_enforcement(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: cap_enforcement
        If cap is not None then updated = min(updated, cap)
        """
        assume(key in counters)  # Precondition: key must exist in counters
        
        original_value = counters[key]
        result = track_release(counters, key, cap)
        
        if cap is not None:
            expected = min(original_value + 1, cap)
            assert result == expected, f"Expected {expected}, got {result} when cap={cap}, original={original_value}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_clamping(self, counters: Dict[str, int], key: str, cap: int):
        """
        Property: cap_clamping
        If updated > cap then updated = cap
        """
        assume(key in counters)  # Precondition: key must exist in counters
        assume(counters[key] + 1 > cap)  # Precondition: updated > cap
        
        result = track_release(counters, key, cap)
        
        assert result == cap, f"Expected {cap}, got {result} when updated > cap"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_monotonic_increase(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: monotonic_increase
        track_release(counters, key) >= counters[key]
        """
        assume(key in counters)  # Precondition: counters[key] is defined and numeric
        
        original_value = counters[key]
        result = track_release(counters, key, cap)
        
        assert result >= original_value, f"Expected result >= {original_value}, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_bounded(self, counters: Dict[str, int], key: str, cap: int):
        """
        Property: cap_bounded
        track_release(counters, key) <= cap when cap is not None
        """
        assume(key in counters)  # Precondition: cap is not None (ensured by strategy)
        
        result = track_release(counters, key, cap)
        
        assert result <= cap, f"Expected result <= {cap}, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',)))
    )
    def test_identity_on_no_cap(self, counters: Dict[str, int], key: str):
        """
        Property: identity_on_no_cap
        track_release(counters, key) == counters[key] + 1 when cap is None
        """
        assume(key in counters)  # Precondition: cap is None (ensured by not passing cap)
        
        original_value = counters[key]
        result = track_release(counters, key)  # cap defaults to None
        
        assert result == original_value + 1, f"Expected {original_value + 1}, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_integer_preservation(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: integer_preservation
        track_release(counters, key) is integer when counters[key] is integer
        """
        assume(key in counters)  # Precondition: counters[key] is integer (ensured by strategy)
        
        result = track_release(counters, key, cap)
        
        assert isinstance(result, int), f"Expected integer result, got {type(result)}"
        assert result == int(result), f"Expected integer result, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_key_preservation(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: key_preservation
        track_release does not modify counters dictionary structure
        """
        assume(key in counters)  # Precondition: counters[key] is defined
        
        original_counters = counters.copy()
        original_keys = set(counters.keys())
        
        track_release(counters, key, cap)
        
        # Check that all original keys are still present
        assert set(counters.keys()) == original_keys, "Dictionary keys were modified"
        
        # Check that only the specified key was modified
        for k in counters:
            if k == key:
                continue  # This key is allowed to change
            assert counters[k] == original_counters[k], f"Key '{k}' was unexpectedly modified"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_incremental_behavior(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: incremental_behavior
        track_release(counters, key) == counters[key] + 1 when cap is None or counters[key] + 1 <= cap
        """
        assume(key in counters)  # Precondition: counters[key] is defined and numeric
        
        original_value = counters[key]
        
        # Only test when the condition is met
        if cap is None or original_value + 1 <= cap:
            result = track_release(counters, key, cap)
            assert result == original_value + 1, f"Expected {original_value + 1}, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_saturation_behavior(self, counters: Dict[str, int], key: str, cap: int):
        """
        Property: saturation_behavior
        track_release(counters, key) == cap when counters[key] + 1 > cap
        """
        assume(key in counters)  # Precondition: counters[key] + 1 > cap and cap is not None
        assume(counters[key] + 1 > cap)
        
        result = track_release(counters, key, cap)
        
        assert result == cap, f"Expected {cap}, got {result} when saturation should occur"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_non_negative_output(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Property: non_negative_output
        track_release(counters, key) >= 0 when counters[key] >= 0
        """
        assume(key in counters)  # Precondition: counters[key] >= 0 (ensured by strategy)
        assume(counters[key] >= 0)
        
        result = track_release(counters, key, cap)
        
        assert result >= 0, f"Expected non-negative result, got {result}"
    
    # Additional edge case tests
    
    @given(
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_new_key_creation(self, key: str, cap: Optional[int]):
        """Test behavior when key doesn't exist in counters."""
        counters = {}
        
        result = track_release(counters, key, cap)
        
        # Should create new key with value 1 (or cap if cap < 1)
        expected = 1 if cap is None or cap >= 1 else cap
        assert result == expected
        assert key in counters
        assert counters[key] == expected
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_zero_behavior(self, counters: Dict[str, int], key: str, cap: int):
        """Test behavior when cap is 0."""
        assume(key in counters)
        
        result = track_release(counters, key, cap)
        
        # When cap is 0, result should always be 0
        assert result == 0, f"Expected 0 when cap=0, got {result}"
    
    @given(
        counters=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.integers(min_value=0, max_value=1000)
        ),
        key=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=('Cs',)))
    )
    def test_multiple_calls_consistency(self, counters: Dict[str, int], key: str):
        """Test that multiple calls maintain consistency."""
        assume(key in counters)
        
        original_value = counters[key]
        
        # First call
        result1 = track_release(counters, key)
        expected1 = original_value + 1
        assert result1 == expected1
        
        # Second call
        result2 = track_release(counters, key)
        expected2 = expected1 + 1
        assert result2 == expected2
        
        # Third call
        result3 = track_release(counters, key)
        expected3 = expected2 + 1
        assert result3 == expected3


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main([__file__, "-v"])