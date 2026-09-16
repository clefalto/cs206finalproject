import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import lists, floats, integers, one_of
from normalize import normalize


class TestBranchLevelProperties:
    """Test branch-level properties that hold under specific conditions."""
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_identity_on_empty(self, xs):
        """Branch-level property: when len(xs) == 0, normalize(xs) == xs"""
        if len(xs) == 0:
            result = normalize(xs)
            assert result == xs, f"Empty list should return itself: {result} != {xs}"
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_unit_sum_non_empty(self, xs):
        """Branch-level property: when len(xs) != 0, sum(normalize(xs)) == 1"""
        if len(xs) != 0:
            result = normalize(xs)
            # Check that sum is approximately 1 (accounting for floating point precision)
            assert abs(sum(result) - 1.0) < 1e-10, f"Sum should be 1, got {sum(result)}"
    
    @given(st.lists(st.floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1))
    def test_non_negative_outputs(self, xs):
        """Branch-level property: when len(xs) != 0 and all(x >= 0 for x in xs), all outputs >= 0"""
        if len(xs) != 0 and all(x >= 0 for x in xs):
            result = normalize(xs)
            assert all(x >= 0 for x in result), f"All outputs should be non-negative: {result}"


class TestFunctionLevelProperties:
    """Test function-level properties that hold for all executions."""
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_unit_sum_property(self, xs):
        """Function-level property: sum(normalize(xs)) == 1 when sum(xs) != 0"""
        if sum(xs) != 0:
            result = normalize(xs)
            assert abs(sum(result) - 1.0) < 1e-10, f"Sum should be 1, got {sum(result)}"
    
    @given(st.lists(st.floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1))
    def test_non_negative_outputs_property(self, xs):
        """Function-level property: all outputs are non-negative when all inputs are non-negative"""
        if all(x >= 0 for x in xs):
            result = normalize(xs)
            assert all(x >= 0 for x in result), f"All outputs should be non-negative: {result}"
    
    @given(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
        st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_scale_invariance_property(self, xs, c):
        """Function-level property: normalize([c * x for x in xs]) == normalize(xs)"""
        if sum(xs) != 0:
            result1 = normalize(xs)
            scaled_xs = [c * x for x in xs]
            result2 = normalize(scaled_xs)
            
            # Compare element-wise with tolerance for floating point precision
            assert len(result1) == len(result2), "Results should have same length"
            for r1, r2 in zip(result1, result2):
                assert abs(r1 - r2) < 1e-10, f"Scale invariance failed: {r1} != {r2}"
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_identity_on_empty_property(self, xs):
        """Function-level property: normalize(xs) == xs when len(xs) == 0"""
        if len(xs) == 0:
            result = normalize(xs)
            assert result == xs, f"Empty list should return itself: {result} != {xs}"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_no_nan_outputs(self, xs):
        """Ensure no NaN values in output when inputs are valid"""
        if sum(xs) != 0:
            result = normalize(xs)
            assert not any(x != x for x in result), f"No NaN values should be present: {result}"
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
    def test_no_infinity_outputs(self, xs):
        """Ensure no infinity values in output when inputs are valid"""
        if sum(xs) != 0:
            result = normalize(xs)
            assert not any(abs(x) == float('inf') for x in result), f"No infinity values should be present: {result}"
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    def test_empty_list_handling(self, xs):
        """Test that empty lists are handled correctly"""
        if len(xs) == 0:
            result = normalize(xs)
            assert result == [], f"Empty list should return empty list: {result}"
            assert isinstance(result, list), f"Result should be a list: {type(result)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])