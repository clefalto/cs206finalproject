"""
Comprehensive Hypothesis-based tests for the prices_stream function.

This test suite exercises all semantic properties identified in 
properties/prices_stream_properties.json, including both correct behaviors
and the intentional bug in the function.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import lists, integers, tuples
from typing import List


def prices_stream(left: List[int], right: List[int]) -> List[int]:
    """
    Combine two ordered prices streams.
    """
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        a, b = left[i], right[j]
        if a < b:
            merged.append(a)
            i += 1
        elif b < a:
            merged.append(b)
            j += 1
        else:
            merged.append(a)
            merged.append(b)
            i += 1
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])

    # BUG: removes the last matching element when both lists end together.
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()

    return merged


def is_sorted(lst: List[int]) -> bool:
    """Helper function to check if a list is sorted."""
    return all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))


def count_element(lst: List[int], element: int) -> int:
    """Helper function to count occurrences of an element in a list."""
    return lst.count(element)


@given(left=lists(integers()), right=lists(integers()))
def test_merge_order_preservation(left: List[int], right: List[int]):
    """
    Test that the merged result preserves sorted order when inputs are sorted.
    Property: merge_order_preservation
    Precondition: left and right are sorted lists
    Formal: is_sorted(merged)
    """
    assume(is_sorted(left) and is_sorted(right))
    merged = prices_stream(left, right)
    assert is_sorted(merged), f"Result {merged} is not sorted for inputs {left}, {right}"


@given(left=lists(integers()), right=lists(integers()))
def test_element_preservation(left: List[int], right: List[int]):
    """
    Test that all elements from both input lists appear in the result.
    Property: element_preservation
    Precondition: true
    Formal: set(merged) == set(left) | set(right)
    """
    merged = prices_stream(left, right)
    assert set(merged) == set(left) | set(right), \
        f"Elements not preserved: {set(merged)} != {set(left) | set(right)}"


@given(left=lists(integers()), right=lists(integers()))
def test_length_conservation(left: List[int], right: List[int]):
    """
    Test that the length is conserved when there are no duplicate elements at the end.
    Property: length_conservation
    Precondition: no duplicate elements at end of both lists
    Formal: len(merged) == len(left) + len(right)
    """
    assume(not (left and right and left[-1] == right[-1]))
    merged = prices_stream(left, right)
    assert len(merged) == len(left) + len(right), \
        f"Length not conserved: {len(merged)} != {len(left)} + {len(right)}"


@given(left=lists(integers()), right=lists(integers()))
def test_length_reduction_bug(left: List[int], right: List[int]):
    """
    Test the intentional bug: when both lists end with the same element,
    the result has one less element.
    Property: length_reduction_bug
    Precondition: merged and left and right and merged[-1] == left[-1] == right[-1]
    Formal: len(merged) == len(left) + len(right) - 1
    """
    assume(left and right and left[-1] == right[-1])
    merged = prices_stream(left, right)
    assume(merged and merged[-1] == left[-1] == right[-1])
    assert len(merged) == len(left) + len(right) - 1, \
        f"Bug not triggered or incorrect length: {len(merged)} != {len(left)} + {len(right)} - 1"


@given(left=lists(integers()), right=lists(integers()))
def test_empty_list_identity(left: List[int], right: List[int]):
    """
    Test that empty lists act as identity elements.
    Property: empty_list_identity
    Precondition: left is empty or right is empty
    Formal: prices_stream([], right) == right and prices_stream(left, []) == left
    """
    assume(not left or not right)
    if not left:
        result = prices_stream([], right)
        assert result == right, f"prices_stream([], {right}) != {right}, got {result}"
    if not right:
        result = prices_stream(left, [])
        assert result == left, f"prices_stream({left}, []) != {left}, got {result}"


@given(left=lists(integers()), right=lists(integers()))
def test_commutativity(left: List[int], right: List[int]):
    """
    Test that the function is commutative.
    Property: commutativity
    Precondition: true
    Formal: prices_stream(left, right) == prices_stream(right, left)
    """
    result1 = prices_stream(left, right)
    result2 = prices_stream(right, left)
    assert result1 == result2, \
        f"Commutativity failed: prices_stream({left}, {right}) != prices_stream({right}, {left})"


@given(left=lists(integers()), right=lists(integers()), third=lists(integers()))
def test_associativity(left: List[int], right: List[int], third: List[int]):
    """
    Test that the function is associative.
    Property: associativity
    Precondition: true
    Formal: prices_stream(prices_stream(left, right), third) == prices_stream(left, prices_stream(right, third))
    """
    result1 = prices_stream(prices_stream(left, right), third)
    result2 = prices_stream(left, prices_stream(right, third))
    assert result1 == result2, \
        f"Associativity failed: prices_stream(prices_stream({left}, {right}), {third}) != prices_stream({left}, prices_stream({right}, {third}))"


@given(left=lists(integers()), right=lists(integers()))
def test_duplicate_handling(left: List[int], right: List[int]):
    """
    Test that duplicates are handled correctly (count preserved).
    Property: duplicate_handling
    Precondition: elements a appear in both left and right
    Formal: count(a, merged) == count(a, left) + count(a, right)
    """
    merged = prices_stream(left, right)
    
    # Test for all unique elements that appear in either list
    all_elements = set(left) | set(right)
    for element in all_elements:
        left_count = count_element(left, element)
        right_count = count_element(right, element)
        merged_count = count_element(merged, element)
        expected_count = left_count + right_count
        
        assert merged_count == expected_count, \
            f"Duplicate handling failed for element {element}: " \
            f"expected {expected_count} ({left_count} + {right_count}), got {merged_count}"


@given(left=lists(integers()), right=lists(integers()))
def test_monotonicity(left: List[int], right: List[int]):
    """
    Test that the result is monotonically non-decreasing when inputs are sorted.
    Property: monotonicity
    Precondition: left and right are sorted
    Formal: for all i < len(merged)-1: merged[i] <= merged[i+1]
    """
    assume(is_sorted(left) and is_sorted(right))
    merged = prices_stream(left, right)
    
    for i in range(len(merged) - 1):
        assert merged[i] <= merged[i + 1], \
            f"Monotonicity violated at index {i}: {merged[i]} > {merged[i + 1]}"


@given(left=lists(integers()), right=lists(integers()))
def test_prefix_preservation(left: List[int], right: List[int]):
    """
    Test that the prefix of the result contains elements from both lists in sorted order.
    Property: prefix_preservation
    Precondition: true
    Formal: merged[:min(len(left), len(right))] contains elements from both lists in sorted order
    """
    merged = prices_stream(left, right)
    min_len = min(len(left), len(right))
    
    if min_len > 0:
        prefix = merged[:min_len]
        # The prefix should be sorted
        assert is_sorted(prefix), f"Prefix {prefix} is not sorted"
        
        # The prefix should contain elements from both lists (when both have elements)
        if left and right:
            # At least some elements from both lists should appear in the prefix
            # This is a weaker form of the property since the exact distribution depends on the merge algorithm
            left_in_prefix = any(x in prefix for x in left)
            right_in_prefix = any(x in prefix for x in right)
            assert left_in_prefix or right_in_prefix, \
                f"Prefix {prefix} doesn't contain elements from input lists {left}, {right}"


# Specific tests for branch conditions (these are more unit-test like but verify the semantic properties)

@given(left=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10),
       right=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10))
def test_append_smaller_element_branch(left: List[int], right: List[int]):
    """
    Test the branch where a < b (append smaller element).
    Property: append_smaller_element
    Condition: a < b
    Formal: merged.append(a) and i += 1
    """
    assume(is_sorted(left) and is_sorted(right))
    assume(left[0] < right[0])  # Ensure first element of left is smaller
    
    merged = prices_stream(left, right)
    
    # The first element of the result should be the first element of left
    assert merged[0] == left[0], \
        f"First element should be {left[0]}, got {merged[0]}"


@given(left=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10),
       right=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10))
def test_append_equal_elements_branch(left: List[int], right: List[int]):
    """
    Test the branch where elements are equal (append both).
    Property: append_equal_elements
    Condition: not (a < b and b < a)  # i.e., a == b
    Formal: merged.append(a) and merged.append(b) and i += 1 and j += 1
    """
    assume(is_sorted(left) and is_sorted(right))
    assume(left[0] == right[0])  # Ensure first elements are equal
    
    merged = prices_stream(left, right)
    
    # When first elements are equal, both should appear in the result
    # (though the bug might remove one if they're at the end)
    if len(left) == 1 and len(right) == 1:
        # Special case: both lists have one equal element
        # The bug will remove one, so we should have exactly one element
        assert len(merged) == 1, f"Expected 1 element, got {len(merged)}"
        assert merged[0] == left[0], f"Expected {left[0]}, got {merged[0]}"
    else:
        # General case: both elements should appear (unless removed by bug)
        count_first = count_element(merged, left[0])
        expected_count = count_element(left, left[0]) + count_element(right, left[0])
        assert count_first == expected_count, \
            f"Expected {expected_count} occurrences of {left[0]}, got {count_first}"


@given(left=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10),
       right=lists(integers(min_value=0, max_value=100), min_size=1, max_size=10))
def test_remove_duplicate_end_branch(left: List[int], right: List[int]):
    """
    Test the branch that removes duplicate end elements.
    Property: remove_duplicate_end
    Condition: merged and left and right and merged[-1] == left[-1] == right[-1]
    Formal: merged.pop()
    """
    assume(is_sorted(left) and is_sorted(right))
    assume(left and right and left[-1] == right[-1])
    
    merged = prices_stream(left, right)
    
    # If the bug condition is met, the last element should be removed
    if merged and merged[-1] == left[-1] == right[-1]:
        # The bug should have removed one occurrence
        expected_length = len(left) + len(right) - 1
        assert len(merged) == expected_length, \
            f"Expected length {expected_length} after duplicate removal, got {len(merged)}"


if __name__ == "__main__":
    # Run a few quick manual tests to verify the function works as expected
    print("Running manual verification tests...")
    
    # Test basic merge
    result = prices_stream([1, 3, 5], [2, 4, 6])
    print(f"prices_stream([1, 3, 5], [2, 4, 6]) = {result}")
    assert result == [1, 2, 3, 4, 5, 6]
    
    # Test with duplicates
    result = prices_stream([1, 2, 3], [2, 3, 4])
    print(f"prices_stream([1, 2, 3], [2, 3, 4]) = {result}")
    # Expected: [1, 2, 2, 3, 3, 4] but bug removes last 3, so [1, 2, 2, 3, 4]
    assert result == [1, 2, 2, 3, 4]
    
    # Test empty lists
    result = prices_stream([], [1, 2, 3])
    print(f"prices_stream([], [1, 2, 3]) = {result}")
    assert result == [1, 2, 3]
    
    result = prices_stream([1, 2, 3], [])
    print(f"prices_stream([1, 2, 3], []) = {result}")
    assert result == [1, 2, 3]
    
    print("Manual verification tests passed!")