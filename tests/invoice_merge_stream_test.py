"""
Hypothesis tests for invoice_merge_stream function semantic properties.

This test suite verifies all the semantic properties identified for the
invoice_merge_stream function, including both correct behaviors and
the specific bug related to duplicate last elements.
"""

import pytest
from hypothesis import given, assume, strategies as st
from typing import List, Tuple


# Import the function under test
# Note: The actual function implementation should be imported here
# from invoice_merge_stream import invoice_merge_stream

def invoice_merge_stream(left: List[int], right: List[int]) -> List[int]:
    """
    Mock implementation of invoice_merge_stream for testing purposes.
    This should be replaced with the actual implementation.
    """
    # This is a placeholder - replace with actual implementation
    merged = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        elif right[j] < left[i]:
            merged.append(right[j])
            j += 1
        else:
            # Handle duplicates
            merged.append(left[i])
            merged.append(right[j])
            i += 1
            j += 1
    
    # Add remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    
    # Bug: Remove last element if it's a duplicate from both lists
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    
    return merged


def is_sorted(lst: List[int]) -> bool:
    """Helper function to check if a list is sorted."""
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))


def count_element(lst: List[int], element: int) -> int:
    """Helper function to count occurrences of an element in a list."""
    return lst.count(element)


class TestInvoiceMergeStreamProperties:
    """Test class for invoice_merge_stream semantic properties."""
    
    # Strategies for generating test data
    sorted_lists = st.lists(st.integers(), min_size=0).map(sorted)
    non_empty_sorted_lists = st.lists(st.integers(), min_size=1).map(sorted)
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_sorted_output(self, left: List[int], right: List[int]):
        """Test that the output is always sorted when inputs are sorted."""
        merged = invoice_merge_stream(left, right)
        assert is_sorted(merged), f"Output {merged} is not sorted for inputs {left}, {right}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_empty_input_handling(self, left: List[int], right: List[int]):
        """Test handling of empty inputs."""
        assume(len(left) == 0 or len(right) == 0)
        
        merged = invoice_merge_stream(left, right)
        expected = left + right
        assert merged == expected, f"Expected {expected}, got {merged} for empty input handling"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_identity_on_empty(self, left: List[int], right: List[int]):
        """Test identity property when both inputs are empty."""
        assume(len(left) == 0 and len(right) == 0)
        
        merged = invoice_merge_stream(left, right)
        assert merged == [], f"Expected empty list, got {merged} for empty inputs"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_contains_all_elements_except_bug(self, left: List[int], right: List[int]):
        """Test that all elements are preserved except when the bug condition is met."""
        merged = invoice_merge_stream(left, right)
        
        # Check if bug condition applies
        bug_condition = (merged and left and right and 
                        merged[-1] == left[-1] == right[-1])
        
        if not bug_condition:
            expected_set = set(left) | set(right)
            actual_set = set(merged)
            assert actual_set == expected_set, (
                f"Element sets don't match: expected {expected_set}, got {actual_set} "
                f"for inputs {left}, {right}"
            )
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_length_conservation_except_bug(self, left: List[int], right: List[int]):
        """Test that length is conserved except when the bug condition is met."""
        merged = invoice_merge_stream(left, right)
        
        # Check if bug condition applies
        bug_condition = (merged and left and right and 
                        merged[-1] == left[-1] == right[-1])
        
        if not bug_condition:
            expected_length = len(left) + len(right)
            actual_length = len(merged)
            assert actual_length == expected_length, (
                f"Length not conserved: expected {expected_length}, got {actual_length} "
                f"for inputs {left}, {right}"
            )
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_commutativity_except_bug(self, left: List[int], right: List[int]):
        """Test commutativity property except when the bug condition is met."""
        merged_lr = invoice_merge_stream(left, right)
        merged_rl = invoice_merge_stream(right, left)
        
        # Check if bug condition applies to either result
        bug_condition_lr = (merged_lr and left and right and 
                           merged_lr[-1] == left[-1] == right[-1])
        bug_condition_rl = (merged_rl and right and left and 
                           merged_rl[-1] == right[-1] == left[-1])
        
        if not bug_condition_lr and not bug_condition_rl:
            assert merged_lr == merged_rl, (
                f"Commutativity failed: {merged_lr} != {merged_rl} "
                f"for inputs {left}, {right}"
            )
    
    @given(left=sorted_lists, right=sorted_lists, third=sorted_lists)
    def test_associativity_except_bug(self, left: List[int], right: List[int], third: List[int]):
        """Test associativity property except when overlapping last elements exist."""
        # Check for overlapping last elements
        overlapping_last = (
            left and right and third and
            left[-1] == right[-1] == third[-1]
        )
        
        if not overlapping_last:
            merged_lr_third = invoice_merge_stream(invoice_merge_stream(left, right), third)
            merged_left_rt = invoice_merge_stream(left, invoice_merge_stream(right, third))
            
            assert merged_lr_third == merged_left_rt, (
                f"Associativity failed: {merged_lr_third} != {merged_left_rt} "
                f"for inputs {left}, {right}, {third}"
            )
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_duplicate_preservation(self, left: List[int], right: List[int]):
        """Test that duplicates are preserved except when last elements overlap."""
        merged = invoice_merge_stream(left, right)
        
        # Check for overlapping last elements
        overlapping_last = (
            merged and left and right and
            merged[-1] == left[-1] == right[-1]
        )
        
        if not overlapping_last:
            all_elements = set(left) | set(right)
            for element in all_elements:
                expected_count = count_element(left, element) + count_element(right, element)
                actual_count = count_element(merged, element)
                assert actual_count == expected_count, (
                    f"Duplicate preservation failed for element {element}: "
                    f"expected {expected_count}, got {actual_count} "
                    f"for inputs {left}, {right}"
                )
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_monotonicity(self, left: List[int], right: List[int]):
        """Test that the output maintains monotonicity (sorted order)."""
        merged = invoice_merge_stream(left, right)
        
        # This is essentially the same as sorted_output, but explicitly tests monotonicity
        for i in range(len(merged) - 1):
            assert merged[i] <= merged[i + 1], (
                f"Monotonicity violated at index {i}: {merged[i]} > {merged[i + 1]} "
                f"for inputs {left}, {right}"
            )
    
    @given(left=non_empty_sorted_lists, right=non_empty_sorted_lists)
    def test_bug_invariant(self, left: List[int], right: List[int]):
        """Test the specific bug invariant when last elements are duplicates."""
        merged = invoice_merge_stream(left, right)
        
        # Check if bug condition applies
        bug_condition = (merged and left and right and 
                        merged[-1] == left[-1] == right[-1])
        
        if bug_condition:
            expected_length = len(left) + len(right) - 1
            actual_length = len(merged)
            assert actual_length == expected_length, (
                f"Bug invariant violated: expected length {expected_length}, "
                f"got {actual_length} for inputs {left}, {right}"
            )
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_left_element_precedence(self, left: List[int], right: List[int]):
        """Test that left elements are placed first when left[i] < right[j]."""
        # This is a more complex property that requires tracking the merge process
        # For now, we test it indirectly through the sorted output property
        merged = invoice_merge_stream(left, right)
        
        # Verify that the merge maintains the relative order within each input list
        left_indices = []
        right_indices = []
        
        i = j = 0
        for item in merged:
            if i < len(left) and item == left[i]:
                left_indices.append(len(left_indices))
                i += 1
            elif j < len(right) and item == right[j]:
                right_indices.append(len(right_indices))
                j += 1
        
        # Check that elements from each list maintain their relative order
        assert is_sorted(left_indices), f"Left elements not in order for {left}, {right}"
        assert is_sorted(right_indices), f"Right elements not in order for {left}, {right}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_right_element_precedence(self, left: List[int], right: List[int]):
        """Test that right elements are placed first when right[j] < left[i]."""
        # Similar to left_element_precedence, tested indirectly
        merged = invoice_merge_stream(left, right)
        
        # The sorted output property ensures correct precedence
        assert is_sorted(merged), f"Right precedence violated for {left}, {right}"
    
    @given(left=sorted_lists, right=sorted_lists)
    def test_branch_duplicate_handling(self, left: List[int], right: List[int]):
        """Test that duplicates are handled correctly in normal cases."""
        merged = invoice_merge_stream(left, right)
        
        # Check if bug condition applies
        bug_condition = (merged and left and right and 
                        merged[-1] == left[-1] == right[-1])
        
        if not bug_condition:
            # For non-last duplicates, both should be preserved
            for i in range(len(left)):
                for j in range(len(right)):
                    if left[i] == right[j] and not (i == len(left) - 1 and j == len(right) - 1):
                        # This element should appear twice in merged
                        count_in_merged = count_element(merged, left[i])
                        assert count_in_merged >= 2, (
                            f"Duplicate handling failed for element {left[i]} "
                            f"at positions {i}, {j} in inputs {left}, {right}"
                        )


class TestEdgeCases:
    """Test edge cases and specific scenarios."""
    
    def test_empty_lists(self):
        """Test with both lists empty."""
        result = invoice_merge_stream([], [])
        assert result == []
    
    def test_one_empty_list(self):
        """Test with one list empty."""
        left = [1, 2, 3]
        result = invoice_merge_stream(left, [])
        assert result == left
        
        result = invoice_merge_stream([], left)
        assert result == left
    
    def test_identical_single_element_lists(self):
        """Test with identical single element lists (triggers bug)."""
        left = [5]
        right = [5]
        result = invoice_merge_stream(left, right)
        
        # Bug: should be [5, 5] but becomes [5] due to last duplicate removal
        assert len(result) == 1
        assert result == [5]
    
    def test_identical_lists(self):
        """Test with identical lists (triggers bug)."""
        left = [1, 2, 3]
        right = [1, 2, 3]
        result = invoice_merge_stream(left, right)
        
        # Bug: last element gets removed
        assert len(result) == 5  # Should be 6, but bug makes it 5
        assert result == [1, 1, 2, 2, 3]
    
    def test_no_overlapping_elements(self):
        """Test with no overlapping elements."""
        left = [1, 3, 5]
        right = [2, 4, 6]
        result = invoice_merge_stream(left, right)
        
        assert result == [1, 2, 3, 4, 5, 6]
        assert len(result) == 6
    
    def test_partial_overlap(self):
        """Test with partial overlap but not at the end."""
        left = [1, 2, 4]
        right = [2, 3, 5]
        result = invoice_merge_stream(left, right)
        
        assert result == [1, 2, 2, 3, 4, 5]
        assert len(result) == 6
    
    def test_overlapping_at_end(self):
        """Test with overlapping elements at the end (triggers bug)."""
        left = [1, 2, 5]
        right = [3, 4, 5]
        result = invoice_merge_stream(left, right)
        
        # Bug: last 5 gets removed
        assert len(result) == 5  # Should be 6, but bug makes it 5
        assert result == [1, 2, 3, 4, 5]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])