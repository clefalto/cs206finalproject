"""
Hypothesis tests for tensor_slice_pad function semantic properties.

This test suite exercises all semantic properties identified in 
properties/tensor_slice_pad_properties.json using the Hypothesis testing framework.
"""

import pytest
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import integers, lists, sampled_from

# Import the function under test
from dataset.python_programs.tensor_slice_pad import tensor_slice_pad


class TestTensorSlicePadProperties:
    """Test class for tensor_slice_pad semantic properties."""

    @given(
        values=lists(st.integers(), min_size=0, max_size=100),
        start=integers(min_value=-10, max_value=10),
        end=integers(min_value=-10, max_value=10)
    )
    @example(values=[], start=-1, end=0)
    @example(values=[], start=0, end=-1)
    @example(values=[1, 2, 3], start=5, end=3)
    def test_invalid_range_error(self, values, start, end):
        """
        Test property: invalid_range_error
        Condition: start < 0 or end < start
        Formal: raises ValueError("invalid range")
        """
        assume(start < 0 or end < start)
        
        with pytest.raises(ValueError, match="invalid range"):
            tensor_slice_pad(values, start, end)

    @given(
        values=lists(st.integers(), min_size=0, max_size=50),
        start=integers(min_value=0, max_value=20),
        end=integers(min_value=0, max_value=20),
        pad=st.integers(min_value=-100, max_value=100)
    )
    @example(values=[1, 2], start=1, end=4, pad=99)  # missing = 1, should pad 2 elements
    @example(values=[1, 2, 3], start=2, end=5, pad=42)  # missing = 0, should pad 1 element (BUG)
    def test_pads_with_extra_element(self, values, start, end, pad):
        """
        Test property: pads_with_extra_element
        Condition: missing >= 0
        Formal: result.extend([pad] * (missing + 1))
        """
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end, pad=pad)
        
        # Calculate expected missing elements
        expected_length = end - start
        actual_length = len(result)
        missing = expected_length - actual_length
        
        # This property tests the BUG: it pads one extra element when exactly aligned
        if missing >= 0:
            # The function should pad (missing + 1) elements due to the bug
            expected_padded_elements = missing + 1
            # Count how many pad elements are at the end
            pad_count = 0
            for i in range(len(result) - 1, -1, -1):
                if result[i] == pad:
                    pad_count += 1
                else:
                    break
            
            assert pad_count == expected_padded_elements, \
                f"Expected {expected_padded_elements} pad elements, got {pad_count}"

    @given(
        values=lists(st.integers(), min_size=0, max_size=100),
        start=integers(min_value=0, max_value=50),
        end=integers(min_value=0, max_value=50)
    )
    @example(values=[], start=0, end=0)
    @example(values=[1, 2, 3], start=1, end=2)
    @example(values=[10, 20, 30, 40], start=0, end=4)
    def test_returns_list(self, values, start, end):
        """
        Test property: returns_list
        Precondition: values is a list
        Formal: isinstance(result, list)
        """
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end)
        
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    @given(
        values=lists(st.integers(), min_size=0, max_size=100),
        start=integers(min_value=0, max_value=20),
        end=integers(min_value=0, max_value=20)
    )
    @example(values=[1, 2, 3, 4, 5], start=1, end=4)  # len(values) >= end
    @example(values=[1, 2], start=0, end=3)  # len(values) < end
    def test_length_is_end_minus_start(self, values, start, end):
        """
        Test property: length_is_end_minus_start
        Precondition: start >= 0 and end >= start and values has enough elements
        Formal: len(result) == end - start
        """
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end)
        
        expected_length = end - start
        assert len(result) == expected_length, \
            f"Expected length {expected_length}, got {len(result)}"

    @given(
        values=lists(st.integers(), min_size=0, max_size=100),
        start=integers(min_value=0, max_value=20),
        end=integers(min_value=0, max_value=20)
    )
    @example(values=[1, 2, 3, 4, 5], start=1, end=3)  # len(values) >= end
    @example(values=[10, 20, 30], start=0, end=3)  # len(values) == end
    def test_preserves_slice_when_no_padding(self, values, start, end):
        """
        Test property: preserves_slice_when_no_padding
        Precondition: start >= 0 and end >= start and len(values) >= end
        Formal: result == values[start:end]
        """
        assume(start >= 0 and end >= start and len(values) >= end)
        
        result = tensor_slice_pad(values, start, end)
        expected = values[start:end]
        
        assert result == expected, \
            f"Expected {expected}, got {result}"

    @given(
        values=lists(st.integers(), min_size=0, max_size=100),
        start=integers(min_value=0, max_value=20),
        end=integers(min_value=0, max_value=20)
    )
    @example(values=[], start=0, end=0)
    @example(values=[1, 2, 3], start=1, end=3)
    @example(values=[1, 2], start=0, end=5)
    def test_metamorphic_relation(self, values, start, end):
        """
        Test property: metamorphic_relation
        Precondition: start >= 0 and end >= start
        Formal: len(tensor_slice_pad(values, start, end)) == end - start
        """
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end)
        expected_length = end - start
        
        assert len(result) == expected_length, \
            f"Metamorphic relation failed: expected length {expected_length}, got {len(result)}"


class TestTensorSlicePadEdgeCases:
    """Additional edge case tests for tensor_slice_pad."""

    @given(
        values=lists(st.integers(), min_size=0, max_size=50),
        start=integers(min_value=0, max_value=20),
        end=integers(min_value=0, max_value=20),
        pad=st.integers()
    )
    def test_different_pad_values(self, values, start, end, pad):
        """Test that different pad values work correctly."""
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end, pad=pad)
        
        # Verify the result length is correct
        assert len(result) == end - start
        
        # If padding occurred, verify the pad value is correct
        if len(values) < end:
            # Check that the last elements are the pad value
            missing = (end - start) - len(values[start:])
            # Due to the bug, we expect (missing + 1) pad elements
            expected_pad_count = missing + 1
            actual_pad_count = sum(1 for x in result[-expected_pad_count:] if x == pad)
            assert actual_pad_count == expected_pad_count

    @given(
        values=lists(st.text(), min_size=0, max_size=20),
        start=integers(min_value=0, max_value=10),
        end=integers(min_value=0, max_value=10),
        pad=st.text()
    )
    def test_with_string_values(self, values, start, end, pad):
        """Test with string values and string pad."""
        assume(start >= 0 and end >= start)
        
        result = tensor_slice_pad(values, start, end, pad=pad)
        
        assert isinstance(result, list)
        assert len(result) == end - start

    def test_empty_list_cases(self):
        """Test specific cases with empty lists."""
        # Empty list with valid range should pad
        result = tensor_slice_pad([], 0, 3, pad=42)
        assert result == [42, 42, 42]  # Due to bug: missing=3, pads 4 elements, but we only need 3
        
        # Empty list with zero range
        result = tensor_slice_pad([], 0, 0, pad=99)
        assert result == []

    def test_exact_alignment_bug(self):
        """Test the specific bug case where padding occurs when not needed."""
        # When we have exactly enough elements, the function still pads one extra
        values = [1, 2, 3]
        result = tensor_slice_pad(values, 0, 3, pad=0)  # Should be [1, 2, 3] but will be [1, 2, 3, 0]
        
        # This test documents the bug: it should be [1, 2, 3] but is [1, 2, 3, 0]
        assert len(result) == 4  # Bug: should be 3
        assert result == [1, 2, 3, 0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])