"""
Hypothesis-based property tests for the stream_joiner function.

This test suite exercises all semantic properties identified for the stream_joiner function
using the Hypothesis testing framework to generate comprehensive test cases.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Any


# Import the stream_joiner function - adjust the import path as needed
# from your_module import stream_joiner

def stream_joiner(left: List[Any], right: List[Any]) -> List[Any]:
    """
    Merge two sorted lists, removing duplicate tail elements.
    
    This is a reference implementation for testing purposes.
    Replace this with the actual stream_joiner implementation.
    """
    if not left:
        return right[:]
    if not right:
        return left[:]
    
    out = []
    i = j = 0
    
    # Merge while both lists have elements
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    
    # Add remaining elements
    while i < len(left):
        out.append(left[i])
        i += 1
    
    while j < len(right):
        out.append(right[j])
        j += 1
    
    # Remove duplicate tail if both input lists had the same last element
    if out and left and right and out[-1] == left[-1] == right[-1]:
        out.pop()
    
    return out


class TestStreamJoinerProperties:
    """Test class for stream_joiner semantic properties."""
    
    # Strategies for generating test data
    sorted_lists = st.lists(st.integers()).map(sorted)
    non_empty_sorted_lists = st.lists(st.integers(min_value=0, max_value=100), min_size=1).map(sorted)
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_sorted_merge(self, left: List[int], right: List[int]):
        """Property: sorted_merge - if left and right are sorted lists, then out is sorted."""
        result = stream_joiner(left, right)
        assert result == sorted(result), f"Result {result} is not sorted"
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    def test_contains_all_elements(self, left: List[int], right: List[int]):
        """Property: contains_all_elements - set(out) == set(left) | set(right)."""
        result = stream_joiner(left, right)
        result_set = set(result)
        expected_set = set(left) | set(right)
        assert result_set == expected_set, f"Result set {result_set} != expected set {expected_set}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_preserves_order(self, left: List[int], right: List[int]):
        """Property: preserves_order - relative order of elements from left and right is preserved in out."""
        result = stream_joiner(left, right)
        
        # Check that elements from left appear in the same relative order
        left_indices = [result.index(x) for x in left if x in result]
        assert left_indices == sorted(left_indices), "Relative order of left elements not preserved"
        
        # Check that elements from right appear in the same relative order
        right_indices = [result.index(x) for x in right if x in result]
        assert right_indices == sorted(right_indices), "Relative order of right elements not preserved"
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    def test_empty_lists_handled(self, left: List[int], right: List[int]):
        """Property: empty_lists_handled - if not left: out == right; if not right: out == left."""
        result = stream_joiner(left, right)
        
        if not left:
            assert result == right, f"Expected {right}, got {result} when left is empty"
        if not right:
            assert result == left, f"Expected {left}, got {result} when right is empty"
    
    @given(left=sorted_lists)
    def test_idempotent_merge(self, left: List[int]):
        """Property: idempotent_merge - stream_joiner(left, left) == left."""
        result = stream_joiner(left, left)
        assert result == left, f"stream_joiner({left}, {left}) = {result}, expected {left}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_commutative_merge(self, left: List[int], right: List[int]):
        """Property: commutative_merge - stream_joiner(left, right) == stream_joiner(right, left)."""
        result1 = stream_joiner(left, right)
        result2 = stream_joiner(right, left)
        assert result1 == result2, f"stream_joiner({left}, {right}) = {result1} != stream_joiner({right}, {left}) = {result2}"
    
    @given(left=sorted_lists, right=sorted_lists, third=sorted_lists)
    def test_associative_merge(self, left: List[int], right: List[int], third: List[int]):
        """Property: associative_merge - stream_joiner(stream_joiner(left, right), third) == stream_joiner(left, stream_joiner(right, third))."""
        result1 = stream_joiner(stream_joiner(left, right), third)
        result2 = stream_joiner(left, stream_joiner(right, third))
        assert result1 == result2, f"Associativity failed: {result1} != {result2}"
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    def test_length_bound(self, left: List[int], right: List[int]):
        """Property: length_bound - len(out) <= len(left) + len(right)."""
        result = stream_joiner(left, right)
        assert len(result) <= len(left) + len(right), f"Length {len(result)} exceeds bound {len(left) + len(right)}"
    
    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_minimum_length(self, left: List[int], right: List[int]):
        """Property: minimum_length - len(out) >= max(len(left), len(right))."""
        result = stream_joiner(left, right)
        min_length = max(len(left), len(right))
        assert len(result) >= min_length, f"Length {len(result)} is less than minimum {min_length}"
    
    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_duplicate_tail_removal(self, left: List[int], right: List[int]):
        """Property: duplicate_tail_removal - if left[-1] == right[-1]: out[-1] != left[-1] (duplicate tail removed)."""
        assume(len(left) > 0 and len(right) > 0)
        assume(left[-1] == right[-1])
        
        result = stream_joiner(left, right)
        
        # If there was a duplicate tail, it should be removed
        if result and len(result) > 0:
            assert result[-1] != left[-1], f"Duplicate tail {left[-1]} not removed from result {result}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_no_internal_duplicates(self, left: List[int], right: List[int]):
        """Property: no_internal_duplicates - no consecutive duplicates in out except possibly at the boundary before tail removal."""
        result = stream_joiner(left, right)
        
        # Check for consecutive duplicates in the result
        for i in range(len(result) - 1):
            # The only allowed duplicate would be at the very end before tail removal,
            # but since tail removal happens, there should be no consecutive duplicates
            assert result[i] != result[i + 1], f"Consecutive duplicate {result[i]} found at positions {i} and {i+1}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_monotonicity_preservation(self, left: List[int], right: List[int]):
        """Property: monotonicity_preservation - if left and right are non-decreasing, then out is non-decreasing."""
        result = stream_joiner(left, right)
        
        # Check that result is non-decreasing
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1], f"Non-monotonic at positions {i},{i+1}: {result[i]} > {result[i+1]}"
    
    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_boundary_element_handling(self, left: List[int], right: List[int]):
        """Property: boundary_element_handling - min(left[0], right[0]) == out[0] and max(left[-1], right[-1]) >= out[-1]."""
        assume(len(left) > 0 and len(right) > 0)
        
        result = stream_joiner(left, right)
        
        if result:  # Only check if result is not empty
            expected_first = min(left[0], right[0])
            assert result[0] == expected_first, f"First element {result[0]} != expected {expected_first}"
            
            expected_last_max = max(left[-1], right[-1])
            assert result[-1] <= expected_last_max, f"Last element {result[-1]} > expected max {expected_last_max}"


class TestStreamJoinerBranchProperties:
    """Test class for stream_joiner branch-specific properties."""

    # Strategies for generating test data
    sorted_lists = st.lists(st.integers()).map(sorted)
    non_empty_sorted_lists = st.lists(st.integers(min_value=0, max_value=100), min_size=1).map(sorted)
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    def test_left_element_selected_branch(self, left: List[int], right: List[int]):
        """Property: left_element_selected - when left[i] <= right[j], left[i] is selected."""
        # This is more of an implementation detail test
        # We can verify this by checking that smaller elements appear first
        assume(len(left) > 0 and len(right) > 0)
        
        result = stream_joiner(left, right)
        
        # The smallest element overall should be first
        min_left = min(left) if left else float('inf')
        min_right = min(right) if right else float('inf')
        expected_first = min(min_left, min_right)
        
        if result:
            assert result[0] == expected_first, f"Expected first element {expected_first}, got {result[0]}"
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    def test_right_element_selected_branch(self, left: List[int], right: List[int]):
        """Property: right_element_selected - when not (left[i] <= right[j]), right[j] is selected."""
        # Similar to above, this tests the selection logic
        assume(len(left) > 0 and len(right) > 0)
        
        result = stream_joiner(left, right)
        
        # The smallest element overall should be first
        min_left = min(left) if left else float('inf')
        min_right = min(right) if right else float('inf')
        expected_first = min(min_left, min_right)
        
        if result:
            assert result[0] == expected_first, f"Expected first element {expected_first}, got {result[0]}"
    
    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_duplicate_tail_removed_branch(self, left: List[int], right: List[int]):
        """Property: duplicate_tail_removed - when out[-1] == left[-1] == right[-1], out.pop() is called."""
        assume(len(left) > 0 and len(right) > 0)
        assume(left[-1] == right[-1])
        
        result = stream_joiner(left, right)
        
        # If there was a duplicate tail, it should be removed
        if result and len(result) > 0:
            assert result[-1] != left[-1], f"Duplicate tail {left[-1]} not removed from result {result}"


class TestStreamJoinerEdgeCases:
    """Test class for edge cases and special scenarios."""

    # Strategies for generating test data
    sorted_lists = st.lists(st.integers()).map(sorted)
    non_empty_sorted_lists = st.lists(st.integers(min_value=0, max_value=100), min_size=1).map(sorted)
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    @settings(max_examples=1000, deadline=None)
    def test_various_edge_cases(self, left: List[int], right: List[int]):
        """Test various edge cases to ensure robustness."""
        result = stream_joiner(left, right)
        
        # Basic sanity checks
        assert isinstance(result, list), "Result should be a list"
        
        # Length constraints
        assert len(result) <= len(left) + len(right), "Result length exceeds sum of input lengths"
        
        # Element containment
        if left or right:
            assert set(result) == set(left) | set(right), "Result doesn't contain all unique elements"
    
    @given(left=st.lists(st.integers()), right=st.lists(st.integers()))
    @example(left=[], right=[])
    @example(left=[1], right=[])
    @example(left=[], right=[1])
    @example(left=[1], right=[1])
    @example(left=[1, 2], right=[3, 4])
    @example(left=[3, 4], right=[1, 2])
    @example(left=[1, 1, 2], right=[2, 3, 3])
    @example(left=[1, 3, 5], right=[2, 4, 6])
    def test_specific_examples(self, left: List[int], right: List[int]):
        """Test specific examples to ensure correctness."""
        result = stream_joiner(left, right)
        
        # Verify sorted property
        assert result == sorted(result), f"Result {result} is not sorted"
        
        # Verify element containment
        assert set(result) == set(left) | set(right), f"Result doesn't contain all elements"


if __name__ == "__main__":
    # Run the tests if this file is executed directly
    pytest.main([__file__, "-v"])