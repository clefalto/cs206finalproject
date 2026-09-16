"""
Hypothesis-based tests for upload_gate function semantic properties.
Tests all 9 semantic properties identified in properties/upload_gate_properties.json.
"""

import hypothesis.strategies as st
from hypothesis import given, assume, example
import pytest
from dataset.python_programs.upload_gate import upload_gate


class TestUploadGateProperties:
    """Test class for upload_gate semantic properties using Hypothesis."""

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_reject_on_limit_exceeded(self, timestamps, now, window, limit):
        """
        Branch property: When len(active) > limit, should reject with (False, 0).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is met
        assume(len(active) > limit)
        
        result = upload_gate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} > limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_accept_with_remaining_capacity(self, timestamps, now, window, limit):
        """
        Branch property: When not (len(active) > limit), should accept with remaining capacity.
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the condition is NOT met (i.e., len(active) <= limit)
        assume(not (len(active) > limit))
        
        result = upload_gate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result == (True, expected_capacity), f"Expected (True, {expected_capacity}) when len(active)={len(active)} <= limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_boolean_result(self, timestamps, now, window, limit):
        """
        Function property: First element of result should always be boolean.
        """
        result = upload_gate(timestamps, now, window=window, limit=limit)
        assert isinstance(result[0], bool), f"Expected boolean result, got {type(result[0])} in {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_non_negative_capacity(self, timestamps, now, window, limit):
        """
        Function property: Second element (capacity) should always be non-negative.
        """
        result = upload_gate(timestamps, now, window=window, limit=limit)
        capacity = result[1]
        assert capacity >= 0, f"Expected non-negative capacity, got {capacity} in {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_capacity_bound(self, timestamps, now, window, limit):
        """
        Function property: Capacity should never exceed the limit.
        """
        result = upload_gate(timestamps, now, window=window, limit=limit)
        capacity = result[1]
        assert capacity <= limit, f"Expected capacity <= limit ({limit}), got {capacity} in {result}"

    @given(
        timestamps1=st.lists(st.integers(min_value=0, max_value=1000)),
        timestamps2=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_capacity_monotonicity(self, timestamps1, timestamps2, now, window, limit):
        """
        Function property: If len(active1) <= len(active2), then capacity1 >= capacity2.
        """
        cutoff = now - window
        active1 = [t for t in timestamps1 if t >= cutoff]
        active2 = [t for t in timestamps2 if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active1) <= len(active2))
        
        result1 = upload_gate(timestamps1, now, window=window, limit=limit)
        result2 = upload_gate(timestamps2, now, window=window, limit=limit)
        
        capacity1 = result1[1]
        capacity2 = result2[1]
        
        assert capacity1 >= capacity2, f"Expected capacity1 ({capacity1}) >= capacity2 ({capacity2}) when len(active1)={len(active1)} <= len(active2)={len(active2)}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_reject_when_full(self, timestamps, now, window, limit):
        """
        Function property: When len(active) >= limit, should reject with (False, 0).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) >= limit)
        
        result = upload_gate(timestamps, now, window=window, limit=limit)
        assert result == (False, 0), f"Expected (False, 0) when len(active)={len(active)} >= limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_accept_when_not_full(self, timestamps, now, window, limit):
        """
        Function property: When len(active) < limit, should accept (first element True).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) < limit)
        
        result = upload_gate(timestamps, now, window=window, limit=limit)
        assert result[0] == True, f"Expected True when len(active)={len(active)} < limit={limit}, got {result}"

    @given(
        timestamps=st.lists(st.integers(min_value=0, max_value=1000)),
        now=st.integers(min_value=0, max_value=1000),
        window=st.just(10),
        limit=st.just(5)
    )
    def test_capacity_calculation(self, timestamps, now, window, limit):
        """
        Function property: When len(active) < limit, capacity should equal limit - len(active).
        """
        cutoff = now - window
        active = [t for t in timestamps if t >= cutoff]
        
        # Only test when the precondition is met
        assume(len(active) < limit)
        
        result = upload_gate(timestamps, now, window=window, limit=limit)
        expected_capacity = limit - len(active)
        assert result[1] == expected_capacity, f"Expected capacity {expected_capacity} when len(active)={len(active)} < limit={limit}, got {result[1]} in {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])