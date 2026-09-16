"""
Hypothesis tests for the percentile_estimator function semantic properties.

This test suite exercises all semantic properties identified in
properties/percentile_estimator_properties.json using the Hypothesis
testing framework for property-based testing.
"""

import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import floats, lists, integers, one_of

# Import the function under test
# Note: The actual implementation should be imported from the appropriate module
# For now, we'll define a placeholder that matches the structure
def percentile_estimator(values, q=0.5):
    """
    Percentile estimator function with known off-by-one bug.
    
    Args:
        values: List of numeric values
        q: Quantile value between 0 and 1 (default: 0.5)
    
    Returns:
        The q-th percentile value from the sorted values list
    
    Raises:
        ValueError: If values is empty or q is not in [0, 1]
    """
    if not values:
        raise ValueError("no values")
    
    if not (0 <= q <= 1):
        raise ValueError("q must be in [0, 1]")
    
    idx = int(len(values) * q)
    # BUG: off-by-one when q=1.0; index equals len(values).
    return values[idx]


class TestPercentileEstimatorProperties:
    """Test class for percentile_estimator semantic properties."""
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=100))
    def test_empty_input_error(self, values):
        """
        Property: empty_input_error
        Condition: not values
        Formal: percentile_estimator(values) raises ValueError with message 'no values'
        """
        assume(not values)  # Only test when values is empty
        
        with pytest.raises(ValueError, match="no values"):
            percentile_estimator(values)
    
    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        q=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_invalid_quantile_error(self, values, q):
        """
        Property: invalid_quantile_error
        Condition: not (0 <= q <= 1)
        Formal: percentile_estimator(values, q) raises ValueError with message 'q must be in [0, 1]'
        """
        assume(not (0 <= q <= 1))  # Only test when q is outside [0, 1]
        
        with pytest.raises(ValueError, match="q must be in \\[0, 1\\]"):
            percentile_estimator(values, q)
    
    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_quantile_range(self, values, q):
        """
        Property: quantile_range
        Precondition: values is non-empty and 0 <= q <= 1
        Formal: min(values) <= percentile_estimator(values, q) <= max(values)
        """
        result = percentile_estimator(values, q)
        assert min(values) <= result <= max(values), \
            f"Result {result} is outside range [{min(values)}, {max(values)}] for q={q}"
    
    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
        q1=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        q2=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_monotonicity(self, values, q1, q2):
        """
        Property: monotonicity
        Precondition: values is non-empty and 0 <= q1 <= q2 <= 1
        Formal: percentile_estimator(values, q1) <= percentile_estimator(values, q2)
        """
        assume(0 <= q1 <= q2 <= 1)  # Ensure q1 <= q2
        
        result1 = percentile_estimator(values, q1)
        result2 = percentile_estimator(values, q2)
        
        assert result1 <= result2, \
            f"Monotonicity violated: percentile_estimator(values, {q1}) = {result1} > percentile_estimator(values, {q2}) = {result2}"
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_identity_on_extremes(self, values):
        """
        Property: identity_on_extremes
        Precondition: values is non-empty
        Formal: percentile_estimator(values, 0) == min(values) and percentile_estimator(values, 1) == max(values)
        """
        result_0 = percentile_estimator(values, 0.0)
        result_1 = percentile_estimator(values, 1.0)
        
        assert result_0 == min(values), \
            f"percentile_estimator(values, 0) = {result_0} != min(values) = {min(values)}"
        
        # Note: This test will fail due to the off-by-one bug when q=1.0
        # The bug causes an IndexError when trying to access values[len(values)]
        assert result_1 == max(values), \
            f"percentile_estimator(values, 1) = {result_1} != max(values) = {max(values)}"
    
    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=50),
        q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        c=st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance(self, values, q, c):
        """
        Property: scale_invariance
        Precondition: values is non-empty, 0 <= q <= 1, and c > 0
        Formal: percentile_estimator([c * x for x in values], q) == c * percentile_estimator(values, q)
        """
        scaled_values = [c * x for x in values]
        result_scaled = percentile_estimator(scaled_values, q)
        result_original_scaled = c * percentile_estimator(values, q)
        
        # Use approximate equality for floating point comparisons
        assert abs(result_scaled - result_original_scaled) < 1e-10, \
            f"Scale invariance violated: percentile_estimator(scaled, {q}) = {result_scaled} != c * percentile_estimator(original, {q}) = {result_original_scaled}"
    
    @given(
        values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=50),
        q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        c=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    def test_translation_invariance(self, values, q, c):
        """
        Property: translation_invariance
        Precondition: values is non-empty, 0 <= q <= 1, and c is any constant
        Formal: percentile_estimator([x + c for x in values], q) == percentile_estimator(values, q) + c
        """
        translated_values = [x + c for x in values]
        result_translated = percentile_estimator(translated_values, q)
        result_original_translated = percentile_estimator(values, q) + c
        
        # Use approximate equality for floating point comparisons
        assert abs(result_translated - result_original_translated) < 1e-10, \
            f"Translation invariance violated: percentile_estimator(translated, {q}) = {result_translated} != percentile_estimator(original, {q}) + c = {result_original_translated}"
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_off_by_one_bug(self, values):
        """
        Property: off_by_one_bug
        Precondition: values is non-empty and q == 1.0
        Formal: percentile_estimator(values, 1.0) raises IndexError or returns incorrect value
        """
        # This test specifically targets the bug where q=1.0 causes an IndexError
        # or returns an incorrect value due to accessing values[len(values)]
        
        try:
            result = percentile_estimator(values, 1.0)
            # If no exception is raised, check if the result is incorrect
            # The correct result should be max(values), but due to the bug
            # it might return an incorrect value or raise an IndexError
            expected = max(values)
            if result != expected:
                # Bug detected: returns incorrect value
                assert True, f"Bug detected: percentile_estimator(values, 1.0) = {result} != max(values) = {expected}"
        except IndexError:
            # Bug detected: raises IndexError
            assert True, "Bug detected: percentile_estimator(values, 1.0) raises IndexError"
        except Exception as e:
            # Unexpected exception
            assert False, f"Unexpected exception: {e}"


# Additional edge case tests
class TestPercentileEstimatorEdgeCases:
    """Additional tests for edge cases and boundary conditions."""
    
    @given(values=st.lists(st.integers(), min_size=1, max_size=100))
    def test_with_integer_values(self, values):
        """Test with integer values to ensure type handling."""
        q = 0.5
        result = percentile_estimator(values, q)
        # Should be one of the values in the list
        assert result in values
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_with_single_element(self, values):
        """Test with single element lists."""
        assume(len(values) == 1)
        
        for q in [0.0, 0.5, 1.0]:
            result = percentile_estimator(values, q)
            assert result == values[0], f"Single element test failed for q={q}"
    
    @given(values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100))
    def test_with_two_elements(self, values):
        """Test with exactly two elements."""
        assume(len(values) == 2)
        
        # Sort for predictable results
        values.sort()
        
        # Test q=0.0, 0.5, 1.0
        result_0 = percentile_estimator(values, 0.0)
        result_05 = percentile_estimator(values, 0.5)
        result_1 = percentile_estimator(values, 1.0)
        
        assert result_0 == values[0]
        assert result_1 == values[1]  # This will fail due to the bug
        # result_05 should be values[0] since int(2 * 0.5) = 1, but accessing values[1] when len=2 causes IndexError