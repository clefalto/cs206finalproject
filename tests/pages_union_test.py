#!/usr/bin/env python3
"""
Hypothesis-based property tests for the pages_union function.
Tests all semantic properties identified in properties/pages_union_properties.json.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Set


def pages_union(left: List[int], right: List[int]) -> List[int]:
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
        a, b = left[i], right[j]
        
        if a < b:
            # left_element_first property
            merged.append(a)
            i += 1
        elif b < a:
            # right_element_first property
            merged.append(b)
            j += 1
        else:
            # equal_elements_both_added property
            merged.append(a)
            merged.append(b)
            i += 1
            j += 1
    
    # Add remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    
    # duplicate_removal property: remove consecutive duplicates
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    
    return merged


def is_sorted(lst: List[int]) -> bool:
    """Check if a list is sorted in non-decreasing order."""
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))


# Strategy for generating sorted lists of integers
sorted_lists = st.lists(st.integers()).map(sorted)


class TestPagesUnionProperties:
    """Test class for pages_union semantic properties."""
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_sorted_output(self, left: List[int], right: List[int]):
        """Test sorted_output property: merged result should be sorted."""
        merged = pages_union(left, right)
        assert is_sorted(merged), f"Result {merged} is not sorted"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_union_semantics(self, left: List[int], right: List[int]):
        """Test union_semantics property: merged should contain union of elements."""
        merged = pages_union(left, right)
        expected_union = set(left) | set(right)
        assert set(merged) == expected_union, \
            f"Union mismatch: {set(merged)} != {expected_union}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_no_duplicates(self, left: List[int], right: List[int]):
        """Test no_duplicates property: merged should have no duplicate elements."""
        merged = pages_union(left, right)
        assert len(set(merged)) == len(merged), \
            f"Found duplicates in {merged}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_preserves_all_elements(self, left: List[int], right: List[int]):
        """Test preserves_all_elements property: all input elements should be in output."""
        merged = pages_union(left, right)
        left_in_merged = all(x in merged for x in left)
        right_in_merged = all(x in merged for x in right)
        assert left_in_merged and right_in_merged, \
            f"Missing elements: left={left}, right={right}, merged={merged}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_length_bound(self, left: List[int], right: List[int]):
        """Test length_bound property: merged length should not exceed sum of inputs."""
        merged = pages_union(left, right)
        assert len(merged) <= len(left) + len(right), \
            f"Length bound violated: {len(merged)} > {len(left) + len(right)}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_empty_input_handling(self, left: List[int], right: List[int]):
        """Test empty_input_handling property: handle empty inputs correctly."""
        merged = pages_union(left, right)
        
        if not left:
            assert merged == right, f"Empty left should return right: {merged} != {right}"
        if not right:
            assert merged == left, f"Empty right should return left: {merged} != {left}"
    
    @given(left=sorted_lists)
    def test_idempotent_union(self, left: List[int]):
        """Test idempotent_union property: union with self should equal self."""
        result = pages_union(left, left)
        assert result == left, f"pages_union({left}, {left}) should equal {left}, got {result}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_commutative(self, left: List[int], right: List[int]):
        """Test commutative property: order of inputs should not matter."""
        result1 = pages_union(left, right)
        result2 = pages_union(right, left)
        assert result1 == result2, \
            f"Commutative property failed: pages_union({left}, {right}) != pages_union({right}, {left})"
    
    @given(left=sorted_lists, right=sorted_lists, third=sorted_lists)
    def test_associative(self, left: List[int], right: List[int], third: List[int]):
        """Test associative property: grouping should not matter."""
        result1 = pages_union(pages_union(left, right), third)
        result2 = pages_union(left, pages_union(right, third))
        assert result1 == result2, \
            f"Associative property failed: {result1} != {result2}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_monotonic_inclusion(self, left: List[int], right: List[int]):
        """Test monotonic_inclusion property: if left ⊆ right, result should equal right."""
        assume(set(left).issubset(set(right)))
        
        merged = pages_union(left, right)
        assert merged == right, \
            f"Monotonic inclusion failed: pages_union({left}, {right}) should equal {right}, got {merged}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_subset_preservation(self, left: List[int], right: List[int]):
        """Test subset_preservation property: input sets should be subsets of output."""
        merged = pages_union(left, right)
        left_set = set(left)
        right_set = set(right)
        merged_set = set(merged)
        
        assert left_set.issubset(merged_set), \
            f"Left set {left_set} not subset of merged {merged_set}"
        assert right_set.issubset(merged_set), \
            f"Right set {right_set} not subset of merged {merged_set}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_left_element_first(self, left: List[int], right: List[int]):
        """Test left_element_first branch property: when a < b, append a and increment i."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] < right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] < right[j]:
                    # Create minimal lists to test this specific branch
                    test_left = left[:i+1]
                    test_right = right[:j+1]
                    
                    merged = pages_union(test_left, test_right)
                    
                    # The smaller element should appear first in merged
                    assert left[i] in merged, f"Element {left[i]} from left should be in merged result"
                    
                    # If this is the first comparison, left[i] should be first
                    if i == 0 and j == 0:
                        assert merged[0] == left[i], \
                            f"When {left[i]} < {right[j]}, {left[i]} should be first in merged result"
                    break
            else:
                continue
            break
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_right_element_first(self, left: List[int], right: List[int]):
        """Test right_element_first branch property: when b < a, append b and increment j."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where right[j] < left[i]
        for i in range(len(left)):
            for j in range(len(right)):
                if right[j] < left[i]:
                    # Create minimal lists to test this specific branch
                    test_left = left[:i+1]
                    test_right = right[:j+1]
                    
                    merged = pages_union(test_left, test_right)
                    
                    # The smaller element should appear first in merged
                    assert right[j] in merged, f"Element {right[j]} from right should be in merged result"
                    
                    # If this is the first comparison, right[j] should be first
                    if i == 0 and j == 0:
                        assert merged[0] == right[j], \
                            f"When {right[j]} < {left[i]}, {right[j]} should be first in merged result"
                    break
            else:
                continue
            break
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_equal_elements_both_added(self, left: List[int], right: List[int]):
        """Test equal_elements_both_added branch property: when a == b, add both and increment both."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] == right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] == right[j]:
                    # Create minimal lists to test this specific branch
                    test_left = left[:i+1]
                    test_right = right[:j+1]
                    
                    merged = pages_union(test_left, test_right)
                    
                    # Both equal elements should be in merged
                    assert left[i] in merged, f"Element {left[i]} from left should be in merged result"
                    assert right[j] in merged, f"Element {right[j]} from right should be in merged result"
                    
                    # If this is the first comparison and elements are equal, both should be added
                    if i == 0 and j == 0:
                        # Count occurrences of the equal element
                        count = merged.count(left[i])
                        assert count >= 2, \
                            f"When {left[i]} == {right[j]}, both should be in merged result, but found only {count} occurrence(s)"
                    break
            else:
                continue
            break
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_duplicate_removal(self, left: List[int], right: List[int]):
        """Test duplicate_removal branch property: remove final duplicate if conditions met."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Test case where the final elements are the same
        if left and right and left[-1] == right[-1]:
            merged = pages_union(left, right)
            
            # If there were duplicates at the end, one should have been removed
            # But we need to be careful about the exact conditions
            left_set = set(left)
            right_set = set(right)
            expected_union = left_set | right_set
            
            # The result should still be a valid union
            assert set(merged) == expected_union, \
                f"Duplicate removal broke union semantics: {set(merged)} != {expected_union}"
            
            # And should still be sorted
            assert is_sorted(merged), f"Duplicate removal broke sorting: {merged}"


if __name__ == "__main__":
    # Run with pytest for full test execution
    pytest.main([__file__, "-v"])