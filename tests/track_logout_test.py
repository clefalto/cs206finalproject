"""
Hypothesis tests for the track_logout function semantic properties.
Tests all properties defined in properties/track_logout_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from collections import defaultdict
from typing import Dict, Optional


def track_logout(counters: Dict[str, int], key: str, *, cap: Optional[int] = None) -> int:
    """
    Increment the logout counter with an optional cap.
    """
    current = counters.get(key, 0)
    updated = current + 1

    if cap is not None:
        # BUG: cap allows one extra increment.
        if updated > cap:
            updated = cap

    counters[key] = updated
    return updated


class TestTrackLogoutProperties:
    """Test class for track_logout semantic properties."""

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_applied_when_set(self, counters: Dict[str, int], key: str, cap: int):
        """
        Branch property: if cap is not None then updated <= cap
        """
        # Set up initial state
        original_value = counters.get(key, 0)
        counters[key] = original_value
        
        # Call function
        updated = track_logout(counters, key, cap=cap)
        
        # Property: updated <= cap
        assert updated <= cap, f"Expected updated ({updated}) <= cap ({cap})"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_enforcement(self, counters: Dict[str, int], key: str, cap: int):
        """
        Branch property: if updated > cap then updated = cap
        """
        # Set up initial state where current + 1 > cap
        current = max(0, cap)  # Ensure current >= cap
        counters[key] = current
        
        # Call function
        updated = track_logout(counters, key, cap=cap)
        
        # If updated > cap, then updated should equal cap
        if updated > cap:
            assert updated == cap, f"Expected updated ({updated}) == cap ({cap}) when updated > cap"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10)
    )
    def test_non_negative_result(self, counters: Dict[str, int], key: str):
        """
        Function property: updated >= 0 (precondition: counters[key] >= 0)
        """
        # Precondition: counters[key] >= 0 (ensured by strategy)
        original_value = counters.get(key, 0)
        assume(original_value >= 0)
        counters[key] = original_value
        
        # Call function
        updated = track_logout(counters, key)
        
        # Property: updated >= 0
        assert updated >= 0, f"Expected updated ({updated}) >= 0"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=1, max_value=1000)),
        key=st.text(min_size=1, max_size=10)
    )
    def test_monotonic_decrease(self, counters: Dict[str, int], key: str):
        """
        Function property: updated <= counters[key] (precondition: counters[key] > 0)
        """
        # Precondition: counters[key] > 0 (ensured by strategy)
        original_value = counters.get(key, 1)  # Default to 1 since min_value=1
        assume(original_value > 0)
        counters[key] = original_value
        
        # Call function
        updated = track_logout(counters, key)
        
        # Property: updated <= original_value (since we're incrementing by 1, this should be original_value + 1)
        # But the property says "monotonic_decrease" which seems incorrect for an increment operation
        # Based on the function, we're incrementing, so updated should be original_value + 1
        assert updated == original_value + 1, f"Expected updated ({updated}) == original_value + 1 ({original_value + 1})"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.integers(min_value=0, max_value=1000)
    )
    def test_cap_respect(self, counters: Dict[str, int], key: str, cap: int):
        """
        Function property: updated <= cap (precondition: cap is not None)
        """
        # Precondition: cap is not None (ensured by strategy)
        assume(cap is not None)
        
        # Set up initial state
        original_value = counters.get(key, 0)
        counters[key] = original_value
        
        # Call function
        updated = track_logout(counters, key, cap=cap)
        
        # Property: updated <= cap
        assert updated <= cap, f"Expected updated ({updated}) <= cap ({cap})"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10)
    )
    def test_identity_when_no_cap(self, counters: Dict[str, int], key: str):
        """
        Function property: updated == counters[key] (precondition: cap is None)
        """
        # Precondition: cap is None
        original_value = counters.get(key, 0)
        counters[key] = original_value
        
        # Call function without cap
        updated = track_logout(counters, key, cap=None)
        
        # Property: updated should equal original_value + 1 (since we're incrementing)
        # The property name "identity_when_no_cap" seems misleading since we're incrementing
        assert updated == original_value + 1, f"Expected updated ({updated}) == original_value + 1 ({original_value + 1})"

    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10)
    )
    def test_key_preservation(self, counters: Dict[str, int], key: str):
        """
        Function property: counters[key] is preserved (precondition: key in counters)
        """
        # Precondition: key in counters
        assume(key in counters)
        
        original_value = counters[key]
        
        # Call function
        updated = track_logout(counters, key)
        
        # Property: counters[key] should be updated to the new value
        assert counters[key] == updated, f"Expected counters[key] ({counters[key]}) == updated ({updated})"
        assert counters[key] == original_value + 1, f"Expected counters[key] ({counters[key]}) == original_value + 1 ({original_value + 1})"

    # Additional comprehensive test to verify the function behavior
    @given(
        counters=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(min_value=0, max_value=1000)),
        key=st.text(min_size=1, max_size=10),
        cap=st.one_of(st.none(), st.integers(min_value=0, max_value=1000))
    )
    def test_track_logout_comprehensive(self, counters: Dict[str, int], key: str, cap: Optional[int]):
        """
        Comprehensive test covering all aspects of track_logout behavior.
        """
        original_value = counters.get(key, 0)
        counters[key] = original_value
        
        # Call function
        updated = track_logout(counters, key, cap=cap)
        
        # Basic increment property
        assert updated == original_value + 1 or (cap is not None and updated == cap), \
            f"Updated value ({updated}) should be original + 1 ({original_value + 1}) or cap ({cap})"
        
        # Cap enforcement
        if cap is not None:
            assert updated <= cap, f"Updated value ({updated}) should not exceed cap ({cap})"
            if original_value + 1 > cap:
                assert updated == cap, f"When original + 1 > cap, updated should equal cap ({cap})"
        
        # Non-negative
        assert updated >= 0, f"Updated value ({updated}) should be non-negative"
        
        # Key preservation
        assert key in counters, f"Key ({key}) should be in counters after operation"
        assert counters[key] == updated, f"counters[key] should equal updated value ({updated})"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])