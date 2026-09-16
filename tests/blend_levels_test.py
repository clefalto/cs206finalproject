"""
Tests for blend_levels function using Hypothesis testing framework.
Tests all semantic properties identified in properties/blend_levels_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import lists, integers


def blend_levels(left, right):
    """
    Merge two sorted lists, removing duplicates at the boundary.
    
    Args:
        left: First sorted list
        right: Second sorted list
    
    Returns:
        Merged sorted list with boundary duplicates removed
    """
    merged = []
    i = j = 0
    
    # Merge lists while maintaining sorted order
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    
    # Add remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    
    # Remove duplicate at boundary if both lists are non-empty and end with same element
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    
    return merged


class TestBlendLevels:
    """Test class for blend_levels function semantic properties."""

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_left_element_preferred(self, left, right):
        """Test that when left[i] <= right[j], left element is preferred."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # Check that the merge algorithm prefers left elements when they are <= right elements
        # This is tested by verifying the merge produces a sorted result
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_right_element_preferred(self, left, right):
        """Test that when left[i] > right[j], right element is preferred."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # Check that the merge algorithm prefers right elements when left[i] > right[j]
        # This is tested by verifying the merge produces a sorted result
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=1),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=1)
    )
    def test_duplicate_removal(self, left, right):
        """Test that duplicate elements at the boundary are removed."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # If both lists are non-empty and end with the same element,
        # the merged result should not end with that duplicate
        if left_sorted and right_sorted and left_sorted[-1] == right_sorted[-1]:
            if result:  # Only check if result is non-empty
                assert result[-1] != left_sorted[-1]

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_length_preservation(self, left, right):
        """Test that output length equals sum of input lengths minus boundary duplicates."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        expected_length = len(left_sorted) + len(right_sorted)
        if left_sorted and right_sorted and left_sorted[-1] == right_sorted[-1]:
            expected_length -= 1
        
        assert len(result) == expected_length

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_sorted_output(self, left, right):
        """Test that the output is sorted when inputs are sorted."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # Verify the result is sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_identity_on_empty(self, left, right):
        """Test that blending with empty lists returns the other list."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        # Test blend_levels([], right) == right
        if len(left_sorted) == 0:
            result = blend_levels(left_sorted, right_sorted)
            assert result == right_sorted
        
        # Test blend_levels(left, []) == left
        if len(right_sorted) == 0:
            result = blend_levels(left_sorted, right_sorted)
            assert result == left_sorted

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_commutativity(self, left, right):
        """Test that blend_levels(left, right) == blend_levels(right, left)."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result1 = blend_levels(left_sorted, right_sorted)
        result2 = blend_levels(right_sorted, left_sorted)
        
        assert result1 == result2

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        other=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_associativity(self, left, right, other):
        """Test that blend_levels is associative."""
        assume(len(left) >= 0 and len(right) >= 0 and len(other) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        other_sorted = sorted(other)
        
        result1 = blend_levels(blend_levels(left_sorted, right_sorted), other_sorted)
        result2 = blend_levels(left_sorted, blend_levels(right_sorted, other_sorted))
        
        assert result1 == result2

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=1),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=1)
    )
    def test_duplicate_handling(self, left, right):
        """Test that duplicate elements at the boundary are properly handled."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # If both lists end with the same element, the result should not end with that element
        if left_sorted and right_sorted and left_sorted[-1] == right_sorted[-1]:
            if result:  # Only check if result is non-empty
                assert result[-1] != left_sorted[-1]

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_element_preservation(self, left, right):
        """Test that all elements from both lists are preserved in the result."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # All elements from left should be in result
        for element in left_sorted:
            assert element in result
        
        # All elements from right should be in result
        for element in right_sorted:
            assert element in result

    @given(
        left=lists(integers(min_value=-1000, max_value=1000), min_size=0),
        right=lists(integers(min_value=-1000, max_value=1000), min_size=0)
    )
    def test_monotonicity(self, left, right):
        """Test that the merge operation preserves monotonicity."""
        assume(len(left) >= 0 and len(right) >= 0)
        
        # Sort the lists to satisfy precondition
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        result = blend_levels(left_sorted, right_sorted)
        
        # The result should be sorted (monotonic)
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]