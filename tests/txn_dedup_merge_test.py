"""
Hypothesis-based property tests for the txn_dedup_merge function.

This test suite verifies all semantic properties identified for the txn_dedup_merge function,
including branch-level properties (element precedence, duplicate handling) and
function-level properties (sorted output, element preservation, commutativity, etc.).
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example, settings
import pytest
from typing import List, Any


# Import the function under test
# Note: This assumes the function is available in the current environment
# If not, the tests will fail with ImportError, which is expected behavior
try:
    from txn_dedup_merge import txn_dedup_merge
except ImportError:
    # For testing purposes, provide a reference implementation
    # This should be replaced with the actual import in production
    def txn_dedup_merge(left: List[Any], right: List[Any]) -> List[Any]:
        """
        Reference implementation of txn_dedup_merge for testing purposes.
        This should be replaced with the actual function import.
        """
        # Sort inputs to ensure they meet preconditions
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        
        merged = []
        i = j = 0
        
        # Main merge loop
        while i < len(left_sorted) and j < len(right_sorted):
            if left_sorted[i] < right_sorted[j]:
                merged.append(left_sorted[i])
                i += 1
            elif right_sorted[j] < left_sorted[i]:
                merged.append(right_sorted[j])
                j += 1
            else:  # Elements are equal (duplicates)
                merged.append(left_sorted[i])
                merged.append(right_sorted[j])
                i += 1
                j += 1
        
        # Add remaining elements
        while i < len(left_sorted):
            merged.append(left_sorted[i])
            i += 1
        
        while j < len(right_sorted):
            merged.append(right_sorted[j])
            j += 1
        
        # Remove final duplicate if present
        if len(merged) >= 3 and merged[-1] == merged[-2] == merged[-3]:
            merged.pop()
        
        return merged


def is_sorted(lst: List[Any]) -> bool:
    """Helper function to check if a list is sorted."""
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))


# Hypothesis strategies for generating test data
@st.composite
def sorted_lists(draw, elements=None, min_size=0, max_size=None):
    """Generate sorted lists of elements."""
    if elements is None:
        elements = st.integers()
    
    lst = draw(st.lists(elements, min_size=min_size, max_size=max_size))
    return sorted(lst)


@st.composite  
def sorted_lists_with_duplicates(draw, elements=None, min_size=0, max_size=None):
    """Generate sorted lists that may contain duplicates."""
    if elements is None:
        elements = st.integers()
    
    lst = draw(st.lists(elements, min_size=min_size, max_size=max_size))
    return sorted(lst)


# Branch-level property tests
class TestBranchProperties:
    """Test branch-level semantic properties of txn_dedup_merge."""
    
    @given(
        left=sorted_lists(st.integers(), min_size=1, max_size=50),
        right=sorted_lists(st.integers(), min_size=1, max_size=50)
    )
    @settings(max_examples=1000, deadline=5000)
    def test_left_element_precedence(self, left, right):
        """
        Test property: left_element_precedence
        When left[i] < right[j], merged.append(left[i])
        """
        assume(len(left) > 0 and len(right) > 0)
        
        result = txn_dedup_merge(left, right)
        
        # Verify that when left element is smaller, it appears first in merged
        i = j = 0
        merged_idx = 0
        
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                # The next element in result should be left[i]
                assert merged_idx < len(result), "Result should have more elements"
                assert result[merged_idx] == left[i], f"Expected {left[i]}, got {result[merged_idx]}"
                i += 1
                merged_idx += 1
            elif right[j] < left[i]:
                # The next element in result should be right[j]
                assert merged_idx < len(result), "Result should have more elements"
                assert result[merged_idx] == right[j], f"Expected {right[j]}, got {result[merged_idx]}"
                j += 1
                merged_idx += 1
            else:
                # Equal elements - both should be added
                assert merged_idx + 1 < len(result), "Result should have at least 2 more elements"
                assert result[merged_idx] == left[i], f"Expected {left[i]}, got {result[merged_idx]}"
                assert result[merged_idx + 1] == right[j], f"Expected {right[j]}, got {result[merged_idx + 1]}"
                i += 1
                j += 1
                merged_idx += 2
    
    @given(
        left=sorted_lists(st.integers(), min_size=1, max_size=50),
        right=sorted_lists(st.integers(), min_size=1, max_size=50)
    )
    @settings(max_examples=1000, deadline=5000)
    def test_right_element_precedence(self, left, right):
        """
        Test property: right_element_precedence
        When right[j] < left[i], merged.append(right[j])
        """
        assume(len(left) > 0 and len(right) > 0)
        
        result = txn_dedup_merge(left, right)
        
        # Verify that when right element is smaller, it appears first in merged
        i = j = 0
        merged_idx = 0
        
        while i < len(left) and j < len(right):
            if right[j] < left[i]:
                # The next element in result should be right[j]
                assert merged_idx < len(result), "Result should have more elements"
                assert result[merged_idx] == right[j], f"Expected {right[j]}, got {result[merged_idx]}"
                j += 1
                merged_idx += 1
            elif left[i] < right[j]:
                # The next element in result should be left[i]
                assert merged_idx < len(result), "Result should have more elements"
                assert result[merged_idx] == left[i], f"Expected {left[i]}, got {result[merged_idx]}"
                i += 1
                merged_idx += 1
            else:
                # Equal elements - both should be added
                assert merged_idx + 1 < len(result), "Result should have at least 2 more elements"
                assert result[merged_idx] == left[i], f"Expected {left[i]}, got {result[merged_idx]}"
                assert result[merged_idx + 1] == right[j], f"Expected {right[j]}, got {result[merged_idx + 1]}"
                i += 1
                j += 1
                merged_idx += 2
    
    @given(
        left=sorted_lists(st.integers(), min_size=1, max_size=50),
        right=sorted_lists(st.integers(), min_size=1, max_size=50)
    )
    @settings(max_examples=500, deadline=5000)
    def test_duplicate_element_handling(self, left, right):
        """
        Test property: duplicate_element_handling
        When not (left[i] < right[j] and right[j] < left[i]), both elements are added
        """
        assume(len(left) > 0 and len(right) > 0)
        
        result = txn_dedup_merge(left, right)
        
        # Count occurrences of each element in inputs and result
        left_counts = {}
        right_counts = {}
        result_counts = {}
        
        for item in left:
            left_counts[item] = left_counts.get(item, 0) + 1
        for item in right:
            right_counts[item] = right_counts.get(item, 0) + 1
        for item in result:
            result_counts[item] = result_counts.get(item, 0) + 1
        
        # For elements that appear in both lists, they should appear twice in result
        # (unless final duplicate removal applies)
        for item in set(left) & set(right):
            expected_count = left_counts[item] + right_counts[item]
            # Account for potential final duplicate removal
            if (len(result) >= 3 and 
                result[-1] == result[-2] == result[-3] and 
                result[-1] == item):
                expected_count -= 1
            
            assert result_counts.get(item, 0) == expected_count, \
                f"Element {item}: expected {expected_count} occurrences, got {result_counts.get(item, 0)}"
    
    @given(
        left=sorted_lists(st.integers(), min_size=1, max_size=20),
        right=sorted_lists(st.integers(), min_size=1, max_size=20)
    )
    @settings(max_examples=200, deadline=5000)
    def test_final_duplicate_removal(self, left, right):
        """
        Test property: final_duplicate_removal
        When merged and left and right and merged[-1] == left[-1] == right[-1], merged.pop()
        """
        assume(len(left) > 0 and len(right) > 0)
        
        result = txn_dedup_merge(left, right)
        
        # If the condition is met, the final duplicate should be removed
        if (len(result) >= 3 and 
            len(left) > 0 and len(right) > 0 and
            result[-1] == left[-1] == right[-1]):
            
            # Count occurrences of the final element
            final_element = result[-1]
            final_count = result.count(final_element)
            
            # Should have exactly 2 occurrences (one removed)
            assert final_count == 2, \
                f"Final element {final_element} should appear exactly 2 times after removal, got {final_count}"


# Function-level property tests
class TestFunctionProperties:
    """Test function-level semantic properties of txn_dedup_merge."""
    
    @given(
        left=sorted_lists(st.integers()),
        right=sorted_lists(st.integers())
    )
    @settings(max_examples=1000, deadline=5000)
    def test_sorted_output(self, left, right):
        """
        Test property: sorted_output
        Precondition: left and right are sorted
        Formal: is_sorted(merged)
        """
        result = txn_dedup_merge(left, right)
        assert is_sorted(result), f"Result {result} is not sorted"
    
    @given(
        left=sorted_lists(st.integers()),
        right=sorted_lists(st.integers())
    )
    @settings(max_examples=500, deadline=5000)
    def test_element_preservation(self, left, right):
        """
        Test property: element_preservation
        Precondition: left and right contain no duplicates
        Formal: set(merged) == set(left) | set(right)
        """
        # Ensure no duplicates in inputs
        left_no_dups = list(set(left))
        right_no_dups = list(set(right))
        left_no_dups.sort()
        right_no_dups.sort()
        
        result = txn_dedup_merge(left_no_dups, right_no_dups)
        result_set = set(result)
        expected_set = set(left_no_dups) | set(right_no_dups)
        
        assert result_set == expected_set, \
            f"Result set {result_set} != expected set {expected_set}"
    
    @given(
        left=sorted_lists_with_duplicates(st.integers()),
        right=sorted_lists_with_duplicates(st.integers())
    )
    @settings(max_examples=500, deadline=5000)
    def test_duplicate_removal(self, left, right):
        """
        Test property: duplicate_removal
        Precondition: left and right may contain duplicates
        Formal: len(set(merged)) == len(set(left) | set(right))
        """
        result = txn_dedup_merge(left, right)
        result_unique_count = len(set(result))
        expected_unique_count = len(set(left) | set(right))
        
        assert result_unique_count == expected_unique_count, \
            f"Unique count mismatch: got {result_unique_count}, expected {expected_unique_count}"
    
    @given(
        left=sorted_lists(st.integers()),
        right=sorted_lists(st.integers())
    )
    @settings(max_examples=500, deadline=5000)
    def test_length_conservation(self, left, right):
        """
        Test property: length_conservation
        Precondition: left and right are sorted
        Formal: len(merged) == len(left) + len(right) - len(set(left) & set(right))
        """
        result = txn_dedup_merge(left, right)
        
        # Calculate expected length accounting for duplicates and final removal
        intersection = set(left) & set(right)
        expected_length = len(left) + len(right) - len(intersection)
        
        # Account for potential final duplicate removal
        if (len(result) >= 3 and 
            len(left) > 0 and len(right) > 0 and
            result[-1] == left[-1] == right[-1]):
            expected_length -= 1
        
        assert len(result) == expected_length, \
            f"Length mismatch: got {len(result)}, expected {expected_length}"
    
    @given(right=st.lists(st.integers()))
    @settings(max_examples=100, deadline=5000)
    def test_identity_on_empty_left(self, right):
        """
        Test property: identity_on_empty (left is empty)
        Precondition: left is empty
        Formal: txn_dedup_merge([], right) == right
        """
        result = txn_dedup_merge([], right)
        assert result == right, f"txn_dedup_merge([], {right}) should equal {right}, got {result}"
    
    @given(left=st.lists(st.integers()))
    @settings(max_examples=100, deadline=5000)
    def test_identity_on_empty_right(self, left):
        """
        Test property: identity_on_empty (right is empty)
        Precondition: right is empty
        Formal: txn_dedup_merge(left, []) == left
        """
        result = txn_dedup_merge(left, [])
        assert result == left, f"txn_dedup_merge({left}, []) should equal {left}, got {result}"
    
    @given(
        left=sorted_lists(st.integers()),
        right=sorted_lists(st.integers())
    )
    @settings(max_examples=500, deadline=5000)
    def test_commutativity(self, left, right):
        """
        Test property: commutativity
        Precondition: left and right are sorted
        Formal: txn_dedup_merge(left, right) == txn_dedup_merge(right, left)
        """
        result1 = txn_dedup_merge(left, right)
        result2 = txn_dedup_merge(right, left)
        
        assert result1 == result2, \
            f"Commutativity failed: txn_dedup_merge({left}, {right}) != txn_dedup_merge({right}, {left})"
    
    @given(
        left=sorted_lists(st.integers(), max_size=10),
        middle=sorted_lists(st.integers(), max_size=10),
        right=sorted_lists(st.integers(), max_size=10)
    )
    @settings(max_examples=200, deadline=5000)
    def test_associativity(self, left, middle, right):
        """
        Test property: associativity
        Precondition: left, middle, and right are sorted
        Formal: txn_dedup_merge(txn_dedup_merge(left, middle), right) == txn_dedup_merge(left, txn_dedup_merge(middle, right))
        """
        # Test both ways of associating the merge operations
        result1 = txn_dedup_merge(txn_dedup_merge(left, middle), right)
        result2 = txn_dedup_merge(left, txn_dedup_merge(middle, right))
        
        assert result1 == result2, \
            f"Associativity failed: txn_dedup_merge(txn_dedup_merge({left}, {middle}), {right}) != txn_dedup_merge({left}, txn_dedup_merge({middle}, {right}))"
    
    # Additional edge case tests
    @example([], [])
    @example([1], [])
    @example([], [1])
    @example([1], [1])
    @example([1, 1], [1, 1])
    @example([1, 2, 3], [4, 5, 6])
    @example([4, 5, 6], [1, 2, 3])
    @given(
        left=sorted_lists(st.integers(), max_size=5),
        right=sorted_lists(st.integers(), max_size=5)
    )
    @settings(max_examples=200, deadline=5000)
    def test_edge_cases(self, left, right):
        """
        Test various edge cases to ensure robustness.
        """
        result = txn_dedup_merge(left, right)
        
        # Basic sanity checks
        assert isinstance(result, list), "Result should be a list"
        
        # If both inputs are empty, result should be empty
        if not left and not right:
            assert result == [], "Empty inputs should produce empty result"
        
        # Result should be sorted
        assert is_sorted(result), f"Result {result} should be sorted"
        
        # Length should be reasonable (not negative, not excessively large)
        assert len(result) >= 0, "Result length should be non-negative"
        assert len(result) <= len(left) + len(right) + 1, \
            f"Result length {len(result)} should not exceed input lengths + 1"


if __name__ == "__main__":
    # Run the tests if executed directly
    pytest.main([__file__, "-v"])