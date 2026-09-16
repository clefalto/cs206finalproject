"""
Test file for ids_merge function using Hypothesis testing framework.
Tests all semantic properties identified in properties/ids_merge_properties.json.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from typing import List


def ids_merge(left: List[int], right: List[int]) -> List[int]:
    """
    Merge two sorted lists, removing duplicates.
    
    Args:
        left: First sorted list
        right: Second sorted list
        
    Returns:
        Merged sorted list with duplicates removed
    """
    merged = []
    i = j = 0
    
    # Merge the two lists
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    
    # Add remaining elements
    while i < len(left):
        merged.append(left[i])
        i += 1
        
    while j < len(right):
        merged.append(right[j])
        j += 1
    
    # Remove duplicates
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    
    return merged


class TestIdsMergeProperties:
    """Test class for ids_merge semantic properties."""
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_sorted_merge(self, left: List[int], right: List[int]):
        """Test that merged result is sorted when inputs are sorted."""
        assume(left == sorted(left) and right == sorted(right))
        merged = ids_merge(left, right)
        assert merged == sorted(merged), f"Expected sorted result, got {merged}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_contains_all_elements(self, left: List[int], right: List[int]):
        """Test that merged result contains all elements from both lists."""
        merged = ids_merge(left, right)
        expected_elements = set(left) | set(right)
        assert set(merged) == expected_elements, \
            f"Expected {expected_elements}, got {set(merged)}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_no_duplicates(self, left: List[int], right: List[int]):
        """Test that merged result has no duplicates."""
        merged = ids_merge(left, right)
        assert len(set(merged)) == len(merged), \
            f"Found duplicates in {merged}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_preserves_order(self, left: List[int], right: List[int]):
        """Test that relative order of elements from left and right is preserved."""
        assume(left == sorted(left) and right == sorted(right))
        merged = ids_merge(left, right)
        
        # Check that elements from left appear in same relative order
        left_indices = [merged.index(x) for x in left if x in merged]
        assert left_indices == sorted(left_indices), \
            f"Left elements not in order: {left_indices}"
        
        # Check that elements from right appear in same relative order
        right_indices = [merged.index(x) for x in right if x in merged]
        assert right_indices == sorted(right_indices), \
            f"Right elements not in order: {right_indices}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_empty_lists_handled(self, left: List[int], right: List[int]):
        """Test that empty lists are handled correctly."""
        merged = ids_merge(left, right)
        
        if not left:
            assert merged == right, f"Expected {right}, got {merged}"
        if not right:
            assert merged == left, f"Expected {left}, got {merged}"
    
    @given(st.lists(st.integers()))
    def test_idempotent_merge(self, left: List[int]):
        """Test that merging a list with itself returns the original list."""
        assume(left == sorted(left))
        result = ids_merge(left, left)
        assert result == left, f"Expected {left}, got {result}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_commutative_merge(self, left: List[int], right: List[int]):
        """Test that merge operation is commutative."""
        assume(left == sorted(left) and right == sorted(right))
        result1 = ids_merge(left, right)
        result2 = ids_merge(right, left)
        assert result1 == result2, \
            f"Commutativity failed: ids_merge({left}, {right}) = {result1}, " \
            f"ids_merge({right}, {left}) = {result2}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()), st.lists(st.integers()))
    def test_associative_merge(self, left: List[int], right: List[int], third: List[int]):
        """Test that merge operation is associative."""
        assume(left == sorted(left) and right == sorted(right) and third == sorted(third))
        result1 = ids_merge(ids_merge(left, right), third)
        result2 = ids_merge(left, ids_merge(right, third))
        assert result1 == result2, \
            f"Associativity failed: ids_merge(ids_merge({left}, {right}), {third}) = {result1}, " \
            f"ids_merge({left}, ids_merge({right}, {third})) = {result2}"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_length_bound(self, left: List[int], right: List[int]):
        """Test that merged length is bounded by sum of input lengths."""
        merged = ids_merge(left, right)
        assert len(merged) <= len(left) + len(right), \
            f"Length bound violated: len({merged}) > len({left}) + len({right})"
    
    @given(st.lists(st.integers(), min_size=1), st.lists(st.integers(), min_size=1))
    def test_minimum_length(self, left: List[int], right: List[int]):
        """Test that merged length is at least the maximum of input lengths."""
        assume(left == sorted(left) and right == sorted(right))
        merged = ids_merge(left, right)
        assert len(merged) >= max(len(left), len(right)), \
            f"Minimum length violated: len({merged}) < max(len({left}), len({right}))"
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_left_element_selected(self, left: List[int], right: List[int]):
        """Test that left element is selected when left[i] <= right[j]."""
        assume(left == sorted(left) and right == sorted(right))
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] <= right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] <= right[j]:
                    # Create a scenario where this condition would be tested
                    test_left = left[:i+1]
                    test_right = right[:j+1]
                    merged = ids_merge(test_left, test_right)
                    
                    # The left element should be in the merged result
                    assert left[i] in merged, \
                        f"Left element {left[i]} should be in merged result {merged}"
                    break
            else:
                continue
            break
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_right_element_selected(self, left: List[int], right: List[int]):
        """Test that right element is selected when left[i] > right[j]."""
        assume(left == sorted(left) and right == sorted(right))
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] > right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] > right[j]:
                    # Create a scenario where this condition would be tested
                    test_left = left[:i+1]
                    test_right = right[:j+1]
                    merged = ids_merge(test_left, test_right)
                    
                    # The right element should be in the merged result
                    assert right[j] in merged, \
                        f"Right element {right[j]} should be in merged result {merged}"
                    break
            else:
                continue
            break
    
    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_duplicate_removed(self, left: List[int], right: List[int]):
        """Test that duplicates are removed when merged[-1] == left[-1] == right[-1]."""
        assume(left == sorted(left) and right == sorted(right))
        assume(len(left) > 0 and len(right) > 0)
        
        # Create a scenario where the last elements are the same
        if left and right and left[-1] == right[-1]:
            merged = ids_merge(left, right)
            
            # Count occurrences of the last element
            last_element = left[-1]
            count_in_left = left.count(last_element)
            count_in_right = right.count(last_element)
            count_in_merged = merged.count(last_element)
            
            # The merged result should have at most one occurrence
            assert count_in_merged <= 1, \
                f"Duplicate not removed: {last_element} appears {count_in_merged} times in {merged}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])