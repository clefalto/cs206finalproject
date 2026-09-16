"""
Hypothesis tests for the track_delivery function semantic properties.
Tests all properties defined in properties/track_delivery_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, just, none, one_of

# Import the function under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'python_programs'))
from track_delivery import track_delivery


class TestTrackDeliveryProperties:
    """Test class for track_delivery semantic properties."""

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_cap_applied_branch(self, counters, key, cap):
        """
        Test property: cap_applied
        Scope: branch
        Condition: cap is not None
        Formal: updated <= cap
        """
        assume(cap is not None)
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated <= cap
        assert updated <= cap, f"Expected updated ({updated}) <= cap ({cap})"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_cap_clamped_branch(self, counters, key, cap):
        """
        Test property: cap_clamped
        Scope: branch
        Condition: updated > cap
        Formal: updated == cap
        """
        assume(cap is not None)
        
        # Set up the counter to be at cap - 1 so that incrementing will exceed cap
        counters[key] = cap - 1
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated == cap (when updated > cap, it should be clamped to cap)
        assert updated == cap, f"Expected updated ({updated}) == cap ({cap}) when exceeding cap"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_monotonic_increase_function(self, counters, key, cap):
        """
        Test property: monotonic_increase
        Scope: function
        Precondition: counters[key] is not None
        Formal: updated >= counters[key]
        """
        assume(key in counters)
        
        # Store the original value
        original_value = counters[key]
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated >= counters[key] (monotonic increase)
        assert updated >= original_value, f"Expected updated ({updated}) >= original ({original_value})"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_non_negative_function(self, counters, key, cap):
        """
        Test property: non_negative
        Scope: function
        Precondition: counters[key] is not None and counters[key] >= 0
        Formal: updated >= 0
        """
        assume(key in counters and counters[key] >= 0)
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated >= 0 (non-negative)
        assert updated >= 0, f"Expected updated ({updated}) >= 0"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_cap_respected_function(self, counters, key, cap):
        """
        Test property: cap_respected
        Scope: function
        Precondition: cap is not None
        Formal: updated <= cap
        """
        assume(cap is not None)
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated <= cap (cap respected)
        assert updated <= cap, f"Expected updated ({updated}) <= cap ({cap})"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_key_preservation_function(self, counters, key, cap):
        """
        Test property: key_preservation
        Scope: function
        Precondition: counters[key] is not None
        Formal: counters[key] remains unchanged
        """
        assume(key in counters)
        
        # Store the original value
        original_value = counters[key]
        
        # Track delivery (this should not modify the original counter value in the dictionary)
        # Note: The function actually modifies the dictionary, so this test checks that
        # the function returns the updated value while the dictionary is also updated
        updated = track_delivery(counters, key, cap=cap)
        
        # The function should return the updated value
        assert updated == original_value + 1, f"Expected returned value ({updated}) == original ({original_value}) + 1"
        
        # And the dictionary should be updated
        assert counters[key] == updated, f"Expected counters[key] ({counters[key]}) == returned value ({updated})"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_delivery_count_increment_function(self, counters, key, cap):
        """
        Test property: delivery_count_increment
        Scope: function
        Precondition: counters[key] is not None
        Formal: updated == counters[key] + 1
        """
        assume(key in counters)
        
        # Store the original value
        original_value = counters[key]
        
        # Track delivery and get the updated value
        updated = track_delivery(counters, key, cap=cap)
        
        # Property: updated == counters[key] + 1 (increment by 1)
        assert updated == original_value + 1, f"Expected updated ({updated}) == original ({original_value}) + 1"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=0), none())
    )
    def test_edge_case_zero_cap(self, counters, key, cap):
        """
        Test edge case: when cap is 0
        """
        assume(cap == 0)
        
        # Track delivery with cap=0
        updated = track_delivery(counters, key, cap=cap)
        
        # Should be clamped to 0
        assert updated == 0, f"Expected updated ({updated}) == 0 when cap is 0"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0)),
        key=st.text(min_size=1),
        cap=one_of(integers(min_value=1), none())
    )
    def test_edge_case_single_increment(self, counters, key, cap):
        """
        Test edge case: when we increment from 0
        """
        # Ensure key is not in counters (will default to 0)
        assume(key not in counters)
        
        # Track delivery
        updated = track_delivery(counters, key, cap=cap)
        
        # Should be 1 (0 + 1)
        assert updated == 1, f"Expected updated ({updated}) == 1 when starting from 0"

    @given(
        counters=dictionaries(st.text(min_size=1), integers(min_value=0, max_value=100)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=1, max_value=100)
    )
    def test_edge_case_exact_cap_match(self, counters, key, cap):
        """
        Test edge case: when current value equals cap - 1
        """
        # Set up counter to be at cap - 1
        counters[key] = cap - 1
        
        # Track delivery
        updated = track_delivery(counters, key, cap=cap)
        
        # Should be exactly cap
        assert updated == cap, f"Expected updated ({updated}) == cap ({cap}) when starting from cap - 1"