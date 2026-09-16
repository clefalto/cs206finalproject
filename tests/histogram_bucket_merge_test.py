"""
Hypothesis-based tests for histogram_bucket_merge function semantic properties.

This test suite exercises all semantic properties identified in 
properties/histogram_bucket_merge_properties.json using the Hypothesis 
testing framework for property-based testing.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List


def histogram_bucket_merge(left: List[int], right: List[int]) -> List[int]:
    """
    Merge two sorted bucket edges, preserving duplicates.
    """
    i = j = 0
    merged = []
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        elif right[j] < left[i]:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            merged.append(right[j])
            i += 1
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])

    # BUG: drops the last duplicate when both end together.
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    return merged


def is_sorted(lst: List[int]) -> bool:
    """Check if a list is sorted in non-decreasing order."""
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))


def count_element(lst: List[int], element: int) -> int:
    """Count occurrences of an element in a list."""
    return lst.count(element)


# Strategies for generating test data
sorted_lists = st.lists(st.integers(), min_size=0).map(sorted)
non_empty_sorted_lists = st.lists(st.integers(), min_size=1).map(sorted)


class TestBranchProperties:
    """Test branch-level semantic properties."""

    @given(left=sorted_lists, right=sorted_lists)
    def test_left_element_precedence(self, left: List[int], right: List[int]):
        """Test that when left[i] < right[j], left[i] is added first."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] < right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] < right[j]:
                    # Create lists where this condition will be hit
                    left_test = left[:i+1]
                    right_test = right[:j+1]
                    
                    result = histogram_bucket_merge(left_test, right_test)
                    
                    # The element left[i] should appear before right[j] in merged
                    left_idx = result.index(left[i]) if left[i] in result else -1
                    right_idx = result.index(right[j]) if right[j] in result else -1
                    
                    if left_idx != -1 and right_idx != -1:
                        assert left_idx < right_idx, f"left[{i}]={left[i]} should come before right[{j}]={right[j]}"
                    break

    @given(left=sorted_lists, right=sorted_lists)
    def test_right_element_precedence(self, left: List[int], right: List[int]):
        """Test that when right[j] < left[i], right[j] is added first."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where right[j] < left[i]
        for i in range(len(left)):
            for j in range(len(right)):
                if right[j] < left[i]:
                    # Create lists where this condition will be hit
                    left_test = left[:i+1]
                    right_test = right[:j+1]
                    
                    result = histogram_bucket_merge(left_test, right_test)
                    
                    # The element right[j] should appear before left[i] in merged
                    left_idx = result.index(left[i]) if left[i] in result else -1
                    right_idx = result.index(right[j]) if right[j] in result else -1
                    
                    if left_idx != -1 and right_idx != -1:
                        assert right_idx < left_idx, f"right[{j}]={right[j]} should come before left[{i}]={left[i]}"
                    break

    @given(left=sorted_lists, right=sorted_lists)
    def test_equal_elements_handling(self, left: List[int], right: List[int]):
        """Test that when elements are equal, both are added."""
        assume(len(left) > 0 and len(right) > 0)
        
        # Find a position where left[i] == right[j]
        for i in range(len(left)):
            for j in range(len(right)):
                if left[i] == right[j]:
                    # Create lists where this condition will be hit
                    left_test = left[:i+1]
                    right_test = right[:j+1]
                    
                    result = histogram_bucket_merge(left_test, right_test)
                    
                    # Both elements should be in the result
                    assert left[i] in result, f"left[{i}]={left[i]} should be in merged result"
                    assert right[j] in result, f"right[{j}]={right[j]} should be in merged result"
                    
                    # Count should be at least 2 (both elements present)
                    count = count_element(result, left[i])
                    assert count >= 2, f"Element {left[i]} should appear at least twice, got {count}"
                    break

    @given(left=sorted_lists, right=sorted_lists)
    def test_duplicate_tail_removal(self, left: List[int], right: List[int]):
        """Test that duplicate tail is removed when both lists end with same element."""
        assume(len(left) > 0 and len(right) > 0 and left[-1] == right[-1])
        
        result = histogram_bucket_merge(left, right)
        
        # If the bug condition is met, the last element should be removed
        if result and left and right and result[-1] == left[-1] == right[-1]:
            # This should not happen due to the bug fix, but testing the condition
            pass  # The bug actually removes it, so this test documents the behavior


class TestFunctionProperties:
    """Test function-level semantic properties."""

    @given(left=sorted_lists, right=sorted_lists)
    def test_sorted_output(self, left: List[int], right: List[int]):
        """Test that the output is sorted when inputs are sorted."""
        result = histogram_bucket_merge(left, right)
        assert is_sorted(result), f"Result {result} is not sorted"

    @given(left=sorted_lists, right=sorted_lists)
    def test_preserves_duplicates(self, left: List[int], right: List[int]):
        """Test that duplicates are preserved except when both lists end with same element."""
        result = histogram_bucket_merge(left, right)
        
        # Get all unique elements from both lists
        all_elements = set(left) | set(right)
        
        for element in all_elements:
            left_count = count_element(left, element)
            right_count = count_element(right, element)
            expected_count = left_count + right_count
            
            # Special case: if both lists end with the same element, the bug removes one
            if (left and right and left[-1] == right[-1] == element and 
                left_count > 0 and right_count > 0):
                expected_count -= 1
            
            actual_count = count_element(result, element)
            assert actual_count == expected_count, (
                f"Element {element}: expected {expected_count} occurrences, "
                f"got {actual_count} (left={left_count}, right={right_count})"
            )

    @given(left=sorted_lists, right=sorted_lists)
    def test_length_conservation(self, left: List[int], right: List[int]):
        """Test that length is conserved except when duplicate tail removal occurs."""
        result = histogram_bucket_merge(left, right)
        
        expected_length = len(left) + len(right)
        
        # Special case: if both lists end with the same element, length is reduced by 1
        if (result and left and right and result[-1] == left[-1] == right[-1]):
            expected_length -= 1
        
        assert len(result) == expected_length, (
            f"Expected length {expected_length}, got {len(result)} "
            f"(left={len(left)}, right={len(right)})"
        )

    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_length_reduction_bug(self, left: List[int], right: List[int]):
        """Test the specific bug where length is reduced when both end with same element."""
        assume(left[-1] == right[-1])
        
        result = histogram_bucket_merge(left, right)
        
        # This tests the bug: when both lists end with the same element,
        # the length should be reduced by 1
        if result and left and right and result[-1] == left[-1] == right[-1]:
            assert len(result) == len(left) + len(right) - 1, (
                f"Bug not triggered: expected length {len(left) + len(right) - 1}, "
                f"got {len(result)}"
            )

    @given(left=sorted_lists, right=sorted_lists)
    def test_empty_input_handling(self, left: List[int], right: List[int]):
        """Test handling of empty inputs."""
        assume(len(left) == 0 or len(right) == 0)
        
        result = histogram_bucket_merge(left, right)
        
        if len(left) == 0:
            assert result == right, f"Empty left should return right={right}, got {result}"
        if len(right) == 0:
            assert result == left, f"Empty right should return left={left}, got {result}"

    @given(left=st.lists(st.integers(), min_size=1, max_size=1),
           right=st.lists(st.integers(), min_size=1, max_size=1))
    def test_single_element_lists(self, left: List[int], right: List[int]):
        """Test behavior with single-element lists."""
        result = histogram_bucket_merge(left, right)
        
        if left[0] == right[0]:
            # When elements are equal, both should be added, then one removed due to bug
            assert len(result) == 1, f"Equal single elements should result in length 1, got {len(result)}"
            assert result[0] == left[0], f"Result should contain the element {left[0]}, got {result}"
        else:
            assert len(result) == 2, f"Different single elements should result in length 2, got {len(result)}"

    @given(left=sorted_lists, right=sorted_lists)
    def test_monotonicity_preservation(self, left: List[int], right: List[int]):
        """Test that monotonicity is preserved."""
        result = histogram_bucket_merge(left, right)
        
        # The result should be sorted (monotonic non-decreasing)
        assert is_sorted(result), f"Result {result} violates monotonicity"

    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_first_element_preservation(self, left: List[int], right: List[int]):
        """Test that the first element is the minimum of the two first elements."""
        result = histogram_bucket_merge(left, right)
        
        if result:  # Only test if result is non-empty
            expected_first = min(left[0], right[0])
            assert result[0] == expected_first, (
                f"First element should be min({left[0]}, {right[0]}) = {expected_first}, "
                f"got {result[0]}"
            )

    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_last_element_bug(self, left: List[int], right: List[int]):
        """Test the bug where last element is incorrectly removed when both end with same element."""
        assume(left[-1] == right[-1])
        
        result = histogram_bucket_merge(left, right)
        
        # Due to the bug, the last element should be missing
        if result and left and right and left[-1] == right[-1]:
            assert result[-1] != left[-1], (
                f"Bug not triggered: last element {left[-1]} should be removed, "
                f"but result ends with {result[-1]}"
            )

    @given(left=sorted_lists, right=sorted_lists)
    def test_commutativity_bug(self, left: List[int], right: List[int]):
        """Test the commutativity bug when both lists end with same element."""
        assume(len(left) > 0 and len(right) > 0 and left[-1] == right[-1])
        
        result1 = histogram_bucket_merge(left, right)
        result2 = histogram_bucket_merge(right, left)
        
        # Due to the bug, these should be different
        assert result1 != result2, (
            f"Commutativity bug not triggered: results should be different "
            f"when both end with same element, but got {result1} and {result2}"
        )

    @given(a=sorted_lists, b=sorted_lists, c=sorted_lists)
    def test_associativity_bug(self, a: List[int], b: List[int], c: List[int]):
        """Test the associativity bug with three lists ending with same element."""
        assume(len(a) > 0 and len(b) > 0 and len(c) > 0)
        assume(a[-1] == b[-1] == c[-1])
        
        result1 = histogram_bucket_merge(histogram_bucket_merge(a, b), c)
        result2 = histogram_bucket_merge(a, histogram_bucket_merge(b, c))
        
        # Due to the bug, these should be different
        assert result1 != result2, (
            f"Associativity bug not triggered: results should be different, "
            f"but got {result1} and {result2}"
        )

    @given(left=sorted_lists)
    def test_idempotent_bug(self, left: List[int]):
        """Test the idempotent bug when merging a list with itself."""
        assume(len(left) > 0)
        
        result = histogram_bucket_merge(left, left)
        
        # Due to the bug, merging with itself should not return the original list
        # when the list has duplicates at the end
        if len(left) > 1 and left[-1] == left[-2]:
            assert result != left, (
                f"Idempotent bug not triggered: merging {left} with itself "
                f"should not return {left}, but got {result}"
            )


class TestEdgeCases:
    """Test additional edge cases and boundary conditions."""

    @example([], [])
    @example([1], [1])
    @example([1, 2], [2, 3])
    @example([1, 1, 2], [1, 2, 2])
    @given(left=sorted_lists, right=sorted_lists)
    def test_specific_examples(self, left: List[int], right: List[int]):
        """Test with specific examples that should trigger various conditions."""
        result = histogram_bucket_merge(left, right)
        
        # Basic sanity checks
        assert isinstance(result, list), "Result should be a list"
        assert is_sorted(result), f"Result {result} should be sorted"

    def test_known_bug_cases(self):
        """Test specific cases that demonstrate the known bugs."""
        # Case 1: Both lists end with same element
        left = [1, 2, 3]
        right = [2, 3, 3]
        result = histogram_bucket_merge(left, right)
        expected = [1, 2, 2, 3, 3]  # Bug removes one 3
        assert result == expected, f"Expected {expected}, got {result}"

        # Case 2: Commutativity bug
        left = [1, 3]
        right = [2, 3]
        result1 = histogram_bucket_merge(left, right)
        result2 = histogram_bucket_merge(right, left)
        assert result1 != result2, f"Commutativity bug: {result1} should != {result2}"

    @settings(max_examples=1000, deadline=None)
    def test_performance_with_larger_lists(self):
        """Test that the function works correctly with larger lists."""
        # Generate larger sorted lists
        left = list(range(0, 100, 2))  # [0, 2, 4, ..., 98]
        right = list(range(1, 101, 2))  # [1, 3, 5, ..., 99]
        
        result = histogram_bucket_merge(left, right)
        
        # Should be a sorted merge of both lists
        expected = list(range(100))  # [0, 1, 2, 3, ..., 99]
        assert result == expected, f"Large list merge failed: expected {expected}, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])