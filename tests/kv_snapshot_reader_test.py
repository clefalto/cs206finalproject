#!/usr/bin/env python3
"""
Hypothesis-based tests for kv_snapshot_reader semantic properties.
Tests all properties defined in properties/kv_snapshot_reader_properties.json.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Tuple, Any, Optional


def kv_snapshot_reader(snapshot: List[Tuple[Any, Any]], key: Any, default: Any = None) -> Any:
    """
    Reference implementation of kv_snapshot_reader for testing.
    Assumes snapshot is sorted by key.
    """
    for k, v in snapshot:
        if k == key:
            return v
        elif k > key:
            break
    return default


class TestKvSnapshotReaderProperties:
    """Test class for kv_snapshot_reader semantic properties."""

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=100
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=1000, deadline=None)
    def test_key_found_return_branch(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test branch property: when k == key, function returns v.
        Scope: branch, condition: k == key, property: key_found_return
        """
        # Find if key exists in snapshot
        key_found = False
        expected_value = None
        
        for k, v in snapshot:
            if k == key:
                key_found = True
                expected_value = v
                break
            elif k > key:
                break
        
        if key_found:
            result = kv_snapshot_reader(snapshot, key, default)
            assert result == expected_value, f"Expected {expected_value}, got {result} for key {key} in snapshot {snapshot}"

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=100
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=1000, deadline=None)
    def test_early_termination_branch(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test branch property: when k > key, function returns default.
        Scope: branch, condition: k > key, property: early_termination
        """
        # Check if there's any key in snapshot greater than our search key
        has_greater_key = any(k > key for k, v in snapshot)
        
        if has_greater_key:
            result = kv_snapshot_reader(snapshot, key, default)
            # If we encounter k > key before finding the key, we should return default
            # But we need to be careful - we only return default if we don't find the key first
            key_exists = any(k == key for k, v in snapshot)
            
            if not key_exists:
                # Find the first key > key to verify early termination
                for k, v in snapshot:
                    if k > key:
                        assert result == default, f"Expected early termination with default {default}, got {result}"
                        break

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=50
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=500, deadline=None)
    def test_key_not_found_default_function(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test function property: when key not in snapshot, return default.
        Scope: function, precondition: key not in [k for k, v in snapshot], property: key_not_found_default
        """
        assume(key not in [k for k, v in snapshot])
        
        result = kv_snapshot_reader(snapshot, key, default)
        assert result == default, f"Expected default {default} when key {key} not found, got {result}"

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=1,
            max_size=50
        ).map(lambda x: sorted(x)),
        default=st.integers()
    )
    @settings(max_examples=500, deadline=None)
    def test_key_found_value_function(self, snapshot: List[Tuple[int, int]], default: int):
        """
        Test function property: when key in snapshot, return corresponding value.
        Scope: function, precondition: key in [k for k, v in snapshot], property: key_found_value
        """
        # Choose a key that exists in the snapshot
        existing_key = st.sampled_from([k for k, v in snapshot])
        
        @given(key=existing_key)
        def test_inner(key):
            result = kv_snapshot_reader(snapshot, key, default)
            # Find the expected value
            expected_value = next(v for k, v in snapshot if k == key)
            assert result == expected_value, f"Expected value {expected_value} for key {key}, got {result}"
        
        test_inner()

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=50
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=500, deadline=None)
    def test_sorted_assumption_function(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test function property: with sorted snapshot, return first match or default.
        Scope: function, precondition: snapshot is sorted by key, property: sorted_assumption
        """
        # Since we generate sorted snapshots, this should always hold
        result = kv_snapshot_reader(snapshot, key, default)
        
        # If key exists, should return first matching value
        key_exists = any(k == key for k, v in snapshot)
        if key_exists:
            expected_value = next(v for k, v in snapshot if k == key)
            assert result == expected_value, f"Expected first match {expected_value}, got {result}"
        else:
            assert result == default, f"Expected default {default} when key not found, got {result}"

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=30
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=200, deadline=None)
    def test_deterministic_function(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test function property: same inputs always produce same output.
        Scope: function, precondition: snapshot and key unchanged, property: deterministic
        """
        result1 = kv_snapshot_reader(snapshot, key, default)
        result2 = kv_snapshot_reader(snapshot, key, default)
        
        assert result1 == result2, f"Function not deterministic: {result1} != {result2}"

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=30
        ).map(lambda x: sorted(x)),
        key=st.integers(),
        default=st.integers()
    )
    @settings(max_examples=200, deadline=None)
    def test_no_side_effects_function(self, snapshot: List[Tuple[int, int]], key: int, default: int):
        """
        Test function property: snapshot remains unchanged after function call.
        Scope: function, precondition: None, property: no_side_effects
        """
        original_snapshot = snapshot.copy()
        kv_snapshot_reader(snapshot, key, default)
        
        assert snapshot == original_snapshot, "Function modified the snapshot"

    @given(
        snapshot=st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=0,
            max_size=50
        ).map(lambda x: sorted(x)),
        key=st.integers()
    )
    @settings(max_examples=500, deadline=None)
    def test_monotonic_search_function(self, snapshot: List[Tuple[int, int]], key: int):
        """
        Test function property: early termination when k > key encountered.
        Scope: function, precondition: snapshot sorted by key, property: monotonic_search
        """
        # This is more of a behavioral test - we can't easily observe internal termination
        # but we can verify the result is consistent with early termination
        result = kv_snapshot_reader(snapshot, key)
        
        # If there are keys > key in the snapshot, we should not have processed them
        # This is implicitly tested by the correctness of the result
        key_exists = any(k == key for k, v in snapshot)
        if key_exists:
            expected_value = next(v for k, v in snapshot if k == key)
            assert result == expected_value
        else:
            # Should return None (default) without processing keys > key
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])