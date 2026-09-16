"""
Hypothesis-based property tests for the offer_expiry function.

This test file exercises all semantic properties identified in
properties/offer_expiry_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, tuples, dictionaries, just, one_of
from typing import Any, Dict, Optional, Tuple, Union

# Import the function under test
from dataset.python_programs.offer_expiry import offer_expiry


# Define strategies for generating test data
@st.composite
def store_strategy(draw):
    """Generate a store dictionary with valid offer records."""
    # Generate a dictionary where keys are strings and values are (value, deadline) tuples
    # Use integers for both value and deadline for simplicity
    store = draw(dictionaries(
        keys=st.text(min_size=1, max_size=10),
        values=tuples(
            st.integers(min_value=0, max_value=1000),  # value
            st.integers(min_value=0, max_value=1000)   # deadline
        ),
        min_size=0,
        max_size=10
    ))
    return store


@st.composite
def valid_offer_record_strategy(draw):
    """Generate a valid offer record (value, deadline) tuple."""
    value = draw(st.integers(min_value=0, max_value=1000))
    deadline = draw(st.integers(min_value=0, max_value=1000))
    return (value, deadline)


class TestOfferExpiryProperties:
    """Test class for offer_expiry semantic properties."""

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_default_on_missing(self, store, key, now, default):
        """
        Property: default_on_missing
        When record is None, offer_expiry should return default.
        """
        # Ensure the key is not in the store (record is None)
        assume(key not in store)
        
        result = offer_expiry(store, key, now, default=default)
        assert result == default, f"Expected default {default}, got {result}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_default_on_expired(self, store, key, now, default):
        """
        Property: default_on_expired
        When now > deadline, offer_expiry should return default.
        """
        # Ensure the key exists in store and now > deadline
        assume(key in store)
        value, deadline = store[key]
        assume(now > deadline)
        
        result = offer_expiry(store, key, now, default=default)
        assert result == default, f"Expected default {default}, got {result}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_value_on_valid(self, store, key, now, default):
        """
        Property: value_on_valid
        When record exists and now <= deadline, offer_expiry should return value.
        """
        # Ensure the key exists in store and now <= deadline
        assume(key in store)
        value, deadline = store[key]
        assume(now <= deadline)
        
        result = offer_expiry(store, key, now, default=default)
        assert result == value, f"Expected value {value}, got {result}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_boundary_inclusion(self, store, key, default):
        """
        Property: boundary_inclusion
        When record exists and now == deadline, offer_expiry should return value.
        """
        # Ensure the key exists in store
        assume(key in store)
        value, deadline = store[key]
        now = deadline  # Boundary case: now == deadline
        
        result = offer_expiry(store, key, now, default=default)
        assert result == value, f"Expected value {value} at boundary, got {result}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now1=st.integers(min_value=0, max_value=1000),
        now2=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_monotonic_expiry(self, store, key, now1, now2, default):
        """
        Property: monotonic_expiry
        If offer_expiry returns default at time now1, it should also return default at any later time now2.
        """
        # Ensure the key exists in store and now1 <= now2
        assume(key in store)
        assume(now1 <= now2)
        
        result1 = offer_expiry(store, key, now1, default=default)
        result2 = offer_expiry(store, key, now2, default=default)
        
        # If result1 is default, then result2 must also be default
        if result1 == default:
            assert result2 == default, f"Monotonicity violated: got {result1} at {now1}, but {result2} at {now2}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_idempotent(self, store, key, now, default):
        """
        Property: idempotent
        Calling offer_expiry multiple times with the same arguments should return the same result.
        """
        # Ensure the key exists in store
        assume(key in store)
        
        result1 = offer_expiry(store, key, now, default=default)
        result2 = offer_expiry(store, key, now, default=default)
        
        assert result1 == result2, f"Idempotency violated: {result1} != {result2}"

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_default_fallback(self, store, key, now, default):
        """
        Property: default_fallback
        offer_expiry should always return either the default or the stored value.
        """
        result = offer_expiry(store, key, now, default=default)
        
        if key in store:
            value, deadline = store[key]
            if now <= deadline:
                expected_values = {value}
            else:
                expected_values = {default}
        else:
            expected_values = {default}
        
        assert result in expected_values, f"Result {result} not in expected values {expected_values}"


class TestOfferExpiryEdgeCases:
    """Additional edge case tests for offer_expiry."""

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.none() | st.integers(min_value=0, max_value=1000)
    )
    def test_with_none_default(self, store, key, now, default):
        """Test behavior when default is None."""
        result = offer_expiry(store, key, now, default=default)
        
        if key not in store:
            assert result is None
        else:
            value, deadline = store[key]
            if now <= deadline:
                assert result == value
            else:
                assert result is None

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_empty_store(self, store, key, now, default):
        """Test behavior with empty store."""
        empty_store = {}
        result = offer_expiry(empty_store, key, now, default=default)
        assert result == default

    @given(
        store=store_strategy(),
        key=st.text(min_size=1, max_size=10),
        now=st.integers(min_value=0, max_value=1000),
        default=st.integers(min_value=0, max_value=1000)
    )
    def test_boundary_values(self, store, key, now, default):
        """Test with boundary values for integers."""
        # Test with minimum and maximum integer values
        min_val, max_val = 0, 1000
        
        # Create a store with boundary values
        test_store = {
            "min_key": (min_val, min_val),
            "max_key": (max_val, max_val),
            "mixed_key": (min_val, max_val)
        }
        
        # Test each key in the boundary store
        for test_key, (value, deadline) in test_store.items():
            result = offer_expiry(test_store, test_key, now, default=default)
            
            if now <= deadline:
                assert result == value
            else:
                assert result == default


if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main([__file__, "-v"])