#!/usr/bin/env python3
"""
Hypothesis-based tests for blend_supplies function semantic properties.
Tests all 9 semantic properties identified in properties/blend_supplies_properties.json.
"""

import sys
import os
from typing import List, Tuple

# Add the current directory to Python path to import blend_supplies
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, integers, builds
import pytest


def blend_supplies(left: List[int], right: List[int]) -> List[int]:
    """
    Merge two sorted lists, removing duplicates.
    
    Args:
        left: First sorted list
        right: Second sorted list
    
    Returns:
        Merged sorted list with duplicates removed
    """
    merged = []
    li, ri = 0, 0
    
    # Merge the two lists
    while li < len(left) and ri < len(right):
        if left[li] < right[ri]:
            merged.append(left[li])
            li += 1
        else:
            merged.append(right[ri])
            ri += 1
    
    # Add remaining elements
    while li < len(left):
        merged.append(left[li])
        li += 1
    
    while ri < len(right):
        merged.append(right[ri])
        ri += 1
    
    # Remove duplicates at boundaries
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    
    return merged


class TestBlendSuppliesProperties:
    """Test class for blend_supplies semantic properties using Hypothesis."""

    @given(left=lists(integers()), right=lists(integers()))
    def test_sorted_merge_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: sorted_merge
        Precondition: left and right are sorted lists
        Formal: merged is sorted
        """
        # Sort the inputs to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        merged = blend_supplies(left_sorted, right_sorted)
        
        # Check that merged list is sorted
        assert merged == sorted(merged), f"Merged list {merged} is not sorted"

    @given(left=lists(integers()), right=lists(integers()))
    def test_element_preservation_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: element_preservation
        Precondition: left and right are lists
        Formal: all elements from left and right are in merged
        """
        merged = blend_supplies(left, right)
        
        # Check that all elements from left are in merged
        for element in left:
            assert element in merged, f"Element {element} from left not found in merged {merged}"
        
        # Check that all elements from right are in merged
        for element in right:
            assert element in merged, f"Element {element} from right not found in merged {merged}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_duplicate_elimination_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: duplicate_elimination
        Precondition: left and right are sorted lists
        Formal: no duplicates in merged except possibly at boundaries
        """
        # Sort the inputs to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        merged = blend_supplies(left_sorted, right_sorted)
        
        # Check for duplicates in merged list (except possibly at boundaries)
        for i in range(len(merged) - 1):
            if i == len(merged) - 2:  # Last pair, boundary case
                continue
            assert merged[i] != merged[i + 1], f"Duplicate found at positions {i}, {i+1} in merged {merged}"

    @given(left=lists(integers(min_value=0, max_value=100)), 
           right=lists(integers(min_value=0, max_value=100)))
    def test_boundary_duplicate_removal_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: boundary_duplicate_removal
        Precondition: left and right are sorted lists with same last element
        Formal: if left[-1] == right[-1], then merged[-1] != left[-1]
        """
        # Sort and ensure both lists are non-empty with same last element
        assume(len(left) > 0 and len(right) > 0)
        
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        # Only test when the precondition is met
        if left_sorted[-1] == right_sorted[-1]:
            merged = blend_supplies(left_sorted, right_sorted)
            
            # Check that the duplicate at boundary is removed
            if merged:  # Only check if merged is not empty
                assert merged[-1] != left_sorted[-1], \
                    f"Boundary duplicate not removed: merged[-1]={merged[-1]}, left[-1]={left_sorted[-1]}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_length_conservation_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: length_conservation
        Precondition: left and right are lists
        Formal: len(merged) <= len(left) + len(right)
        """
        merged = blend_supplies(left, right)
        
        # Check that merged length doesn't exceed sum of input lengths
        assert len(merged) <= len(left) + len(right), \
            f"Merged length {len(merged)} exceeds sum of input lengths {len(left) + len(right)}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_empty_input_handling_property(self, left: List[int], right: List[int]) -> None:
        """
        Property: empty_input_handling
        Precondition: left or right is empty
        Formal: if left is empty, merged == right; if right is empty, merged == left
        """
        merged = blend_supplies(left, right)
        
        # Test empty left list
        if len(left) == 0:
            assert merged == right, f"When left is empty, merged {merged} should equal right {right}"
        
        # Test empty right list
        if len(right) == 0:
            assert merged == left, f"When right is empty, merged {merged} should equal left {left}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_left_element_precedence_branch(self, left: List[int], right: List[int]) -> None:
        """
        Property: left_element_precedence
        Scope: branch
        Condition: left[li] < right[ri]
        Formal: merged.append(left[li])
        """
        # Sort inputs to ensure predictable behavior
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        # Only test when we have elements to compare
        if len(left_sorted) > 0 and len(right_sorted) > 0:
            # Find a position where left element is less than right element
            for li in range(len(left_sorted)):
                for ri in range(len(right_sorted)):
                    if left_sorted[li] < right_sorted[ri]:
                        # Create a scenario where this condition would be hit
                        # by making left[li] the smallest available element
                        test_left = [left_sorted[li]] + [x for x in left_sorted if x > left_sorted[li]]
                        test_right = [right_sorted[ri]] + [x for x in right_sorted if x >= right_sorted[ri]]
                        
                        merged = blend_supplies(test_left, test_right)
                        
                        # The left element should appear before the right element in merged
                        left_pos = merged.index(left_sorted[li]) if left_sorted[li] in merged else -1
                        right_pos = merged.index(right_sorted[ri]) if right_sorted[ri] in merged else -1
                        
                        if left_pos != -1 and right_pos != -1:
                            assert left_pos < right_pos, \
                                f"Left element {left_sorted[li]} should precede right element {right_sorted[ri]} in merged {merged}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_right_element_precedence_branch(self, left: List[int], right: List[int]) -> None:
        """
        Property: right_element_precedence
        Scope: branch
        Condition: not (left[li] < right[ri])
        Formal: merged.append(right[ri])
        """
        # Sort inputs to ensure predictable behavior
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        # Only test when we have elements to compare
        if len(left_sorted) > 0 and len(right_sorted) > 0:
            # Find a position where left element is not less than right element
            for li in range(len(left_sorted)):
                for ri in range(len(right_sorted)):
                    if not (left_sorted[li] < right_sorted[ri]):
                        # Create a scenario where this condition would be hit
                        test_left = [left_sorted[li]] + [x for x in left_sorted if x >= left_sorted[li]]
                        test_right = [right_sorted[ri]] + [x for x in right_sorted if x <= right_sorted[ri]]
                        
                        merged = blend_supplies(test_left, test_right)
                        
                        # The right element should appear before or at same position as left element
                        left_pos = merged.index(left_sorted[li]) if left_sorted[li] in merged else -1
                        right_pos = merged.index(right_sorted[ri]) if right_sorted[ri] in merged else -1
                        
                        if left_pos != -1 and right_pos != -1:
                            assert right_pos <= left_pos, \
                                f"Right element {right_sorted[ri]} should precede or equal left element {left_sorted[li]} in merged {merged}"

    @given(left=lists(integers()), right=lists(integers()))
    def test_duplicate_removal_branch(self, left: List[int], right: List[int]) -> None:
        """
        Property: duplicate_removal
        Scope: branch
        Condition: merged and left and right and merged[-1] == left[-1] == right[-1]
        Formal: merged.pop()
        """
        # Sort inputs and ensure they have the same last element
        assume(len(left) > 0 and len(right) > 0)
        
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        # Only test when the condition for duplicate removal is met
        if left_sorted[-1] == right_sorted[-1]:
            merged = blend_supplies(left_sorted, right_sorted)
            
            # If the condition was met, the duplicate should have been removed
            # So merged[-1] should not equal the original last elements
            if merged and len(merged) > 0:
                assert merged[-1] != left_sorted[-1], \
                    f"Duplicate removal failed: merged[-1]={merged[-1]} still equals left[-1]={left_sorted[-1]}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])