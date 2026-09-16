"""
Hypothesis tests for the login_tally function semantic properties.
Tests all 8 semantic properties identified in properties/login_tally_properties.json.
"""

import pytest
from hypothesis import given, assume, strategies as st
from dataset.python_programs.login_tally import login_tally


class TestLoginTallyProperties:
    """Test class for login_tally semantic properties."""

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_cap_applied_branch_property(self, counters, key, cap):
        """
        Branch property: if cap is not None then updated <= cap
        """
        assume(key not in counters or counters[key] < (cap if cap is not None else float('inf')))
        
        result = login_tally(counters, key, cap=cap)
        
        if cap is not None:
            assert result <= cap, f"Result {result} should be <= cap {cap}"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=0)
    )
    def test_cap_enforced_branch_property(self, counters, key, cap):
        """
        Branch property: if updated > cap then updated == cap
        """
        # Set up initial state where current + 1 > cap
        current = cap  # This ensures current + 1 > cap
        counters[key] = current
        
        result = login_tally(counters, key, cap=cap)
        
        # Since current + 1 > cap, result should equal cap
        assert result == cap, f"Result {result} should equal cap {cap} when updated > cap"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_increment_by_one_function_property(self, counters, key, cap):
        """
        Function property: updated == current + 1
        """
        current = counters.get(key, 0)
        
        result = login_tally(counters, key, cap=cap)
        
        assert result == current + 1, f"Result {result} should equal current {current} + 1"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_counter_updated_function_property(self, counters, key, cap):
        """
        Function property: counters[key] == updated
        """
        result = login_tally(counters, key, cap=cap)
        
        assert counters[key] == result, f"counters[{key}] should equal result {result}"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_non_negative_result_function_property(self, counters, key, cap):
        """
        Function property: updated >= 0
        """
        result = login_tally(counters, key, cap=cap)
        
        assert result >= 0, f"Result {result} should be >= 0"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_monotonic_increase_function_property(self, counters, key, cap):
        """
        Function property: updated >= current
        """
        current = counters.get(key, 0)
        
        result = login_tally(counters, key, cap=cap)
        
        assert result >= current, f"Result {result} should be >= current {current}"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.integers(min_value=0)
    )
    def test_cap_respected_function_property(self, counters, key, cap):
        """
        Function property: updated <= cap (when cap is not None)
        """
        result = login_tally(counters, key, cap=cap)
        
        assert result <= cap, f"Result {result} should be <= cap {cap}"

    @given(
        counters=st.dictionaries(st.text(min_size=1), st.integers(min_value=0)),
        key=st.text(min_size=1),
        cap=st.one_of(st.none(), st.integers(min_value=0))
    )
    def test_default_initialization_function_property(self, counters, key, cap):
        """
        Function property: current == 0 (when key not in counters)
        """
        assume(key not in counters)
        
        current = counters.get(key, 0)
        
        assert current == 0, f"Current value should be 0 when key {key} not in counters"
        
        # Also verify the function behavior
        result = login_tally(counters, key, cap=cap)
        assert result == 1, f"Result should be 1 when starting from 0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])