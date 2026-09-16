"""
Hypothesis tests for timestamps_stream function semantic properties.

This test file exercises all semantic properties identified in 
properties/timestamps_stream_properties.json using the Hypothesis 
testing framework.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest

# Import the function under test
from dataset.python_programs.timestamps_stream import timestamps_stream


class TestTimestampsStreamProperties:
    """Test class for timestamps_stream semantic properties."""

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_sorted_merge_property(self, left, right):
        """
        Property: sorted_merge
        Precondition: left and right are sorted lists
        Formal: merged is sorted
        """
        # Ensure precondition: both lists are sorted
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        merged = timestamps_stream(left_sorted, right_sorted)
        
        # Verify the merged list is sorted
        assert merged == sorted(merged), f"Merged list {merged} is not sorted"

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_no_duplicates_property(self, left, right):
        """
        Property: no_duplicates
        Precondition: left and right contain no duplicates
        Formal: merged contains no duplicates
        """
        # Ensure precondition: no duplicates in input lists
        left_no_dups = list(dict.fromkeys(left))  # Remove duplicates while preserving order
        right_no_dups = list(dict.fromkeys(right))
        
        # Skip empty lists as they don't satisfy the precondition of containing no duplicates
        assume(len(left_no_dups) > 0 and len(right_no_dups) > 0)
        
        merged = timestamps_stream(left_no_dups, right_no_dups)
        
        # Verify no duplicates in merged list
        assert len(merged) == len(set(merged)), f"Merged list {merged} contains duplicates"

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_contains_all_elements_property(self, left, right):
        """
        Property: contains_all_elements
        Precondition: left and right are non-empty
        Formal: merged contains all elements from left and right
        """
        # Ensure precondition: both lists are non-empty
        assume(len(left) > 0 and len(right) > 0)
        
        merged = timestamps_stream(left, right)
        
        # Verify all elements from both lists are in merged
        all_elements = set(left) | set(right)
        merged_set = set(merged)
        
        assert all_elements == merged_set, (
            f"Merged list {merged} does not contain all elements from "
            f"left {left} and right {right}"
        )

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_preserves_order_property(self, left, right):
        """
        Property: preserves_order
        Precondition: left and right are sorted
        Formal: relative order of elements from left and right is preserved in merged
        """
        # Ensure precondition: both lists are sorted
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        merged = timestamps_stream(left_sorted, right_sorted)
        
        # Verify relative order is preserved for left elements
        left_indices = [merged.index(x) for x in left_sorted if x in merged]
        assert left_indices == sorted(left_indices), (
            f"Order of left elements not preserved in merged: {merged}"
        )
        
        # Verify relative order is preserved for right elements
        right_indices = [merged.index(x) for x in right_sorted if x in merged]
        assert right_indices == sorted(right_indices), (
            f"Order of right elements not preserved in merged: {merged}"
        )

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_left_element_selected_property(self, left, right):
        """
        Property: left_element_selected
        Scope: branch
        Condition: left[i] <= right[j]
        Formal: merged.append(left[i])
        """
        # Ensure precondition: both lists are sorted
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        assume(len(left_sorted) > 0 and len(right_sorted) > 0)
        
        merged = timestamps_stream(left_sorted, right_sorted)
        
        # Test the property by checking that when left[i] <= right[j],
        # the left element appears before the right element in merged
        # (unless they're equal, in which case order doesn't matter for the property)
        
        i = j = 0
        merged_idx = 0
        
        while i < len(left_sorted) and j < len(right_sorted):
            if left_sorted[i] <= right_sorted[j]:
                # The left element should be selected next
                assert merged_idx < len(merged), "Merged list exhausted unexpectedly"
                assert merged[merged_idx] == left_sorted[i], (
                    f"Left element {left_sorted[i]} not selected when condition "
                    f"left[{i}] <= right[{j}] ({left_sorted[i]} <= {right_sorted[j]}) is true"
                )
                i += 1
                merged_idx += 1
            else:
                # The right element should be selected next
                assert merged_idx < len(merged), "Merged list exhausted unexpectedly"
                assert merged[merged_idx] == right_sorted[j], (
                    f"Right element {right_sorted[j]} not selected when condition "
                    f"left[{i}] > right[{j}] ({left_sorted[i]} > {right_sorted[j]}) is true"
                )
                j += 1
                merged_idx += 1

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_right_element_selected_property(self, left, right):
        """
        Property: right_element_selected
        Scope: branch
        Condition: not (left[i] <= right[j])
        Formal: merged.append(right[j])
        """
        # Ensure precondition: both lists are sorted
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        assume(len(left_sorted) > 0 and len(right_sorted) > 0)
        
        merged = timestamps_stream(left_sorted, right_sorted)
        
        # Test the property by checking that when left[i] > right[j],
        # the right element appears before the left element in merged
        
        i = j = 0
        merged_idx = 0
        
        while i < len(left_sorted) and j < len(right_sorted):
            if not (left_sorted[i] <= right_sorted[j]):
                # The right element should be selected next
                assert merged_idx < len(merged), "Merged list exhausted unexpectedly"
                assert merged[merged_idx] == right_sorted[j], (
                    f"Right element {right_sorted[j]} not selected when condition "
                    f"not (left[{i}] <= right[{j}]) ({left_sorted[i]} > {right_sorted[j]}) is true"
                )
                j += 1
                merged_idx += 1
            else:
                # The left element should be selected next
                assert merged_idx < len(merged), "Merged list exhausted unexpectedly"
                assert merged[merged_idx] == left_sorted[i], (
                    f"Left element {left_sorted[i]} not selected when condition "
                    f"left[{i}] <= right[{j}] ({left_sorted[i]} <= {right_sorted[j]}) is true"
                )
                i += 1
                merged_idx += 1

    @given(
        left=st.lists(st.integers(), min_size=1),
        right=st.lists(st.integers(), min_size=1)
    )
    def test_duplicate_removed_property(self, left, right):
        """
        Property: duplicate_removed
        Scope: branch
        Condition: merged and left and right and merged[-1] == left[-1] == right[-1]
        Formal: merged.pop()
        """
        # Ensure precondition: both lists are sorted and non-empty
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        assume(len(left_sorted) > 0 and len(right_sorted) > 0)
        
        merged = timestamps_stream(left_sorted, right_sorted)
        
        # Check if the condition for duplicate removal is met
        if (merged and left_sorted and right_sorted and 
            merged[-1] == left_sorted[-1] == right_sorted[-1]):
            
            # The bug should have removed the duplicate
            # So merged[-1] should not equal left_sorted[-1] anymore
            # (unless there were multiple duplicates)
            
            # Count occurrences in original lists
            left_count = left_sorted.count(left_sorted[-1])
            right_count = right_sorted.count(right_sorted[-1])
            total_count = left_count + right_count
            
            # Count occurrences in merged list
            merged_count = merged.count(left_sorted[-1])
            
            # Due to the bug, one duplicate should be removed
            assert merged_count == total_count - 1, (
                f"Duplicate removal bug not working correctly. "
                f"Expected {total_count - 1} occurrences, got {merged_count}"
            )

    # Additional edge case tests to ensure comprehensive coverage
    
    @given(
        left=st.lists(st.integers()),
        right=st.lists(st.integers())
    )
    def test_empty_lists_property(self, left, right):
        """Test behavior with empty lists."""
        merged = timestamps_stream(left, right)
        
        # If both are empty, result should be empty
        if not left and not right:
            assert merged == []
        
        # If one is empty, result should be the other
        elif not left:
            assert merged == right
        elif not right:
            assert merged == left

    @given(
        left=st.lists(st.integers()),
        right=st.lists(st.integers())
    )
    @example(left=[], right=[])
    @example(left=[1], right=[])
    @example(left=[], right=[1])
    @example(left=[1], right=[2])
    @example(left=[2], right=[1])
    @example(left=[1, 1], right=[1, 1])  # Test duplicate handling
    @example(left=[1, 3, 5], right=[2, 4, 6])  # Test interleaving
    @example(left=[1, 2, 3], right=[1, 2, 3])  # Test identical lists
    def test_specific_examples(self, left, right):
        """Test specific examples to ensure correct behavior."""
        merged = timestamps_stream(left, right)
        
        # Basic sanity checks
        if not left and not right:
            assert merged == []
        elif not left:
            assert merged == right
        elif not right:
            assert merged == left
        else:
            # For non-empty lists, verify basic properties
            assert len(merged) <= len(left) + len(right), "Merged list too long"
            assert set(merged) == set(left) | set(right), "Missing elements in merged"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])